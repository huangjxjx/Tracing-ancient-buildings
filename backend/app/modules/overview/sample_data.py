from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from backend.app.modules.overview.schemas import (
    ArchiveNodeRecord,
    ArchiveUpdateStage,
    BriefingStatus,
    CoordinationEventRecord,
    CoordinationModule,
    HeroMetricRecord,
    IssueRankingRecord,
    IssueSeverity,
    OverviewBriefingRecord,
    OverviewSnapshotRecord,
    RegionalHealthFocusMetric,
    RegionalHealthRecord,
    RegionalHealthStatus,
    RiskLevel,
    WorkOrderRecord,
)


DISPLAY_TIMEZONE = ZoneInfo("Asia/Shanghai")


def _local_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(DISPLAY_TIMEZONE)


def build_overview_sample_snapshot() -> OverviewSnapshotRecord:
    return OverviewSnapshotRecord(
        snapshot_at=_local_datetime("2026-03-15T11:20:00+08:00"),
        hero_metrics=[
            HeroMetricRecord(
                key="connected_sites",
                label="监管建筑",
                total=1,
                note="应县木塔（佛宫寺释迦塔）单体档案",
            ),
            HeroMetricRecord(
                key="archive_nodes",
                label="构件档案",
                total=5,
                note="台基、塔身、塔檐、外槽柱和彩画分区",
            ),
            HeroMetricRecord(
                key="detected_issues",
                label="病害档案",
                total=4,
                note="裂缝、瓦件位移、台基渗水和彩画风化",
            ),
            HeroMetricRecord(
                key="active_orders",
                label="处置事项",
                total=3,
                note="现场复核、排水核查和补充影像采集",
            ),
        ],
        archive_nodes=[
            ArchiveNodeRecord(
                node_id="node_pillar_se",
                name="东南外槽柱组",
                issue_code="timber_crack",
                issue_name="木柱纵向裂缝",
                issue_severity=IssueSeverity.MODERATE,
                risk_level=RiskLevel.HIGH,
                updated_at=_local_datetime("2026-03-15T09:20:00+08:00"),
                update_stage=ArchiveUpdateStage.REVIEWED,
            ),
            ArchiveNodeRecord(
                node_id="node_roof_upper",
                name="上层塔檐瓦件",
                issue_code="tile_displacement",
                issue_name="瓦件位移",
                issue_severity=IssueSeverity.MODERATE,
                risk_level=RiskLevel.HIGH,
                updated_at=_local_datetime("2026-03-15T10:10:00+08:00"),
                update_stage=ArchiveUpdateStage.DECISION_PENDING,
            ),
            ArchiveNodeRecord(
                node_id="node_platform",
                name="南侧台基前缘",
                issue_code="platform_seepage",
                issue_name="渗水返碱",
                issue_severity=IssueSeverity.MINOR,
                risk_level=RiskLevel.MEDIUM,
                updated_at=_local_datetime("2026-03-15T08:40:00+08:00"),
                update_stage=ArchiveUpdateStage.MONITORING,
            ),
            ArchiveNodeRecord(
                node_id="node_painting",
                name="二层外檐彩画",
                issue_code="paint_weathering",
                issue_name="彩画风化",
                risk_level=RiskLevel.MEDIUM,
                updated_at=_local_datetime("2026-03-14T16:30:00+08:00"),
                update_stage=ArchiveUpdateStage.PLAN_ACTIVE,
            ),
        ],
        issue_rankings=[
            IssueRankingRecord(issue_code="timber_crack", issue_name="木构裂缝", score=92),
            IssueRankingRecord(issue_code="tile_displacement", issue_name="瓦件位移", score=84),
            IssueRankingRecord(issue_code="platform_seepage", issue_name="台基渗水", score=68),
            IssueRankingRecord(issue_code="paint_weathering", issue_name="彩画风化", score=57),
            IssueRankingRecord(issue_code="component_tilt", issue_name="构件倾斜", score=41),
        ],
        regional_health=[
            RegionalHealthRecord(
                region_code="yingxian-fogong-core",
                region_name="佛宫寺核心保护范围",
                status=RegionalHealthStatus.HIGH_PRESSURE,
                focus_metric=RegionalHealthFocusMetric.HIGH_RISK_SITES,
                high_risk_sites=2,
                inspection_completion_rate=0.96,
            ),
            RegionalHealthRecord(
                region_code="yingxian-control-zone",
                region_name="建设控制地带",
                status=RegionalHealthStatus.ATTENTION,
                focus_metric=RegionalHealthFocusMetric.INSPECTION_COMPLETION_RATE,
                high_risk_sites=1,
                inspection_completion_rate=0.88,
            ),
            RegionalHealthRecord(
                region_code="yingxian-drainage",
                region_name="佛宫寺周边排水汇水区",
                status=RegionalHealthStatus.ATTENTION,
                focus_metric=RegionalHealthFocusMetric.HUMIDITY_DELTA,
                high_risk_sites=1,
                inspection_completion_rate=0.91,
                humidity_delta_pct=9,
            ),
        ],
        work_orders=[
            WorkOrderRecord(stage_code="image_ingest", stage_name="巡检影像入库", completed=18, total=18),
            WorkOrderRecord(stage_code="ai_detection", stage_name="病害识别", completed=18, total=18),
            WorkOrderRecord(stage_code="expert_review", stage_name="专家复核", completed=11, total=18),
            WorkOrderRecord(stage_code="repair_decision", stage_name="处置决策", completed=3, total=4),
        ],
        overview_briefings=[
            OverviewBriefingRecord(
                briefing_id="briefing_pillar_review",
                title="东南外槽柱裂缝完成一次复核",
                summary="裂缝宽度、含水率和端部状态已回写到数字档案，当前维持高风险关注。",
                status=BriefingStatus.SYNCED,
            ),
            OverviewBriefingRecord(
                briefing_id="briefing_knowledge_strategy",
                title="知识库匹配木构裂缝处理路径",
                summary="处理建议优先要求近景补拍、含水率复测和裂缝活性观察，再判断是否进入修补工序。",
                status=BriefingStatus.STRATEGY_REFRESHED,
            ),
            OverviewBriefingRecord(
                briefing_id="briefing_dispatch",
                title="佛宫寺片区现场任务已排程",
                summary="无人机补拍、台基排水核查和彩画补充影像采集已分配到对应班组。",
                status=BriefingStatus.DISPATCH_ACTIVE,
            ),
        ],
        coordination_events=[
            CoordinationEventRecord(
                event_id="event_detect_001",
                occurred_at=_local_datetime("2026-03-15T09:20:00+08:00"),
                module=CoordinationModule.DETECTION,
                title="东南外槽柱照片完成识别",
                detail="本批次生成 3 条病害档案，其中木构裂缝被标记为高风险。",
            ),
            CoordinationEventRecord(
                event_id="event_twin_001",
                occurred_at=_local_datetime("2026-03-15T10:05:00+08:00"),
                module=CoordinationModule.TWIN,
                title="高风险点位同步到木塔档案",
                detail="裂缝、瓦件位移和台基渗水已绑定到对应构件和数字孪生节点。",
            ),
            CoordinationEventRecord(
                event_id="event_knowledge_001",
                occurred_at=_local_datetime("2026-03-15T11:30:00+08:00"),
                module=CoordinationModule.KNOWLEDGE,
                title="生成木构裂缝与台基渗水处理建议",
                detail="知识页已提供复核清单、处置顺序和文献参考链接。",
            ),
            CoordinationEventRecord(
                event_id="event_dispatch_001",
                occurred_at=_local_datetime("2026-03-15T13:15:00+08:00"),
                module=CoordinationModule.DISPATCH,
                title="佛宫寺核心保护范围进入重点巡查",
                detail="现场巡检组按构件档案执行复核，监管页同步显示任务进度。",
            ),
        ],
    )
