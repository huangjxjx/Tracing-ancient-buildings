from __future__ import annotations

from datetime import datetime
from typing import Annotated
from typing import Protocol
from zoneinfo import ZoneInfo

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db_session
from backend.app.modules.detection.repository import DetectionBatchRepository
from backend.app.modules.detection.schemas import DetectionPageResultRecord, DetectionReviewWritebackRecord, DetectionSeverity
from backend.app.modules.workorders.schemas import WorkOrderStatus
from backend.app.modules.overview.sample_data import build_overview_sample_snapshot
from backend.app.modules.overview.schemas import (
    ArchiveNodeCard,
    ArchiveNodeRecord,
    ArchiveUpdateStage,
    BriefingStatus,
    CoordinationEventCard,
    CoordinationEventRecord,
    CoordinationModule,
    HeroMetricCard,
    HeroMetricRecord,
    IssueRankingItem,
    IssueRankingRecord,
    IssueSeverity,
    OverviewBriefingCard,
    OverviewBriefingRecord,
    OverviewPagePayload,
    OverviewSnapshotRecord,
    RegionalHealthCard,
    RegionalHealthFocusMetric,
    RegionalHealthRecord,
    RegionalHealthStatus,
    WorkOrderProgress,
    WorkOrderRecord,
)


class OverviewDataProvider(Protocol):
    def get_snapshot(self) -> OverviewSnapshotRecord: ...


class StaticOverviewDataProvider:
    def __init__(self, snapshot: OverviewSnapshotRecord | None = None) -> None:
        self._snapshot = snapshot or build_overview_sample_snapshot()

    def get_snapshot(self) -> OverviewSnapshotRecord:
        return self._snapshot


class OverviewPageService:
    _display_timezone = ZoneInfo("Asia/Shanghai")

    def __init__(self, provider: OverviewDataProvider | None = None, session: Session | None = None) -> None:
        self._provider = provider or StaticOverviewDataProvider()
        self._session = session

    def get_page_payload(self) -> OverviewPagePayload:
        snapshot = self._provider.get_snapshot()
        payload = OverviewPagePayload(
            hero_metrics=[self._build_hero_metric_card(item) for item in snapshot.hero_metrics],
            archive_nodes=[self._build_archive_node_card(item, snapshot.snapshot_at) for item in snapshot.archive_nodes],
            issue_ranking=[
                self._build_issue_ranking_item(item)
                for item in sorted(snapshot.issue_rankings, key=lambda item: item.score, reverse=True)
            ],
            regional_health=[self._build_regional_health_card(item) for item in snapshot.regional_health],
            work_orders=[self._build_work_order_progress(item) for item in snapshot.work_orders],
            overview_briefings=[self._build_overview_briefing_card(item) for item in snapshot.overview_briefings],
            coordination_events=[
                self._build_coordination_event_card(item)
                for item in sorted(snapshot.coordination_events, key=lambda item: item.occurred_at)
            ],
        )
        self._apply_detection_aggregates(payload)
        self._apply_review_writebacks(payload)
        return payload

    def _apply_detection_aggregates(self, payload: OverviewPagePayload) -> None:
        if self._session is None:
            return

        repository = DetectionBatchRepository(self._session)
        results = repository.list_page_results(limit=12)
        if not results:
            return

        issue_counts: dict[str, int] = {}
        for result in results:
            issue_counts[result.damage_type_name] = issue_counts.get(result.damage_type_name, 0) + 1
            payload.overview_briefings.append(self._build_detection_briefing_card(result))
            payload.coordination_events.append(self._build_detection_coordination_card(result))

        existing_issue_names = {item.name for item in payload.issue_ranking}
        for issue_name, count in sorted(issue_counts.items(), key=lambda item: item[1], reverse=True):
            if issue_name not in existing_issue_names:
                payload.issue_ranking.append(IssueRankingItem(name=issue_name, value=min(100, count * 20)))

        work_orders = repository.list_work_orders(limit=50)
        if work_orders:
            dispatched_count = len([item for item in work_orders if item.status != WorkOrderStatus.CANDIDATE])
            payload.work_orders.append(
                WorkOrderProgress(stage="档案处置任务", done=dispatched_count, total=len(work_orders))
            )

    def _apply_review_writebacks(self, payload: OverviewPagePayload) -> None:
        if self._session is None:
            return

        for writeback in DetectionBatchRepository(self._session).list_review_writebacks(limit=3):
            payload.overview_briefings.append(self._build_review_briefing_card(writeback))
            payload.coordination_events.append(self._build_review_coordination_card(writeback))

    @staticmethod
    def _build_hero_metric_card(record: HeroMetricRecord) -> HeroMetricCard:
        return HeroMetricCard(
            label=record.label,
            value=f"{record.total:,}",
            note=record.note,
        )

    @staticmethod
    def _build_archive_node_card(record: ArchiveNodeRecord, snapshot_at: datetime) -> ArchiveNodeCard:
        severity_map = {
            IssueSeverity.MINOR: "\u8f7b\u5fae",
            IssueSeverity.MODERATE: "\u4e2d\u5ea6",
        }
        risk_map = {"low": "I \u7ea7", "medium": "II \u7ea7", "high": "III \u7ea7"}
        severity_prefix = severity_map.get(record.issue_severity, "")
        state = f"{severity_prefix}{record.issue_name}" if severity_prefix else record.issue_name

        return ArchiveNodeCard(
            name=record.name,
            state=state,
            risk=risk_map[record.risk_level.value],
            update=OverviewPageService._format_archive_update(record, snapshot_at),
        )

    @staticmethod
    def _format_archive_update(record: ArchiveNodeRecord, snapshot_at: datetime) -> str:
        if record.update_stage == ArchiveUpdateStage.DECISION_PENDING:
            return "\u5f85\u4fee\u7f2e\u51b3\u7b56"
        if record.update_stage == ArchiveUpdateStage.PLAN_ACTIVE:
            return "\u5df2\u8fdb\u5165\u76d1\u6d4b\u8ba1\u5212"

        local_snapshot_at = OverviewPageService._to_display_time(snapshot_at)
        local_updated_at = OverviewPageService._to_display_time(record.updated_at)
        elapsed = local_snapshot_at - local_updated_at
        elapsed_hours = max(1, int(elapsed.total_seconds() // 3600))
        elapsed_days = local_snapshot_at.date() - local_updated_at.date()

        if record.update_stage == ArchiveUpdateStage.REVIEWED:
            return f"{elapsed_hours} \u5c0f\u65f6\u524d\u590d\u6d4b"
        if record.update_stage == ArchiveUpdateStage.MONITORING and elapsed_days.days == 1:
            return "\u6628\u65e5\u66f4\u65b0"
        if record.update_stage == ArchiveUpdateStage.MONITORING:
            return f"{elapsed_hours} \u5c0f\u65f6\u524d\u66f4\u65b0"

        return local_updated_at.strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def _build_issue_ranking_item(record: IssueRankingRecord) -> IssueRankingItem:
        return IssueRankingItem(name=record.issue_name, value=record.score)

    @staticmethod
    def _build_regional_health_card(record: RegionalHealthRecord) -> RegionalHealthCard:
        status_map = {
            RegionalHealthStatus.STABLE: "\u7a33\u5b9a",
            RegionalHealthStatus.ATTENTION: "\u5173\u6ce8",
            RegionalHealthStatus.HIGH_PRESSURE: "\u9ad8\u538b\u8fd0\u884c",
        }

        if record.focus_metric == RegionalHealthFocusMetric.HIGH_RISK_SITES:
            value = f"{record.high_risk_sites} \u5904\u9ad8\u98ce\u9669\u70b9\u5f85\u590d\u6838"
        elif record.focus_metric == RegionalHealthFocusMetric.HUMIDITY_DELTA:
            value = f"\u6e7f\u5ea6\u589e\u5e45 {record.humidity_delta_pct:.0f}%"
        elif record.focus_metric == RegionalHealthFocusMetric.WEATHERING_TREND:
            value = "\u98ce\u5316\u75c5\u5bb3\u5360\u6bd4\u4e0a\u5347"
        else:
            value = f"\u5de1\u68c0\u5b8c\u6210\u7387 {record.inspection_completion_rate:.0%}"

        return RegionalHealthCard(
            region=record.region_name,
            status=status_map[record.status],
            value=value,
        )

    @staticmethod
    def _build_work_order_progress(record: WorkOrderRecord) -> WorkOrderProgress:
        return WorkOrderProgress(stage=record.stage_name, done=record.completed, total=record.total)

    @staticmethod
    def _build_overview_briefing_card(record: OverviewBriefingRecord) -> OverviewBriefingCard:
        status_map = {
            BriefingStatus.SYNCED: "\u75c5\u5bb3\u8bc6\u522b\u5df2\u56de\u5199",
            BriefingStatus.STRATEGY_REFRESHED: "\u7b56\u7565\u5e93\u6301\u7eed\u6269\u5bb9",
            BriefingStatus.DISPATCH_ACTIVE: "\u8054\u52a8\u94fe\u8def\u5728\u7ebf",
        }
        return OverviewBriefingCard(
            title=record.title,
            summary=record.summary,
            status=status_map[record.status],
        )

    @staticmethod
    def _build_coordination_event_card(record: CoordinationEventRecord) -> CoordinationEventCard:
        module_map = {
            CoordinationModule.DETECTION: "\u75c5\u5bb3\u68c0\u6d4b",
            CoordinationModule.TWIN: "\u6570\u5b57\u5b6a\u751f",
            CoordinationModule.KNOWLEDGE: "\u4fee\u7f2e\u667a\u5e93",
            CoordinationModule.DISPATCH: "\u533a\u57df\u6001\u52bf",
        }
        return CoordinationEventCard(
            title=record.title,
            module=module_map[record.module],
            time=OverviewPageService._to_display_time(record.occurred_at).strftime("%H:%M"),
            detail=record.detail,
        )

    @staticmethod
    def _build_detection_briefing_card(record: DetectionPageResultRecord) -> OverviewBriefingCard:
        severity_label = {
            DetectionSeverity.HIGH: "高风险",
            DetectionSeverity.MEDIUM: "中风险",
            DetectionSeverity.LOW: "低风险",
        }[record.severity]
        return OverviewBriefingCard(
            title=f"新增病害档案：{record.title}",
            summary=f"{record.component_name} 发现 {record.damage_type_name}，位置：{record.location_text}",
            status=f"{severity_label}，待复核",
        )

    @classmethod
    def _build_detection_coordination_card(cls, record: DetectionPageResultRecord) -> CoordinationEventCard:
        return CoordinationEventCard(
            title=f"病害档案已生成：{record.title}",
            module="病害检测",
            time=cls._to_display_time(record.detected_at).strftime("%H:%M"),
            detail=f"病害档案 {record.result_id} 来自检测 {record.batch_id}，当前状态：{record.review_status}",
        )

    @classmethod
    def _build_review_briefing_card(cls, record: DetectionReviewWritebackRecord) -> OverviewBriefingCard:
        return OverviewBriefingCard(
            title=f"复核结果已回写：{record.title}",
            summary=f"{record.component_name} 的{record.damage_type_name}已进入跨模块联动，复核备注：{record.review_note or '无'}。",
            status="病害识别已回写",
        )

    @classmethod
    def _build_review_coordination_card(cls, record: DetectionReviewWritebackRecord) -> CoordinationEventCard:
        return CoordinationEventCard(
            title=f"人工复核通过：{record.title}",
            module="病害检测",
            time=cls._to_display_time(record.reviewed_at).strftime("%H:%M"),
            detail=f"结果 {record.result_id} 已同步至数字孪生、总览聚合和区域态势。",
        )

    @classmethod
    def _to_display_time(cls, value: datetime) -> datetime:
        return value.astimezone(cls._display_timezone)


def get_overview_page_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> OverviewPageService:
    return OverviewPageService(session=session)
