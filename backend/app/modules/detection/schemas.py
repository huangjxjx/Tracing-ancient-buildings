from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator

from backend.app.schemas.common import SchemaModel


class DetectionBatchStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DetectionTaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DetectionSeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DetectionSource(str, Enum):
    DRONE = "drone"
    GROUND = "ground"
    MOBILE = "mobile"


class DetectionReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_RECHECK = "needs_recheck"


class DetectionAreaMeasure(SchemaModel):
    value: float = Field(gt=0)
    unit: str = "m²"


class DetectionBoundingBox(SchemaModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(ge=1)
    height: int = Field(ge=1)


class DetectionAssetRecord(SchemaModel):
    asset_id: str
    file_name: str
    capture_context: str
    captured_at: datetime


class DetectionTaskRecord(SchemaModel):
    task_id: str
    batch_id: str
    stage_code: str
    title: str
    description: str
    status: DetectionTaskStatus
    progress: int = Field(ge=0, le=100)
    eta_seconds: int | None = Field(default=None, ge=0)
    error_message: str | None = None


class DetectionResultRecord(SchemaModel):
    result_id: str
    batch_id: str
    task_id: str
    title: str
    damage_type_code: str
    damage_type_name: str
    confidence: float = Field(ge=0, le=1)
    area: DetectionAreaMeasure
    severity: DetectionSeverity
    location_text: str
    component_name: str
    bounding_box: DetectionBoundingBox
    suggestion: str
    summary: str
    review_status: DetectionReviewStatus
    model_version: str
    tags: list[str]


class DetectionReviewWritebackRecord(SchemaModel):
    result_id: str
    batch_id: str
    site_id: str
    component_id: str
    title: str
    damage_type_name: str
    severity: DetectionSeverity
    location_text: str
    component_name: str
    suggestion: str
    review_status: DetectionReviewStatus
    review_note: str
    reviewed_at: datetime


class DetectionPageResultRecord(SchemaModel):
    result_id: str
    batch_id: str
    site_id: str
    component_id: str
    title: str
    damage_type_code: str
    damage_type_name: str
    severity: DetectionSeverity
    location_text: str
    component_name: str
    suggestion: str
    review_status: DetectionReviewStatus
    detected_at: datetime


class DetectionBatchRecord(SchemaModel):
    batch_id: str
    site_id: str
    component_id: str
    asset_ids: list[str]
    source: DetectionSource
    captured_at: datetime
    created_at: datetime
    status: DetectionBatchStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    error_message: str | None = None


class DetectionBatchAggregate(SchemaModel):
    batch: DetectionBatchRecord
    asset: DetectionAssetRecord
    tasks: list[DetectionTaskRecord]
    results: list[DetectionResultRecord]


class CreateDetectionBatchRequest(SchemaModel):
    site_id: str = Field(min_length=1, alias="siteId")
    component_id: str = Field(min_length=1, alias="componentId")
    asset_ids: list[str] = Field(min_length=1, alias="assetIds")
    source: DetectionSource
    captured_at: datetime = Field(alias="capturedAt")

    @field_validator("site_id", "component_id")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("站点编号和构件编号不能为空。")
        return cleaned

    @field_validator("asset_ids")
    @classmethod
    def validate_asset_ids(cls, value: list[str]) -> list[str]:
        cleaned = [asset_id.strip() for asset_id in value if asset_id.strip()]
        if not cleaned:
            raise ValueError("至少需要提供一个有效的 assetId。")
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("assetId 不能重复。")
        return cleaned

    @field_validator("captured_at")
    @classmethod
    def validate_captured_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("capturedAt 需要带时区信息。")
        return value


class CreateDetectionBatchPayload(SchemaModel):
    batch_id: str = Field(alias="batchId")
    status: DetectionBatchStatus


class ReviewDetectionResultRequest(SchemaModel):
    review_status: DetectionReviewStatus = Field(alias="reviewStatus")
    note: str = Field(default="", max_length=500)

    @field_validator("review_status", mode="before")
    @classmethod
    def normalize_review_status(cls, value: str) -> str:
        cleaned = str(value).strip()
        legacy_statuses = {
            "å·²å¤æ ¸é€šè¿‡": DetectionReviewStatus.APPROVED.value,
            "已复核通过": DetectionReviewStatus.APPROVED.value,
            "å¾…å¤æ ¸": DetectionReviewStatus.PENDING.value,
            "待复核": DetectionReviewStatus.PENDING.value,
        }
        return legacy_statuses.get(cleaned, cleaned)

    @field_validator("note")
    @classmethod
    def strip_note(cls, value: str) -> str:
        return value.strip()


class DetectionAssetPayload(SchemaModel):
    id: str
    name: str
    source: str
    captured_at: str = Field(alias="capturedAt")
    progress: int = Field(ge=0, le=100)
    status_label: str = Field(alias="statusLabel")


class DetectionTaskPayload(SchemaModel):
    id: str
    title: str
    description: str
    status: DetectionTaskStatus
    progress: int = Field(ge=0, le=100)
    eta: str
    error_message: str | None = Field(default=None, alias="errorMessage")


class DetectionResultPayload(SchemaModel):
    id: str
    task_id: str = Field(alias="taskId")
    title: str
    damage_type: str = Field(alias="damageType")
    confidence: float = Field(ge=0, le=1)
    area: str
    severity: DetectionSeverity
    location: str
    component: str
    bounding_box: str = Field(alias="boundingBox")
    suggestion: str
    summary: str
    review_status: DetectionReviewStatus = Field(alias="reviewStatus")
    model_version: str = Field(alias="modelVersion")
    tags: list[str]


class DetectionBatchDetailPayload(SchemaModel):
    batch_id: str = Field(alias="batchId")
    site_id: str = Field(alias="siteId")
    component_id: str = Field(alias="componentId")
    source: DetectionSource
    status: DetectionBatchStatus
    progress: int = Field(ge=0, le=100)
    elapsed_seconds: int = Field(alias="elapsedSeconds", ge=0)
    error_message: str | None = Field(default=None, alias="errorMessage")
    captured_at: str = Field(alias="capturedAt")
    created_at: str = Field(alias="createdAt")
    hero_title: str = Field(alias="heroTitle")
    hero_description: str = Field(alias="heroDescription")
    upload_hint: str = Field(alias="uploadHint")
    upload_badge: str = Field(alias="uploadBadge")
    queue_summary: str = Field(alias="queueSummary")
    asset: DetectionAssetPayload
    tasks: list[DetectionTaskPayload]
    results: list[DetectionResultPayload]
