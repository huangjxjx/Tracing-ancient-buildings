from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db_session
from backend.app.modules.detection.repository import (
    DetectionBatchRepository,
)
from backend.app.modules.detection.schemas import DetectionPageResultRecord, DetectionReviewWritebackRecord, DetectionSeverity
from backend.app.modules.workorders.schemas import WorkOrderRecord, WorkOrderStatus
from backend.app.modules.screen.sample_data import build_screen_page_payload
from backend.app.modules.screen.schemas import (
    ScreenAlert,
    ScreenEvent,
    ScreenMetric,
    ScreenPagePayload,
    ScreenWorkOrderStage,
)


class ScreenPageService:
    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    def get_page_payload(self) -> ScreenPagePayload:
        payload = build_screen_page_payload()
        self._apply_detection_results(payload)
        self._apply_review_writebacks(payload)
        self._apply_work_order_updates(payload)
        return payload

    def _apply_detection_results(self, payload: ScreenPagePayload) -> None:
        if self._session is None:
            return

        results = DetectionBatchRepository(self._session).list_page_results(limit=10)
        if not results:
            return

        payload.screen_alerts.extend(self._build_detection_alert(result) for result in results[:5])
        payload.screen_events.extend(self._build_detection_event(result) for result in results[:5])

    def _apply_review_writebacks(self, payload: ScreenPagePayload) -> None:
        if self._session is None:
            return

        for writeback in DetectionBatchRepository(self._session).list_review_writebacks(limit=3):
            payload.screen_alerts.append(self._build_review_alert(writeback))
            payload.screen_events.append(self._build_review_event(writeback))

    def _apply_work_order_updates(self, payload: ScreenPagePayload) -> None:
        if self._session is None:
            return

        work_orders = DetectionBatchRepository(self._session).list_work_orders(limit=20)
        if not work_orders:
            return

        base_total = int(payload.screen_metrics[-1].value)
        payload.screen_metrics[-1] = ScreenMetric(
            label="在途工单",
            value=str(base_total + len(work_orders)),
            delta=f"新增 {len(work_orders)} 单由病害档案驱动",
        )

        dispatched_count = len(
            [
                item
                for item in work_orders
                if item.status in {WorkOrderStatus.CREATED, WorkOrderStatus.ASSIGNED, WorkOrderStatus.IN_PROGRESS}
            ]
        )
        archived_count = len([item for item in work_orders if item.status == WorkOrderStatus.DONE])
        payload.screen_work_order_stages = [
            self._merge_stage(
                payload.screen_work_order_stages[0],
                extra_done=len(work_orders),
                extra_total=len(work_orders),
                note="新增病害档案触发候选处置任务",
            ),
            self._merge_stage(
                payload.screen_work_order_stages[1],
                extra_done=len(work_orders),
                extra_total=len(work_orders),
                note="复核通过档案已自动进入候选处置池",
            ),
            self._merge_stage(
                payload.screen_work_order_stages[2],
                extra_done=dispatched_count,
                extra_total=len(work_orders),
                note="已派发处置任务开始影响现场执行进度",
            ),
            self._merge_stage(
                payload.screen_work_order_stages[3],
                extra_done=archived_count,
                extra_total=len(work_orders),
                note="已完成处置任务会继续回写知识库和区域态势",
            ),
        ]

        payload.screen_events.extend(
            self._build_work_order_event(item)
            for item in work_orders[:3]
            if item.status != WorkOrderStatus.CANDIDATE
        )

    @staticmethod
    def _merge_stage(
        stage: ScreenWorkOrderStage,
        *,
        extra_done: int,
        extra_total: int,
        note: str,
    ) -> ScreenWorkOrderStage:
        return ScreenWorkOrderStage(
            stage=stage.stage,
            done=stage.done + extra_done,
            total=stage.total + extra_total,
            note=note,
        )

    @staticmethod
    def _build_detection_alert(record: DetectionPageResultRecord) -> ScreenAlert:
        severity_map = {
            DetectionSeverity.HIGH: "high",
            DetectionSeverity.MEDIUM: "medium",
            DetectionSeverity.LOW: "low",
        }
        return ScreenAlert(
            title=f"新增识别告警：{record.title}",
            region=record.site_id,
            severity=severity_map[record.severity],
            detail=f"病害档案 {record.result_id} 位于 {record.location_text}，当前状态：{record.review_status}",
        )

    @staticmethod
    def _build_detection_event(record: DetectionPageResultRecord) -> ScreenEvent:
        return ScreenEvent(
            time=record.detected_at.strftime("%H:%M"),
            type="识别",
            title=f"识别完成：{record.title}",
            detail=f"{record.component_name} 发现 {record.damage_type_name}，结果 {record.result_id} 已进入复核队列。",
        )

    @staticmethod
    def _build_review_alert(record: DetectionReviewWritebackRecord) -> ScreenAlert:
        severity_map = {
            DetectionSeverity.HIGH: "high",
            DetectionSeverity.MEDIUM: "medium",
            DetectionSeverity.LOW: "low",
        }
        return ScreenAlert(
            title=f"{record.title}已复核",
            region="佛宫寺核心保护范围",
            severity=severity_map[record.severity],
            detail=f"档案 {record.result_id} 已回写区域态势，建议下一步查看处理知识并安排处置任务。",
        )

    @staticmethod
    def _build_review_event(record: DetectionReviewWritebackRecord) -> ScreenEvent:
        return ScreenEvent(
            time=record.reviewed_at.strftime("%H:%M"),
            type="复核",
            title=f"人工复核通过：{record.title}",
            detail=f"{record.component_name} 的{record.damage_type_name}已同步到总览、孪生和区域态势。",
        )

    @staticmethod
    def _build_work_order_event(record: WorkOrderRecord) -> ScreenEvent:
        return ScreenEvent(
            time=record.updated_at.strftime("%H:%M"),
            type="处置",
            title=f"处置任务已派发：{record.title}",
            detail=f"{record.owner_team} 已接手 {record.damage_type_name} 处置，当前状态：{record.status}。",
        )


def get_screen_page_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> ScreenPageService:
    return ScreenPageService(session=session)
