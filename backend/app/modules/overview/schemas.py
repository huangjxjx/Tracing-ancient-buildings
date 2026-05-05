from datetime import datetime
from enum import Enum

from pydantic import Field

from backend.app.schemas.common import SchemaModel


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IssueSeverity(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"


class ArchiveUpdateStage(str, Enum):
    REVIEWED = "reviewed"
    MONITORING = "monitoring"
    DECISION_PENDING = "decision_pending"
    PLAN_ACTIVE = "plan_active"


class RegionalHealthStatus(str, Enum):
    STABLE = "stable"
    ATTENTION = "attention"
    HIGH_PRESSURE = "high_pressure"


class RegionalHealthFocusMetric(str, Enum):
    HIGH_RISK_SITES = "high_risk_sites"
    INSPECTION_COMPLETION_RATE = "inspection_completion_rate"
    HUMIDITY_DELTA = "humidity_delta"
    WEATHERING_TREND = "weathering_trend"


class BriefingStatus(str, Enum):
    SYNCED = "synced"
    STRATEGY_REFRESHED = "strategy_refreshed"
    DISPATCH_ACTIVE = "dispatch_active"


class CoordinationModule(str, Enum):
    DETECTION = "detection"
    TWIN = "twin"
    KNOWLEDGE = "knowledge"
    DISPATCH = "dispatch"


class HeroMetricRecord(SchemaModel):
    key: str
    label: str
    total: int = Field(ge=0)
    note: str


class ArchiveNodeRecord(SchemaModel):
    node_id: str = Field(serialization_alias="nodeId")
    name: str
    issue_code: str = Field(serialization_alias="issueCode")
    issue_name: str = Field(serialization_alias="issueName")
    issue_severity: IssueSeverity | None = Field(default=None, serialization_alias="issueSeverity")
    risk_level: RiskLevel = Field(serialization_alias="riskLevel")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    update_stage: ArchiveUpdateStage = Field(serialization_alias="updateStage")


class IssueRankingRecord(SchemaModel):
    issue_code: str = Field(serialization_alias="issueCode")
    issue_name: str = Field(serialization_alias="issueName")
    score: int = Field(ge=0, le=100)


class RegionalHealthRecord(SchemaModel):
    region_code: str = Field(serialization_alias="regionCode")
    region_name: str = Field(serialization_alias="regionName")
    status: RegionalHealthStatus
    focus_metric: RegionalHealthFocusMetric = Field(serialization_alias="focusMetric")
    high_risk_sites: int = Field(default=0, serialization_alias="highRiskSites")
    inspection_completion_rate: float = Field(serialization_alias="inspectionCompletionRate")
    humidity_delta_pct: float = Field(default=0, serialization_alias="humidityDeltaPct")
    weathering_delta_pct: float = Field(default=0, serialization_alias="weatheringDeltaPct")


class WorkOrderRecord(SchemaModel):
    stage_code: str = Field(serialization_alias="stageCode")
    stage_name: str = Field(serialization_alias="stageName")
    completed: int = Field(ge=0)
    total: int = Field(ge=0)


class OverviewBriefingRecord(SchemaModel):
    briefing_id: str = Field(serialization_alias="briefingId")
    title: str
    summary: str
    status: BriefingStatus


class CoordinationEventRecord(SchemaModel):
    event_id: str = Field(serialization_alias="eventId")
    occurred_at: datetime = Field(serialization_alias="occurredAt")
    module: CoordinationModule
    title: str
    detail: str


class OverviewSnapshotRecord(SchemaModel):
    snapshot_at: datetime = Field(serialization_alias="snapshotAt")
    hero_metrics: list[HeroMetricRecord] = Field(serialization_alias="heroMetrics")
    archive_nodes: list[ArchiveNodeRecord] = Field(serialization_alias="archiveNodes")
    issue_rankings: list[IssueRankingRecord] = Field(serialization_alias="issueRankings")
    regional_health: list[RegionalHealthRecord] = Field(serialization_alias="regionalHealth")
    work_orders: list[WorkOrderRecord] = Field(serialization_alias="workOrders")
    overview_briefings: list[OverviewBriefingRecord] = Field(serialization_alias="overviewBriefings")
    coordination_events: list[CoordinationEventRecord] = Field(serialization_alias="coordinationEvents")


class HeroMetricCard(SchemaModel):
    label: str
    value: str
    note: str


class ArchiveNodeCard(SchemaModel):
    name: str
    state: str
    risk: str
    update: str


class IssueRankingItem(SchemaModel):
    name: str
    value: int


class RegionalHealthCard(SchemaModel):
    region: str
    status: str
    value: str


class WorkOrderProgress(SchemaModel):
    stage: str
    done: int
    total: int


class OverviewBriefingCard(SchemaModel):
    title: str
    summary: str
    status: str


class CoordinationEventCard(SchemaModel):
    title: str
    module: str
    time: str
    detail: str


class OverviewPagePayload(SchemaModel):
    hero_metrics: list[HeroMetricCard] = Field(serialization_alias="heroMetrics")
    archive_nodes: list[ArchiveNodeCard] = Field(serialization_alias="archiveNodes")
    issue_ranking: list[IssueRankingItem] = Field(serialization_alias="issueRanking")
    regional_health: list[RegionalHealthCard] = Field(serialization_alias="regionalHealth")
    work_orders: list[WorkOrderProgress] = Field(serialization_alias="workOrders")
    overview_briefings: list[OverviewBriefingCard] = Field(serialization_alias="overviewBriefings")
    coordination_events: list[CoordinationEventCard] = Field(serialization_alias="coordinationEvents")
