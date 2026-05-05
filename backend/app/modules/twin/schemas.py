from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from backend.app.schemas.common import SchemaModel

TwinVector3 = tuple[float, float, float]


class TwinRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TwinScenePrimitive(str, Enum):
    BOX = "box"
    CYLINDER = "cylinder"
    CONE = "cone"


class TwinComponentStatus(str, Enum):
    STABLE = "stable"
    MOISTURE_SENSITIVE = "moisture_sensitive"
    WEATHERING_ATTENTION = "weathering_attention"
    TILE_DISPLACEMENT = "tile_displacement"
    CRACK_WARNING = "crack_warning"


class TwinDamageStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    ALERTING = "alerting"
    MONITORING = "monitoring"
    NEEDS_CAPTURE = "needs_capture"


class TwinMetricRecord(SchemaModel):
    key: str
    label: str
    value_number: float | None = Field(default=None, serialization_alias="valueNumber")
    value_text: str | None = Field(default=None, serialization_alias="valueText")
    unit: str | None = None
    precision: int = 0


class TwinSiteRecord(SchemaModel):
    id: str
    name: str
    region_name: str = Field(serialization_alias="regionName")
    scene_version: str = Field(serialization_alias="sceneVersion")
    model_asset_key: str | None = Field(default=None, serialization_alias="modelAssetKey")
    coordinate_reference: str = Field(serialization_alias="coordinateReference")


class TwinSceneNodeRecord(SchemaModel):
    id: str
    label: str
    primitive: TwinScenePrimitive
    position: TwinVector3
    rotation: TwinVector3 | None = None
    size: TwinVector3 | None = None
    radius_top: float | None = Field(default=None, serialization_alias="radiusTop")
    radius_bottom: float | None = Field(default=None, serialization_alias="radiusBottom")
    radius: float | None = None
    height: float | None = None
    radial_segments: int | None = Field(default=None, serialization_alias="radialSegments")
    color: str
    wire_color: str | None = Field(default=None, serialization_alias="wireColor")
    roughness: float | None = None
    metalness: float | None = None


class TwinComponentRecord(SchemaModel):
    id: str
    name: str
    category: str
    material: str
    risk_level: TwinRiskLevel = Field(serialization_alias="riskLevel")
    status: TwinComponentStatus
    summary: str
    last_inspection_at: datetime = Field(serialization_alias="lastInspectionAt")
    node_ids: list[str] = Field(serialization_alias="nodeIds")
    focus_point: TwinVector3 = Field(serialization_alias="focusPoint")
    metrics: list[TwinMetricRecord]
    related_damage_ids: list[str] = Field(serialization_alias="relatedDamageIds")


class TwinDamagePointRecord(SchemaModel):
    id: str
    name: str
    component_id: str = Field(serialization_alias="componentId")
    type: str
    risk_level: TwinRiskLevel = Field(serialization_alias="riskLevel")
    severity_score: float = Field(serialization_alias="severityScore")
    status: TwinDamageStatus
    description: str
    suggestion: str
    position: TwinVector3
    anchor_node_id: str = Field(serialization_alias="anchorNodeId")
    inspected_at: datetime = Field(serialization_alias="inspectedAt")


class TwinSiteSnapshotRecord(SchemaModel):
    site: TwinSiteRecord
    scene_nodes: list[TwinSceneNodeRecord]
    components: list[TwinComponentRecord]
    damage_points: list[TwinDamagePointRecord]
    default_damage_id: str | None = Field(default=None, serialization_alias="defaultDamageId")


class TwinMetricCard(SchemaModel):
    label: str
    value: str


class TwinComponentCard(SchemaModel):
    id: str
    name: str
    category: str
    material: str
    risk_level: TwinRiskLevel = Field(serialization_alias="riskLevel")
    status: str
    summary: str
    last_inspection: str = Field(serialization_alias="lastInspection")
    node_ids: list[str] = Field(serialization_alias="nodeIds")
    focus_point: TwinVector3 = Field(serialization_alias="focusPoint")
    metrics: list[TwinMetricCard]
    related_damage_ids: list[str] = Field(serialization_alias="relatedDamageIds")


class TwinDamagePointCard(SchemaModel):
    id: str
    name: str
    component_id: str = Field(serialization_alias="componentId")
    type: str
    risk_level: TwinRiskLevel = Field(serialization_alias="riskLevel")
    severity_score: float = Field(serialization_alias="severityScore")
    status: str
    description: str
    suggestion: str
    position: TwinVector3
    anchor_node_id: str = Field(serialization_alias="anchorNodeId")
    inspected_at: str = Field(serialization_alias="inspectedAt")


class TwinPagePayload(SchemaModel):
    site: TwinSiteRecord
    scene_nodes: list[TwinSceneNodeRecord] = Field(serialization_alias="sceneNodes")
    components: list[TwinComponentCard]
    damage_points: list[TwinDamagePointCard] = Field(serialization_alias="damagePoints")
    default_damage_id: str | None = Field(default=None, serialization_alias="defaultDamageId")


class TwinSampleDataset(SchemaModel):
    snapshots: dict[str, TwinSiteSnapshotRecord]
