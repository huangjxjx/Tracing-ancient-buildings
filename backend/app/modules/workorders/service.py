from __future__ import annotations

from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db_session
from backend.app.modules.detection.repository import DetectionBatchRepository
from backend.app.modules.workorders.schemas import (
    CreateWorkOrderRequest,
    UpdateWorkOrderStatusRequest,
    WorkOrderPayload,
    WorkOrderRecord,
)


DISPLAY_TIMEZONE = ZoneInfo("Asia/Shanghai")


class WorkOrderService:
    def __init__(self, repository: DetectionBatchRepository) -> None:
        self._repository = repository
        self._repository.ensure_demo_data()

    def list_work_orders(self, *, limit: int = 20) -> list[WorkOrderPayload]:
        return [self._build_payload(record) for record in self._repository.list_work_orders(limit=limit)]

    def get_work_order(self, work_order_id: str) -> WorkOrderPayload | None:
        record = self._repository.get_work_order(work_order_id)
        if record is None:
            return None
        return self._build_payload(record)

    def create_work_order(self, payload: CreateWorkOrderRequest) -> WorkOrderPayload | None:
        record = self._repository.create_work_order(result_id=payload.result_id, note=payload.note)
        if record is None:
            return None
        return self._build_payload(record)

    def update_work_order_status(
        self,
        work_order_id: str,
        payload: UpdateWorkOrderStatusRequest,
    ) -> WorkOrderPayload | None:
        record = self._repository.update_work_order_status(
            work_order_id=work_order_id,
            status=payload.status,
            note=payload.note,
        )
        if record is None:
            return None
        return self._build_payload(record)

    @staticmethod
    def _build_payload(record: WorkOrderRecord) -> WorkOrderPayload:
        return WorkOrderPayload(
            work_order_id=record.work_order_id,
            result_id=record.result_id,
            batch_id=record.batch_id,
            site_id=record.site_id,
            component_id=record.component_id,
            title=record.title,
            damage_type_name=record.damage_type_name,
            status=record.status,
            priority=record.priority,
            owner_team=record.owner_team,
            note=record.note,
            created_at=record.created_at.astimezone(DISPLAY_TIMEZONE).strftime("%Y-%m-%d %H:%M"),
            updated_at=record.updated_at.astimezone(DISPLAY_TIMEZONE).strftime("%Y-%m-%d %H:%M"),
        )


def get_work_order_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> WorkOrderService:
    return WorkOrderService(DetectionBatchRepository(session))
