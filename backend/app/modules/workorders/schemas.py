from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator

from backend.app.schemas.common import SchemaModel


class WorkOrderStatus(str, Enum):
    CANDIDATE = "candidate"
    CREATED = "created"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class WorkOrderRecord(SchemaModel):
    work_order_id: str
    result_id: str
    batch_id: str
    site_id: str
    component_id: str
    title: str
    damage_type_name: str
    status: WorkOrderStatus
    priority: str
    owner_team: str
    note: str
    created_at: datetime
    updated_at: datetime


class CreateWorkOrderRequest(SchemaModel):
    result_id: str = Field(min_length=1, alias="resultId")
    note: str = Field(default="", max_length=500)

    @field_validator("result_id", "note")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class UpdateWorkOrderStatusRequest(SchemaModel):
    status: WorkOrderStatus
    note: str = Field(default="", max_length=500)

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value: str) -> str:
        cleaned = str(value).strip()
        legacy_statuses = {
            "å€™é€‰å·¥å•": WorkOrderStatus.CANDIDATE.value,
            "候选工单": WorkOrderStatus.CANDIDATE.value,
            "å·²æ´¾å‘": WorkOrderStatus.CREATED.value,
            "已派发": WorkOrderStatus.CREATED.value,
            "å¤„ç†ä¸­": WorkOrderStatus.IN_PROGRESS.value,
            "处理中": WorkOrderStatus.IN_PROGRESS.value,
            "å·²å®Œæˆ": WorkOrderStatus.DONE.value,
            "已完成": WorkOrderStatus.DONE.value,
        }
        return legacy_statuses.get(cleaned, cleaned)

    @field_validator("note")
    @classmethod
    def strip_note(cls, value: str) -> str:
        return value.strip()


class WorkOrderPayload(SchemaModel):
    work_order_id: str = Field(alias="workOrderId")
    result_id: str = Field(alias="resultId")
    batch_id: str = Field(alias="batchId")
    site_id: str = Field(alias="siteId")
    component_id: str = Field(alias="componentId")
    title: str
    damage_type_name: str = Field(alias="damageTypeName")
    status: WorkOrderStatus
    priority: str
    owner_team: str = Field(alias="ownerTeam")
    note: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
