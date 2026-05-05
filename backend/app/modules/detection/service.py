from __future__ import annotations

import threading
import time
from datetime import UTC, datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import BackgroundTasks, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db_session, get_session_factory
from backend.app.modules.detection.analyzers.base import AnalyzerContext
from backend.app.modules.detection.analyzers.local_rule_based import LocalRuleBasedDamageAnalyzer
from backend.app.modules.detection.repository import DetectionBatchRepository
from backend.app.modules.detection.schemas import (
    CreateDetectionBatchPayload,
    CreateDetectionBatchRequest,
    DetectionAssetRecord,
    DetectionAssetPayload,
    DetectionBatchAggregate,
    DetectionBatchDetailPayload,
    DetectionBatchStatus,
    DetectionResultRecord,
    DetectionResultPayload,
    DetectionTaskRecord,
    DetectionTaskPayload,
    DetectionTaskStatus,
    ReviewDetectionResultRequest,
)


DISPLAY_TIMEZONE = ZoneInfo("Asia/Shanghai")


def _format_display_time(value: datetime) -> str:
    return value.astimezone(DISPLAY_TIMEZONE).strftime("%Y-%m-%d %H:%M")


def _start_detection_processing_thread(batch_id: str) -> None:
    thread = threading.Thread(
        target=_run_detection_processing,
        args=(batch_id,),
        name=f"detection-processing-{batch_id}",
        daemon=True,
    )
    thread.start()


def _run_detection_processing(batch_id: str) -> None:
    session_factory = get_session_factory()
    try:
        time.sleep(0.2)

        with session_factory() as session:
            DetectionBatchRepository(session).mark_batch_running(batch_id)

        time.sleep(0.15)

        with session_factory() as session:
            repository = DetectionBatchRepository(session)
            analyzer_payload = repository.get_batch_analyzer_assets(batch_id)
            if analyzer_payload is None:
                return
            assets, context_payload = analyzer_payload
            findings = LocalRuleBasedDamageAnalyzer().analyze(
                assets=assets,
                context=AnalyzerContext(**context_payload),
            )
            repository.mark_batch_completed(batch_id, findings=findings)
    except Exception as exc:  # pragma: no cover - defensive guard for the background thread.
        with session_factory() as session:
            DetectionBatchRepository(session).mark_batch_failed(
                batch_id=batch_id,
                error_message=f"图像识别任务执行失败：{exc}",
            )


class DetectionBatchService:
    def __init__(self, repository: DetectionBatchRepository) -> None:
        self._repository = repository
        self._repository.ensure_demo_data()

    def create_batch(
        self,
        payload: CreateDetectionBatchRequest,
        background_tasks: BackgroundTasks | None = None,
    ) -> CreateDetectionBatchPayload:
        aggregate = self._repository.create_batch(payload)
        if background_tasks is not None:
            background_tasks.add_task(_start_detection_processing_thread, aggregate.batch.batch_id)
        return CreateDetectionBatchPayload(
            batch_id=aggregate.batch.batch_id,
            status=aggregate.batch.status,
        )

    def get_batch(self, batch_id: str) -> DetectionBatchDetailPayload | None:
        aggregate = self._repository.get_batch(batch_id)
        if aggregate is None:
            return None
        return self._build_batch_detail_payload(aggregate)

    def list_batches(self, *, limit: int = 20, include_demo: bool = False) -> list[DetectionBatchDetailPayload]:
        return [
            self._build_batch_detail_payload(aggregate)
            for aggregate in self._repository.list_batches(limit=limit, include_demo=include_demo)
        ]

    def list_batch_results(self, batch_id: str) -> list[DetectionResultPayload] | None:
        results = self._repository.list_results_by_batch(batch_id)
        if results is None:
            return None
        return [self._build_result_payload(result) for result in results]

    def delete_batch(self, batch_id: str) -> bool:
        return self._repository.delete_batch(batch_id)

    def get_result(self, result_id: str) -> DetectionResultPayload | None:
        result = self._repository.get_result(result_id)
        if result is None:
            return None
        return self._build_result_payload(result)

    def review_result(self, result_id: str, payload: ReviewDetectionResultRequest) -> DetectionResultPayload | None:
        result = self._repository.update_result_review(
            result_id=result_id,
            review_status=payload.review_status,
            note=payload.note,
        )
        if result is None:
            return None
        return self._build_result_payload(result)

    def _build_batch_detail_payload(self, aggregate: DetectionBatchAggregate) -> DetectionBatchDetailPayload:
        status = aggregate.batch.status
        progress = self._calculate_progress(aggregate.tasks)
        hero_title, hero_description, upload_hint, upload_badge, queue_summary, asset_status = self._build_status_copy(
            batch_id=aggregate.batch.batch_id,
            status=status,
            result_count=len(aggregate.results),
            error_message=aggregate.batch.error_message,
        )

        return DetectionBatchDetailPayload(
            batch_id=aggregate.batch.batch_id,
            site_id=aggregate.batch.site_id,
            component_id=aggregate.batch.component_id,
            source=aggregate.batch.source,
            status=status,
            progress=progress,
            elapsed_seconds=self._calculate_elapsed_seconds(aggregate),
            error_message=aggregate.batch.error_message,
            captured_at=_format_display_time(aggregate.batch.captured_at),
            created_at=_format_display_time(aggregate.batch.created_at),
            hero_title=hero_title,
            hero_description=hero_description,
            upload_hint=upload_hint,
            upload_badge=upload_badge,
            queue_summary=queue_summary,
            asset=self._build_asset_payload(aggregate.asset, progress, asset_status),
            tasks=[self._build_task_payload(task) for task in aggregate.tasks],
            results=[self._build_result_payload(result) for result in aggregate.results],
        )

    @staticmethod
    def _calculate_progress(tasks: list[DetectionTaskRecord]) -> int:
        if not tasks:
            return 0
        return round(sum(task.progress for task in tasks) / len(tasks))

    @staticmethod
    def _calculate_elapsed_seconds(aggregate: DetectionBatchAggregate) -> int:
        end_time = aggregate.batch.completed_at or aggregate.batch.failed_at or datetime.now(UTC)
        created_at = aggregate.batch.created_at
        if created_at.tzinfo is None or created_at.utcoffset() is None:
            created_at = created_at.replace(tzinfo=UTC)
        if end_time.tzinfo is None or end_time.utcoffset() is None:
            end_time = end_time.replace(tzinfo=UTC)
        return max(0, int((end_time - created_at).total_seconds()))

    @staticmethod
    def _build_status_copy(
        *,
        batch_id: str,
        status: DetectionBatchStatus,
        result_count: int,
        error_message: str | None,
    ) -> tuple[str, str, str, str, str, str]:
        if status == DetectionBatchStatus.QUEUED:
            return (
                "检测任务已入队",
                "系统已记录本次上传，图像识别任务将自动推进。",
                "等待图像识别任务启动。",
                "已入队",
                "任务 1/3 已完成，等待模型执行。",
                "已入队，等待模型执行",
            )
        if status == DetectionBatchStatus.RUNNING:
            return (
                "图像识别正在执行",
                "系统正在处理图像并准备生成病害档案。",
                "可刷新页面查看最新进度。",
                "执行中",
                "任务 2/3 正在执行。",
                "后台识别中",
            )
        if status == DetectionBatchStatus.FAILED:
            return (
                "检测任务失败",
                error_message or "图像识别任务执行失败。",
                "请检查上传文件后重新创建检测任务。",
                "失败",
                "任务已停止。",
                "处理失败",
            )
        return (
            f"检测完成，生成 {result_count} 条病害档案",
            "病害档案已写入数据库，可在数字档案和知识页面继续查看。",
            "查看下方病害档案和复核入口。",
            "已完成",
            f"批次 {batch_id} 已完成。",
            "识别完成",
        )

    @staticmethod
    def _build_asset_payload(
        asset: DetectionAssetRecord,
        progress: int,
        status_label: str,
    ) -> DetectionAssetPayload:
        return DetectionAssetPayload(
            id=asset.asset_id,
            name=asset.file_name,
            source=asset.capture_context,
            captured_at=_format_display_time(asset.captured_at),
            progress=progress,
            status_label=status_label,
        )

    @staticmethod
    def _build_task_payload(task: DetectionTaskRecord) -> DetectionTaskPayload:
        if task.status == DetectionTaskStatus.COMPLETED:
            eta = "已完成"
        elif task.status == DetectionTaskStatus.FAILED:
            eta = "失败"
        elif task.eta_seconds is None:
            eta = "等待中"
        else:
            eta = f"约 {task.eta_seconds} 秒"

        return DetectionTaskPayload(
            id=task.task_id,
            title=task.title,
            description=task.description,
            status=task.status,
            progress=task.progress,
            eta=eta,
            error_message=task.error_message,
        )

    @staticmethod
    def _build_result_payload(result: DetectionResultRecord) -> DetectionResultPayload:
        return DetectionResultPayload(
            id=result.result_id,
            task_id=result.task_id,
            title=result.title,
            damage_type=result.damage_type_name,
            confidence=result.confidence,
            area=f"{result.area.value:.2f} {result.area.unit}",
            severity=result.severity,
            location=result.location_text,
            component=result.component_name,
            bounding_box=(
                f"x: {result.bounding_box.x}, y: {result.bounding_box.y}, "
                f"w: {result.bounding_box.width}, h: {result.bounding_box.height}"
            ),
            suggestion=result.suggestion,
            summary=result.summary,
            review_status=result.review_status,
            model_version=result.model_version,
            tags=result.tags,
        )


def get_detection_batch_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> DetectionBatchService:
    return DetectionBatchService(DetectionBatchRepository(session))
