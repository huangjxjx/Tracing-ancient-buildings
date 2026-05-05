from typing import Literal

from pydantic import Field

from backend.app.schemas.common import SchemaModel


class ScreenMetric(SchemaModel):
    label: str
    value: str
    delta: str


class ScreenCommandNote(SchemaModel):
    label: str
    value: str
    detail: str


class ScreenCoverageRegion(SchemaModel):
    region: str
    health_index: int = Field(serialization_alias="healthIndex")
    connected_sites: int = Field(serialization_alias="connectedSites")
    high_risk_count: int = Field(serialization_alias="highRiskCount")
    work_order_progress: int = Field(serialization_alias="workOrderProgress")
    status: Literal["critical", "watch", "stable"]


class ScreenIssue(SchemaModel):
    label: str
    value: int
    count: str


class ScreenWorkOrderStage(SchemaModel):
    stage: str
    done: int
    total: int
    note: str


class ScreenAlert(SchemaModel):
    title: str
    region: str
    severity: Literal["high", "medium", "low"]
    detail: str


class ScreenDispatch(SchemaModel):
    team: str
    region: str
    mission: str
    progress: int


class ScreenRegionDetail(SchemaModel):
    region: str
    commander_window: str = Field(serialization_alias="commanderWindow")
    response_mode: str = Field(serialization_alias="responseMode")
    focus: str
    next_action: str = Field(serialization_alias="nextAction")


class ScreenEvent(SchemaModel):
    time: str
    type: str
    title: str
    detail: str


class ScreenPagePayload(SchemaModel):
    screen_metrics: list[ScreenMetric] = Field(serialization_alias="screenMetrics")
    screen_command_notes: list[ScreenCommandNote] = Field(serialization_alias="screenCommandNotes")
    screen_coverage_regions: list[ScreenCoverageRegion] = Field(serialization_alias="screenCoverageRegions")
    screen_issues_top5: list[ScreenIssue] = Field(serialization_alias="screenIssuesTop5")
    screen_work_order_stages: list[ScreenWorkOrderStage] = Field(serialization_alias="screenWorkOrderStages")
    screen_alerts: list[ScreenAlert] = Field(serialization_alias="screenAlerts")
    screen_dispatches: list[ScreenDispatch] = Field(serialization_alias="screenDispatches")
    screen_region_details: list[ScreenRegionDetail] = Field(serialization_alias="screenRegionDetails")
    screen_events: list[ScreenEvent] = Field(serialization_alias="screenEvents")
