from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.modules.detection.analyzers.base import AnalyzerAsset, AnalyzerFinding
from backend.app.modules.detection.models import (
    DetectionBatchModel,
    DetectionResultModel,
    DetectionTaskModel,
    MediaAssetModel,
    ReviewRecordModel,
    WorkOrderModel,
)
from backend.app.modules.detection.schemas import (
    CreateDetectionBatchRequest,
    DetectionAreaMeasure,
    DetectionAssetRecord,
    DetectionBatchAggregate,
    DetectionBatchRecord,
    DetectionBatchStatus,
    DetectionBoundingBox,
    DetectionPageResultRecord,
    DetectionResultRecord,
    DetectionReviewWritebackRecord,
    DetectionReviewStatus,
    DetectionSeverity,
    DetectionSource,
    DetectionTaskRecord,
    DetectionTaskStatus,
)
from backend.app.modules.workorders.schemas import WorkOrderRecord, WorkOrderStatus


APPROVED_REVIEW_STATUS = DetectionReviewStatus.APPROVED.value
WORK_ORDER_CANDIDATE_STATUS = WorkOrderStatus.CANDIDATE.value
WORK_ORDER_CREATED_STATUS = WorkOrderStatus.CREATED.value

LEGACY_REVIEW_STATUS_MAP = {
    "å·²å¤æ ¸é€šè¿‡": DetectionReviewStatus.APPROVED,
    "已复核通过": DetectionReviewStatus.APPROVED,
    "å¾…å¤æ ¸": DetectionReviewStatus.PENDING,
    "待复核": DetectionReviewStatus.PENDING,
}
LEGACY_WORK_ORDER_STATUS_MAP = {
    "å€™é€‰å·¥å•": WorkOrderStatus.CANDIDATE,
    "候选工单": WorkOrderStatus.CANDIDATE,
    "å·²æ´¾å‘": WorkOrderStatus.CREATED,
    "已派发": WorkOrderStatus.CREATED,
    "å¤„ç†ä¸­": WorkOrderStatus.IN_PROGRESS,
    "处理中": WorkOrderStatus.IN_PROGRESS,
    "å·²å®Œæˆ": WorkOrderStatus.DONE,
    "已完成": WorkOrderStatus.DONE,
}


class DetectionBatchRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def ensure_demo_data(self) -> None:
        asset_id = "IMG_YINGXIAN_PAGODA_20260312_001.jpg"
        created_at = self._utc_datetime("2026-03-12T09:30:00+08:00")
        if self._session.get(MediaAssetModel, asset_id) is None:
            self._session.add(
                MediaAssetModel(
                    asset_id=asset_id,
                    file_name=asset_id,
                    capture_context="应县木塔东南外槽柱组 / 无人机巡检",
                    captured_at=self._utc_datetime("2026-03-12T09:24:00+08:00"),
                    upload_status="uploaded",
                    created_at=created_at,
                    updated_at=created_at,
                )
            )

        demo_batches = {
            DetectionBatchStatus.QUEUED: "batch_demo_queued",
            DetectionBatchStatus.RUNNING: "batch_demo_running",
            DetectionBatchStatus.COMPLETED: "batch_demo_completed",
        }
        existing_ids = {
            row[0]
            for row in self._session.execute(
                select(DetectionBatchModel.batch_id).where(
                    DetectionBatchModel.batch_id.in_(demo_batches.values())
                )
            ).all()
        }
        for status, batch_id in demo_batches.items():
            if batch_id not in existing_ids:
                self._insert_demo_batch(batch_id=batch_id, status=status, asset_id=asset_id, now=created_at)

        self._session.commit()

    def create_batch(self, payload: CreateDetectionBatchRequest) -> DetectionBatchAggregate:
        batch_id = f"batch_{uuid4().hex[:12]}"
        created_at = datetime.now(UTC)
        asset_id = payload.asset_ids[0]

        batch_model = DetectionBatchModel(
            batch_id=batch_id,
            site_id=payload.site_id,
            component_id=payload.component_id,
            source=payload.source.value,
            captured_at=payload.captured_at.astimezone(UTC),
            status=DetectionBatchStatus.QUEUED.value,
            asset_ids_json=json.dumps(payload.asset_ids, ensure_ascii=False),
            created_at=created_at,
            updated_at=created_at,
        )
        self._session.add(batch_model)

        asset_model = self._session.get(MediaAssetModel, asset_id)
        if asset_model is not None:
            asset_model.capture_context = f"{payload.component_id} / {self._source_label(payload.source)}"
            asset_model.captured_at = payload.captured_at.astimezone(UTC)
            asset_model.updated_at = created_at

        self._session.add_all(self._build_task_models(batch_id=batch_id, status=DetectionBatchStatus.QUEUED, now=created_at))
        self._session.commit()
        aggregate = self.get_batch(batch_id)
        if aggregate is None:
            raise LookupError(f"Created detection batch {batch_id} was not found")
        return aggregate

    def get_batch(self, batch_id: str) -> DetectionBatchAggregate | None:
        batch_model = self._session.get(DetectionBatchModel, batch_id)
        if batch_model is None:
            return None

        asset_ids = self._parse_asset_ids(batch_model.asset_ids_json)
        asset_model = self._session.get(MediaAssetModel, asset_ids[0]) if asset_ids else None
        if asset_model is None:
            fallback_asset_id = asset_ids[0] if asset_ids else "missing_asset"
            asset_model = MediaAssetModel(
                asset_id=fallback_asset_id,
                file_name=fallback_asset_id if "." in fallback_asset_id else f"{fallback_asset_id}.jpg",
                capture_context="missing",
                captured_at=batch_model.captured_at,
                upload_status="missing",
                created_at=batch_model.created_at,
                updated_at=batch_model.updated_at,
            )

        task_models = self._session.scalars(
            select(DetectionTaskModel).where(DetectionTaskModel.batch_id == batch_id).order_by(DetectionTaskModel.task_id)
        ).all()
        result_models = self._session.scalars(
            select(DetectionResultModel).where(DetectionResultModel.batch_id == batch_id).order_by(DetectionResultModel.result_id)
        ).all()

        return DetectionBatchAggregate(
            batch=DetectionBatchRecord(
                batch_id=batch_model.batch_id,
                site_id=batch_model.site_id,
                component_id=batch_model.component_id,
                asset_ids=asset_ids,
                source=DetectionSource(batch_model.source),
                captured_at=batch_model.captured_at,
                created_at=batch_model.created_at,
                status=DetectionBatchStatus(batch_model.status),
                started_at=batch_model.started_at,
                completed_at=batch_model.completed_at,
                failed_at=batch_model.failed_at,
                error_message=batch_model.error_message,
            ),
            asset=DetectionAssetRecord(
                asset_id=asset_model.asset_id,
                file_name=asset_model.file_name,
                capture_context=asset_model.capture_context,
                captured_at=asset_model.captured_at,
            ),
            tasks=[
                DetectionTaskRecord(
                    task_id=item.task_id,
                    batch_id=item.batch_id,
                    stage_code=item.stage_code,
                    title=item.title,
                    description=item.description,
                    status=DetectionTaskStatus(item.status),
                    progress=item.progress,
                    eta_seconds=item.eta_seconds,
                    error_message=item.error_message,
                )
                for item in task_models
            ],
            results=[self._build_result_record(item) for item in result_models],
        )

    def list_batches(self, *, limit: int = 20, include_demo: bool = False) -> list[DetectionBatchAggregate]:
        statement = select(DetectionBatchModel).order_by(DetectionBatchModel.created_at.desc()).limit(limit)
        if not include_demo:
            statement = statement.where(~DetectionBatchModel.batch_id.like("batch_demo_%"))

        aggregates: list[DetectionBatchAggregate] = []
        for batch_model in self._session.scalars(statement).all():
            aggregate = self.get_batch(batch_model.batch_id)
            if aggregate is not None:
                aggregates.append(aggregate)
        return aggregates

    def list_results_by_batch(self, batch_id: str) -> list[DetectionResultRecord] | None:
        aggregate = self.get_batch(batch_id)
        if aggregate is None:
            return None
        return aggregate.results

    def delete_batch(self, batch_id: str) -> bool:
        batch_model = self._session.get(DetectionBatchModel, batch_id)
        if batch_model is None:
            return False

        result_ids = [
            row[0]
            for row in self._session.execute(
                select(DetectionResultModel.result_id).where(DetectionResultModel.batch_id == batch_id)
            ).all()
        ]
        if result_ids:
            self._session.execute(delete(WorkOrderModel).where(WorkOrderModel.result_id.in_(result_ids)))
            self._session.execute(delete(ReviewRecordModel).where(ReviewRecordModel.result_id.in_(result_ids)))
            self._session.execute(delete(DetectionResultModel).where(DetectionResultModel.result_id.in_(result_ids)))

        self._session.execute(delete(DetectionTaskModel).where(DetectionTaskModel.batch_id == batch_id))
        self._session.delete(batch_model)
        self._session.commit()
        return True

    def get_result(self, result_id: str) -> DetectionResultRecord | None:
        result_model = self._session.get(DetectionResultModel, result_id)
        if result_model is None:
            return None
        return self._build_result_record(result_model)

    def list_page_results(
        self,
        *,
        limit: int = 20,
        include_demo: bool = False,
    ) -> list[DetectionPageResultRecord]:
        statement = (
            select(DetectionResultModel, DetectionBatchModel)
            .join(DetectionBatchModel, DetectionBatchModel.batch_id == DetectionResultModel.batch_id)
            .where(DetectionBatchModel.status == DetectionBatchStatus.COMPLETED.value)
            .order_by(DetectionResultModel.updated_at.desc(), DetectionResultModel.created_at.desc())
            .limit(limit)
        )
        if not include_demo:
            statement = statement.where(~DetectionBatchModel.batch_id.like("batch_demo_%"))

        return [
            self._build_page_result_record(result_model, batch_model)
            for result_model, batch_model in self._session.execute(statement).all()
        ]

    def mark_batch_running(self, batch_id: str) -> None:
        batch_model = self._session.get(DetectionBatchModel, batch_id)
        if batch_model is None or batch_model.status != DetectionBatchStatus.QUEUED.value:
            return

        now = datetime.now(UTC)
        validation_error = self._validate_batch_assets(batch_model)
        if validation_error is not None:
            self.mark_batch_failed(batch_id=batch_id, error_message=validation_error)
            return

        batch_model.status = DetectionBatchStatus.RUNNING.value
        batch_model.started_at = now
        batch_model.updated_at = now
        for task in self._get_task_models(batch_id):
            task.updated_at = now
            if task.stage_code == "asset_ingest":
                task.status = DetectionTaskStatus.COMPLETED.value
                task.progress = 100
                task.eta_seconds = 0
                task.completed_at = now
                task.description = "上传文件已入库。"
            elif task.stage_code == "model_inference":
                task.status = DetectionTaskStatus.RUNNING.value
                task.progress = 55
                task.eta_seconds = 3
                task.started_at = now
                task.description = "本地识别任务执行中。"
            else:
                task.status = DetectionTaskStatus.PENDING.value
                task.progress = 0
                task.eta_seconds = None
        self._session.commit()

    def get_batch_analyzer_assets(self, batch_id: str) -> tuple[list[AnalyzerAsset], dict[str, str]] | None:
        batch_model = self._session.get(DetectionBatchModel, batch_id)
        if batch_model is None:
            return None

        assets: list[AnalyzerAsset] = []
        for asset_id in self._parse_asset_ids(batch_model.asset_ids_json):
            asset = self._session.get(MediaAssetModel, asset_id)
            if asset is None:
                raise LookupError(f"Asset {asset_id} does not exist.")
            if asset.upload_status != "uploaded" or not asset.storage_path:
                raise ValueError(f"Asset {asset_id} has not been uploaded.")
            assets.append(
                AnalyzerAsset(
                    asset_id=asset.asset_id,
                    filename=asset.file_name,
                    storage_path=Path(asset.storage_path),
                    content_type=asset.content_type or "application/octet-stream",
                    file_size=asset.file_size or 0,
                )
            )

        return assets, {
            "batch_id": batch_model.batch_id,
            "site_id": batch_model.site_id,
            "component_id": batch_model.component_id,
            "source": batch_model.source,
        }

    def mark_batch_completed(self, batch_id: str, findings: list[AnalyzerFinding]) -> None:
        batch_model = self._session.get(DetectionBatchModel, batch_id)
        if batch_model is None or batch_model.status in {
            DetectionBatchStatus.COMPLETED.value,
            DetectionBatchStatus.FAILED.value,
        }:
            return
        if not findings:
            self.mark_batch_failed(batch_id=batch_id, error_message="Analyzer returned no findings.")
            return

        now = datetime.now(UTC)
        batch_model.status = DetectionBatchStatus.COMPLETED.value
        batch_model.completed_at = now
        batch_model.updated_at = now
        batch_model.error_message = None
        for task in self._get_task_models(batch_id):
            task.updated_at = now
            task.status = DetectionTaskStatus.COMPLETED.value
            task.progress = 100
            task.eta_seconds = 0
            task.completed_at = now
            task.error_message = None
            task.description = {
                "asset_ingest": "上传文件已入库。",
                "model_inference": "本地识别任务已输出候选区域。",
                "result_archive": "病害档案已写入数据库。",
            }.get(task.stage_code, "任务已完成。")

        existing_results = self._session.scalars(
            select(DetectionResultModel).where(DetectionResultModel.batch_id == batch_id)
        ).all()
        if not existing_results:
            for result_model in self._build_result_models(batch_id=batch_id, now=now, findings=findings):
                self._session.add(result_model)
        self._session.commit()

    def mark_batch_failed(self, *, batch_id: str, error_message: str) -> None:
        batch_model = self._session.get(DetectionBatchModel, batch_id)
        if batch_model is None or batch_model.status == DetectionBatchStatus.COMPLETED.value:
            return

        now = datetime.now(UTC)
        batch_model.status = DetectionBatchStatus.FAILED.value
        batch_model.failed_at = now
        batch_model.updated_at = now
        batch_model.error_message = error_message
        for task in self._get_task_models(batch_id):
            task.updated_at = now
            if task.status != DetectionTaskStatus.COMPLETED.value:
                task.status = DetectionTaskStatus.FAILED.value
                task.failed_at = now
                task.error_message = error_message
                task.eta_seconds = 0
        self._session.commit()

    def update_result_review(self, *, result_id: str, review_status: str, note: str) -> DetectionResultRecord | None:
        result_model = self._session.get(DetectionResultModel, result_id)
        if result_model is None:
            return None

        now = datetime.now(UTC)
        normalized_review_status = self._normalize_review_status(review_status).value
        result_model.review_status = normalized_review_status
        result_model.updated_at = now
        self._session.add(
            ReviewRecordModel(
                review_id=f"review_{uuid4().hex[:12]}",
                result_id=result_id,
                review_status=normalized_review_status,
                note=note,
                created_at=now,
                updated_at=now,
            )
        )
        if normalized_review_status == APPROVED_REVIEW_STATUS:
            self._ensure_work_order(result_model, now)
        self._session.commit()
        return self._build_result_record(result_model)

    def list_review_writebacks(
        self,
        *,
        review_status: str = APPROVED_REVIEW_STATUS,
        limit: int = 5,
    ) -> list[DetectionReviewWritebackRecord]:
        normalized_review_status = self._normalize_review_status(review_status)
        matching_statuses = [
            value
            for value, normalized in LEGACY_REVIEW_STATUS_MAP.items()
            if normalized == normalized_review_status
        ]
        matching_statuses.append(normalized_review_status.value)
        review_models = self._session.scalars(
            select(ReviewRecordModel)
            .where(ReviewRecordModel.review_status.in_(matching_statuses))
            .order_by(ReviewRecordModel.updated_at.desc())
            .limit(limit)
        ).all()

        writebacks: list[DetectionReviewWritebackRecord] = []
        seen_result_ids: set[str] = set()
        for review_model in review_models:
            if review_model.result_id in seen_result_ids:
                continue
            result_model = self._session.get(DetectionResultModel, review_model.result_id)
            if result_model is None:
                continue
            batch_model = self._session.get(DetectionBatchModel, result_model.batch_id)
            if batch_model is None:
                continue
            writebacks.append(
                DetectionReviewWritebackRecord(
                    result_id=result_model.result_id,
                    batch_id=result_model.batch_id,
                    site_id=batch_model.site_id,
                    component_id=batch_model.component_id,
                    title=result_model.title,
                    damage_type_name=result_model.damage_type_name,
                    severity=DetectionSeverity(result_model.severity),
                    location_text=result_model.location_text,
                    component_name=result_model.component_name,
                    suggestion=result_model.suggestion,
                    review_status=self._normalize_review_status(review_model.review_status),
                    review_note=review_model.note,
                    reviewed_at=review_model.updated_at,
                )
            )
            seen_result_ids.add(review_model.result_id)
        return writebacks

    def create_upload_asset(self, *, filename: str, content_type: str, biz_type: str) -> tuple[str, str]:
        asset_id = f"asset_{uuid4().hex[:12]}"
        now = datetime.now(UTC)
        object_key = f"{biz_type}/{now:%Y/%m}/{asset_id}_{filename}"
        self._session.add(
            MediaAssetModel(
                asset_id=asset_id,
                file_name=filename,
                capture_context=biz_type,
                captured_at=now,
                content_type=content_type,
                object_key=object_key,
                upload_status="pending",
                created_at=now,
                updated_at=now,
            )
        )
        self._session.commit()
        return asset_id, object_key

    def get_upload_asset(self, asset_id: str) -> MediaAssetModel | None:
        return self._session.get(MediaAssetModel, asset_id)

    def mark_upload_completed(self, *, asset_id: str, storage_path: str, file_size: int, content_type: str) -> MediaAssetModel | None:
        asset_model = self._session.get(MediaAssetModel, asset_id)
        if asset_model is None:
            return None

        asset_model.storage_path = storage_path
        asset_model.file_size = file_size
        asset_model.content_type = content_type
        asset_model.upload_status = "uploaded"
        asset_model.updated_at = datetime.now(UTC)
        self._session.commit()
        return asset_model

    def list_work_orders(self, *, limit: int = 20) -> list[WorkOrderRecord]:
        work_order_models = self._session.scalars(
            select(WorkOrderModel).order_by(WorkOrderModel.updated_at.desc()).limit(limit)
        ).all()
        return [self._build_work_order_record(model) for model in work_order_models]

    def get_work_order(self, work_order_id: str) -> WorkOrderRecord | None:
        work_order_model = self._session.get(WorkOrderModel, work_order_id)
        if work_order_model is None:
            return None
        return self._build_work_order_record(work_order_model)

    def create_work_order(self, *, result_id: str, note: str = "") -> WorkOrderRecord | None:
        result_model = self._session.get(DetectionResultModel, result_id)
        if result_model is None:
            return None

        now = datetime.now(UTC)
        existing = self._session.scalars(
            select(WorkOrderModel).where(WorkOrderModel.result_id == result_id)
        ).first()
        if existing is not None:
            if self._normalize_work_order_status(existing.status) == WorkOrderStatus.CANDIDATE:
                existing.status = WORK_ORDER_CREATED_STATUS
            if note:
                existing.note = note
            existing.updated_at = now
            self._session.commit()
            return self._build_work_order_record(existing)

        work_order_model = WorkOrderModel(
            work_order_id=f"wo_{uuid4().hex[:12]}",
            result_id=result_model.result_id,
            title=f"{result_model.title}修缮工单",
            status=WORK_ORDER_CREATED_STATUS,
            priority=self._priority_from_severity(result_model.severity),
            owner_team=self._owner_team_from_damage(result_model.damage_type_code),
            note=note or "由复核结果转为正式工单。",
            created_at=now,
            updated_at=now,
        )
        self._session.add(work_order_model)
        self._session.commit()
        return self._build_work_order_record(work_order_model)

    def update_work_order_status(
        self,
        *,
        work_order_id: str,
        status: WorkOrderStatus,
        note: str = "",
    ) -> WorkOrderRecord | None:
        work_order_model = self._session.get(WorkOrderModel, work_order_id)
        if work_order_model is None:
            return None

        work_order_model.status = self._normalize_work_order_status(status).value
        if note:
            work_order_model.note = note
        work_order_model.updated_at = datetime.now(UTC)
        self._session.commit()
        return self._build_work_order_record(work_order_model)

    def _ensure_work_order(self, result_model: DetectionResultModel, now: datetime) -> None:
        existing = self._session.scalars(
            select(WorkOrderModel).where(WorkOrderModel.result_id == result_model.result_id)
        ).first()
        if existing is not None:
            if self._normalize_work_order_status(existing.status) == WorkOrderStatus.CANDIDATE:
                existing.status = WORK_ORDER_CANDIDATE_STATUS
            existing.updated_at = now
            return

        self._session.add(
            WorkOrderModel(
                work_order_id=f"wo_{uuid4().hex[:12]}",
                result_id=result_model.result_id,
                title=f"{result_model.title}修缮候选工单",
                status=WORK_ORDER_CANDIDATE_STATUS,
                priority=self._priority_from_severity(result_model.severity),
                owner_team=self._owner_team_from_damage(result_model.damage_type_code),
                note="识别结果已复核通过，等待转正式工单。",
                created_at=now,
                updated_at=now,
            )
        )

    def _insert_demo_batch(
        self,
        *,
        batch_id: str,
        status: DetectionBatchStatus,
        asset_id: str,
        now: datetime,
    ) -> None:
        self._session.add(
            DetectionBatchModel(
                batch_id=batch_id,
                site_id="site_001",
                component_id="component-pillar-east",
                source=DetectionSource.DRONE.value,
                captured_at=self._utc_datetime("2026-03-12T09:24:00+08:00"),
                status=status.value,
                asset_ids_json=json.dumps([asset_id], ensure_ascii=False),
                started_at=now if status in {DetectionBatchStatus.RUNNING, DetectionBatchStatus.COMPLETED} else None,
                completed_at=now if status == DetectionBatchStatus.COMPLETED else None,
                created_at=now,
                updated_at=now,
            )
        )
        self._session.add_all(self._build_task_models(batch_id=batch_id, status=status, now=now))
        if status == DetectionBatchStatus.COMPLETED:
            self._session.add_all(
                self._build_result_models(
                    batch_id=batch_id,
                    now=now,
                    findings=self._build_demo_findings(batch_id=batch_id),
                )
            )

    def _validate_batch_assets(self, batch_model: DetectionBatchModel) -> str | None:
        for asset_id in self._parse_asset_ids(batch_model.asset_ids_json):
            asset = self._session.get(MediaAssetModel, asset_id)
            if asset is None:
                return f"Asset {asset_id} does not exist."
            if asset.upload_status == "pending":
                return f"Asset {asset_id} has not been uploaded."
        return None

    def _get_task_models(self, batch_id: str) -> list[DetectionTaskModel]:
        return list(
            self._session.scalars(
                select(DetectionTaskModel).where(DetectionTaskModel.batch_id == batch_id)
            ).all()
        )

    @staticmethod
    def _parse_asset_ids(asset_ids_json: str) -> list[str]:
        return list(json.loads(asset_ids_json))

    @staticmethod
    def _utc_datetime(value: str) -> datetime:
        return datetime.fromisoformat(value).astimezone(UTC)

    @staticmethod
    def _source_label(source: DetectionSource) -> str:
        return {
            DetectionSource.DRONE: "无人机",
            DetectionSource.GROUND: "地面巡检",
            DetectionSource.MOBILE: "移动端",
        }[source]

    @staticmethod
    def _priority_from_severity(severity: str) -> str:
        return {
            DetectionSeverity.HIGH.value: "高",
            DetectionSeverity.MEDIUM.value: "中",
            DetectionSeverity.LOW.value: "低",
        }.get(severity, "中")

    @staticmethod
    def _owner_team_from_damage(damage_type_code: str) -> str:
        if "stone" in damage_type_code:
            return "石作修缮组"
        if "paint" in damage_type_code:
            return "彩画修缮组"
        return "木作修缮组"

    @staticmethod
    def _build_task_models(
        *,
        batch_id: str,
        status: DetectionBatchStatus,
        now: datetime,
    ) -> list[DetectionTaskModel]:
        task_specs = [
            ("ingest", "asset_ingest", "文件入库", "上传文件等待入库。"),
            ("detect", "model_inference", "本地识别", "等待本地识别任务执行。"),
            ("archive", "result_archive", "档案写入", "等待病害档案写入数据库。"),
        ]
        task_models: list[DetectionTaskModel] = []
        for suffix, stage_code, title, description in task_specs:
            task_status = DetectionTaskStatus.PENDING
            progress = 0
            eta_seconds: int | None = None
            started_at = None
            completed_at = None
            if status == DetectionBatchStatus.QUEUED and stage_code == "asset_ingest":
                task_status = DetectionTaskStatus.COMPLETED
                progress = 100
                eta_seconds = 0
                completed_at = now
                description = "上传文件已入库。"
            elif status == DetectionBatchStatus.RUNNING:
                if stage_code == "asset_ingest":
                    task_status = DetectionTaskStatus.COMPLETED
                    progress = 100
                    eta_seconds = 0
                    completed_at = now
                    description = "上传文件已入库。"
                elif stage_code == "model_inference":
                    task_status = DetectionTaskStatus.RUNNING
                    progress = 55
                    eta_seconds = 3
                    started_at = now
                    description = "本地识别任务执行中。"
            elif status == DetectionBatchStatus.COMPLETED:
                task_status = DetectionTaskStatus.COMPLETED
                progress = 100
                eta_seconds = 0
                completed_at = now
                description = "任务已完成。"

            task_models.append(
                DetectionTaskModel(
                    task_id=f"{batch_id}_{suffix}",
                    batch_id=batch_id,
                    stage_code=stage_code,
                    title=title,
                    description=description,
                    status=task_status.value,
                    progress=progress,
                    eta_seconds=eta_seconds,
                    started_at=started_at,
                    completed_at=completed_at,
                    created_at=now,
                    updated_at=now,
                )
            )
        return task_models

    @staticmethod
    def _build_result_models(
        *,
        batch_id: str,
        now: datetime,
        findings: list[AnalyzerFinding],
    ) -> list[DetectionResultModel]:
        task_id = f"{batch_id}_detect"
        return [
            DetectionResultModel(
                result_id=f"{batch_id}_result_{finding.result_suffix}",
                batch_id=batch_id,
                task_id=task_id,
                title=finding.title,
                damage_type_code=finding.damage_type_code,
                damage_type_name=finding.damage_type_name,
                confidence=finding.confidence,
                area_value=finding.area_value,
                area_unit="m2",
                severity=finding.severity.value,
                location_text=finding.location_text,
                component_name=finding.component_name,
                bbox_x=finding.bounding_box[0],
                bbox_y=finding.bounding_box[1],
                bbox_width=finding.bounding_box[2],
                bbox_height=finding.bounding_box[3],
                suggestion=finding.suggestion,
                summary=finding.summary,
                review_status="待复核",
                model_version=finding.analyzer_version,
                tags_json=json.dumps(finding.tags, ensure_ascii=False),
                created_at=now,
                updated_at=now,
            )
            for finding in findings
        ]

    @staticmethod
    def _build_demo_findings(*, batch_id: str) -> list[AnalyzerFinding]:
        return [
            AnalyzerFinding(
                result_suffix="demo_timber_crack",
                title="东南外槽柱纵向裂缝",
                damage_type_code="timber_crack",
                damage_type_name="木构裂缝",
                confidence=0.94,
                area_value=0.36,
                severity=DetectionSeverity.HIGH,
                location_text="东南外槽柱 2.1m-2.8m",
                component_name="东南外槽柱组",
                bounding_box=(412, 188, 116, 284),
                suggestion="建议立即复核裂缝宽度，必要时设置临时支护。",
                summary="识别到纵向裂缝，位置集中在受力构件中段。",
                tags=["高风险", "木构", "裂缝"],
                analyzer_version="demo-seed",
            ),
            AnalyzerFinding(
                result_suffix="demo_stone_spalling",
                title="上层塔檐瓦件位移",
                damage_type_code="tile_displacement",
                damage_type_name="瓦件位移",
                confidence=0.88,
                area_value=1.12,
                severity=DetectionSeverity.MEDIUM,
                location_text="上层塔檐转折部位",
                component_name="五层六檐屋面",
                bounding_box=(108, 426, 208, 122),
                suggestion="建议补拍无人机近景，确认位移边界和临时围控范围。",
                summary="塔檐局部瓦件存在位移，需要复核近期变化趋势。",
                tags=["中风险", "瓦作", "位移"],
                analyzer_version="demo-seed",
            ),
            AnalyzerFinding(
                result_suffix="demo_paint_fading",
                title="塔身彩画风化",
                damage_type_code="paint_fading",
                damage_type_name="彩画风化",
                confidence=0.82,
                area_value=0.22,
                severity=DetectionSeverity.LOW,
                location_text="二层外檐彩画表层",
                component_name="八角塔身主体",
                bounding_box=(286, 142, 94, 88),
                suggestion="建议补充多光谱影像，并与历史照片对比颜色边界。",
                summary="局部颜色衰减，需结合材料复核判断风化程度。",
                tags=["低风险", "彩画", "复拍"],
                analyzer_version="demo-seed",
            ),
        ]

    @staticmethod
    def _normalize_review_status(value: str | DetectionReviewStatus) -> DetectionReviewStatus:
        if isinstance(value, DetectionReviewStatus):
            return value
        cleaned = str(value).strip()
        if cleaned in DetectionReviewStatus._value2member_map_:
            return DetectionReviewStatus(cleaned)
        return LEGACY_REVIEW_STATUS_MAP.get(cleaned, DetectionReviewStatus.PENDING)

    @staticmethod
    def _normalize_work_order_status(value: str | WorkOrderStatus) -> WorkOrderStatus:
        if isinstance(value, WorkOrderStatus):
            return value
        cleaned = str(value).strip()
        if cleaned in WorkOrderStatus._value2member_map_:
            return WorkOrderStatus(cleaned)
        return LEGACY_WORK_ORDER_STATUS_MAP.get(cleaned, WorkOrderStatus.CANDIDATE)

    @staticmethod
    def _build_result_record(result_model: DetectionResultModel) -> DetectionResultRecord:
        return DetectionResultRecord(
            result_id=result_model.result_id,
            batch_id=result_model.batch_id,
            task_id=result_model.task_id,
            title=result_model.title,
            damage_type_code=result_model.damage_type_code,
            damage_type_name=result_model.damage_type_name,
            confidence=result_model.confidence,
            area=DetectionAreaMeasure(value=result_model.area_value, unit=result_model.area_unit),
            severity=DetectionSeverity(result_model.severity),
            location_text=result_model.location_text,
            component_name=result_model.component_name,
            bounding_box=DetectionBoundingBox(
                x=result_model.bbox_x,
                y=result_model.bbox_y,
                width=result_model.bbox_width,
                height=result_model.bbox_height,
            ),
            suggestion=result_model.suggestion,
            summary=result_model.summary,
            review_status=DetectionBatchRepository._normalize_review_status(result_model.review_status),
            model_version=result_model.model_version,
            tags=json.loads(result_model.tags_json),
        )

    @staticmethod
    def _build_page_result_record(
        result_model: DetectionResultModel,
        batch_model: DetectionBatchModel,
    ) -> DetectionPageResultRecord:
        return DetectionPageResultRecord(
            result_id=result_model.result_id,
            batch_id=result_model.batch_id,
            site_id=batch_model.site_id,
            component_id=batch_model.component_id,
            title=result_model.title,
            damage_type_code=result_model.damage_type_code,
            damage_type_name=result_model.damage_type_name,
            severity=DetectionSeverity(result_model.severity),
            location_text=result_model.location_text,
            component_name=result_model.component_name,
            suggestion=result_model.suggestion,
            review_status=DetectionBatchRepository._normalize_review_status(result_model.review_status),
            detected_at=batch_model.completed_at or result_model.created_at,
        )

    def _build_work_order_record(self, work_order_model: WorkOrderModel) -> WorkOrderRecord:
        result_model = self._session.get(DetectionResultModel, work_order_model.result_id)
        if result_model is None:
            raise LookupError(f"Missing detection result for work order {work_order_model.work_order_id}")
        batch_model = self._session.get(DetectionBatchModel, result_model.batch_id)
        if batch_model is None:
            raise LookupError(f"Missing detection batch for work order {work_order_model.work_order_id}")

        return WorkOrderRecord(
            work_order_id=work_order_model.work_order_id,
            result_id=work_order_model.result_id,
            batch_id=result_model.batch_id,
            site_id=batch_model.site_id,
            component_id=batch_model.component_id,
            title=work_order_model.title,
            damage_type_name=result_model.damage_type_name,
            status=self._normalize_work_order_status(work_order_model.status),
            priority=work_order_model.priority,
            owner_team=work_order_model.owner_team,
            note=work_order_model.note,
            created_at=work_order_model.created_at,
            updated_at=work_order_model.updated_at,
        )
