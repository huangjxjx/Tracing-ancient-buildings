from __future__ import annotations

from datetime import datetime

from backend.app.modules.twin.schemas import (
    TwinComponentRecord,
    TwinComponentStatus,
    TwinDamagePointRecord,
    TwinDamageStatus,
    TwinMetricRecord,
    TwinRiskLevel,
    TwinSampleDataset,
    TwinSceneNodeRecord,
    TwinScenePrimitive,
    TwinSiteRecord,
    TwinSiteSnapshotRecord,
)


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _box(
    node_id: str,
    label: str,
    size: tuple[float, float, float],
    position: tuple[float, float, float],
    color: str,
    wire_color: str,
    rotation: tuple[float, float, float] | None = None,
) -> TwinSceneNodeRecord:
    return TwinSceneNodeRecord(
        id=node_id,
        label=label,
        primitive=TwinScenePrimitive.BOX,
        size=size,
        position=position,
        rotation=rotation,
        color=color,
        wire_color=wire_color,
        roughness=0.82,
    )


def _cylinder(
    node_id: str,
    label: str,
    radius_top: float,
    radius_bottom: float,
    height: float,
    position: tuple[float, float, float],
    color: str,
    wire_color: str,
    radial_segments: int = 8,
) -> TwinSceneNodeRecord:
    return TwinSceneNodeRecord(
        id=node_id,
        label=label,
        primitive=TwinScenePrimitive.CYLINDER,
        radius_top=radius_top,
        radius_bottom=radius_bottom,
        height=height,
        radial_segments=radial_segments,
        position=position,
        color=color,
        wire_color=wire_color,
        roughness=0.76,
    )


def _cone(
    node_id: str,
    label: str,
    radius: float,
    height: float,
    position: tuple[float, float, float],
    color: str,
    wire_color: str,
    radial_segments: int = 8,
) -> TwinSceneNodeRecord:
    return TwinSceneNodeRecord(
        id=node_id,
        label=label,
        primitive=TwinScenePrimitive.CONE,
        radius=radius,
        height=height,
        radial_segments=radial_segments,
        position=position,
        rotation=(0, 0.3926990817, 0),
        color=color,
        wire_color=wire_color,
        roughness=0.7,
    )


def _pagoda_scene_nodes() -> list[TwinSceneNodeRecord]:
    nodes: list[TwinSceneNodeRecord] = [
        _box("site-ground", "佛宫寺院落地面", (38, 0.38, 38), (0, -0.19, 0), "#d6c4a4", "#b69b72"),
        _cylinder("foundation-octagon", "八角须弥台基", 9.2, 10.2, 1.05, (0, 0.52, 0), "#b89e79", "#826f50", 8),
        _cylinder("foundation-upper", "上层台明", 7.4, 8.2, 0.52, (0, 1.3, 0), "#c3a77c", "#8b734f", 8),
        _box("south-stair", "南向踏跺", (2.2, 0.35, 3.2), (0, 0.34, 10.4), "#b79d77", "#806a4a"),
    ]

    floor_specs = [
        (1, 2.05, 6.4, 2.0, 8.1),
        (2, 4.35, 5.55, 1.72, 7.1),
        (3, 6.35, 4.8, 1.48, 6.2),
        (4, 8.1, 4.05, 1.26, 5.35),
        (5, 9.62, 3.35, 1.02, 4.55),
    ]
    for index, center_y, radius, height, roof_radius in floor_specs:
        nodes.extend(
            [
                _cylinder(
                    f"floor-{index}-body",
                    f"{index} 层八角塔身",
                    radius,
                    radius * 1.03,
                    height,
                    (0, center_y, 0),
                    "#d8bd8c",
                    "#8a6a45",
                    8,
                ),
                _cylinder(
                    f"floor-{index}-balcony",
                    f"{index} 层平座栏杆",
                    roof_radius * 0.93,
                    roof_radius * 0.93,
                    0.18,
                    (0, center_y + height * 0.48 + 0.08, 0),
                    "#7e4d32",
                    "#56341f",
                    8,
                ),
                _cone(
                    f"floor-{index}-eave",
                    f"{index} 层出檐屋面",
                    roof_radius,
                    0.95,
                    (0, center_y + height * 0.5 + 0.55, 0),
                    "#914935",
                    "#6e3022",
                    8,
                ),
            ]
        )

    nodes.extend(
        [
            _cylinder("spire-base", "塔刹基座", 1.15, 1.35, 0.42, (0, 11.22, 0), "#715338", "#4d3826", 16),
            _cone("spire-body", "塔刹", 1.15, 2.2, (0, 12.35, 0), "#6d4b2f", "#4a331f", 16),
        ]
    )

    pillar_positions = [
        ("east-front", 5.8, 5.8),
        ("east-back", 5.8, -5.8),
        ("west-front", -5.8, 5.8),
        ("west-back", -5.8, -5.8),
        ("north", 0, -7.1),
        ("south", 0, 7.1),
    ]
    for name, x, z in pillar_positions:
        nodes.append(
            _cylinder(
                f"pillar-{name}",
                f"{name} 外檐柱",
                0.34,
                0.42,
                5.7,
                (x, 4.4, z),
                "#7f4f33",
                "#57341f",
                16,
            )
        )

    return nodes


def build_twin_sample_dataset() -> TwinSampleDataset:
    return TwinSampleDataset(
        snapshots={
            "site_001": TwinSiteSnapshotRecord(
                site=TwinSiteRecord(
                    id="site_001",
                    name="应县木塔（佛宫寺释迦塔）",
                    region_name="山西省朔州市应县佛宫寺片区",
                    scene_version="yingxian-pagoda-procedural-v2",
                    model_asset_key=None,
                    coordinate_reference="local-octagonal-anchor-v2",
                ),
                scene_nodes=_pagoda_scene_nodes(),
                components=[
                    TwinComponentRecord(
                        id="component-platform",
                        name="八角台基与踏跺",
                        category="基础",
                        material="砖石台基",
                        risk_level=TwinRiskLevel.MEDIUM,
                        status=TwinComponentStatus.MOISTURE_SENSITIVE,
                        summary="台基承载木塔整体荷载，南向踏跺与前缘位置存在渗水返碱迹象。",
                        last_inspection_at=_dt("2026-03-10T14:20:00+08:00"),
                        node_ids=["site-ground", "foundation-octagon", "foundation-upper", "south-stair"],
                        focus_point=(0, 1.15, 4.8),
                        metrics=[
                            TwinMetricRecord(key="last_patrol_hours", label="最近巡检", value_number=48, unit=" 小时内"),
                            TwinMetricRecord(key="monitoring_type", label="监测类型", value_text="湿度 / 沉降"),
                            TwinMetricRecord(key="risk_band", label="风险等级", value_text="II 级"),
                        ],
                        related_damage_ids=["damage-platform-seepage"],
                    ),
                    TwinComponentRecord(
                        id="component-body",
                        name="五层八角塔身",
                        category="主体",
                        material="木构楼阁式结构",
                        risk_level=TwinRiskLevel.MEDIUM,
                        status=TwinComponentStatus.WEATHERING_ATTENTION,
                        summary="塔身按五层八角构件拆分，外立面彩画和围护构件按层归档。",
                        last_inspection_at=_dt("2026-03-11T09:05:00+08:00"),
                        node_ids=[
                            "floor-1-body",
                            "floor-2-body",
                            "floor-3-body",
                            "floor-4-body",
                            "floor-5-body",
                            "floor-1-balcony",
                            "floor-2-balcony",
                            "floor-3-balcony",
                            "floor-4-balcony",
                            "floor-5-balcony",
                        ],
                        focus_point=(0, 6.2, 0),
                        metrics=[
                            TwinMetricRecord(key="archive_code", label="档案编号", value_text="GJ-TWIN-01"),
                            TwinMetricRecord(key="component_group", label="构件类别", value_text="围护 / 彩画"),
                            TwinMetricRecord(key="damage_total", label="病害数量", value_number=1, unit=" 处"),
                        ],
                        related_damage_ids=["damage-paint-weathering"],
                    ),
                    TwinComponentRecord(
                        id="component-roof",
                        name="五层出檐屋面",
                        category="屋面",
                        material="木基层 + 筒瓦",
                        risk_level=TwinRiskLevel.HIGH,
                        status=TwinComponentStatus.TILE_DISPLACEMENT,
                        summary="屋面节点按各层出檐拆分，重点关注上层瓦件位移和檐口排水。",
                        last_inspection_at=_dt("2026-03-11T11:40:00+08:00"),
                        node_ids=[
                            "floor-1-eave",
                            "floor-2-eave",
                            "floor-3-eave",
                            "floor-4-eave",
                            "floor-5-eave",
                            "spire-base",
                            "spire-body",
                        ],
                        focus_point=(0, 9.8, 0),
                        metrics=[
                            TwinMetricRecord(key="roof_layers", label="屋面层数", value_text="5 层出檐"),
                            TwinMetricRecord(key="alert_source", label="预警来源", value_text="无人机巡检"),
                            TwinMetricRecord(key="risk_band", label="风险等级", value_text="III 级"),
                        ],
                        related_damage_ids=["damage-roof-shift"],
                    ),
                    TwinComponentRecord(
                        id="component-pillar-east",
                        name="东南外檐柱组",
                        category="柱体",
                        material="木柱",
                        risk_level=TwinRiskLevel.HIGH,
                        status=TwinComponentStatus.CRACK_WARNING,
                        summary="东南向外檐柱组已归集裂缝与含水率复核记录，是当前重点复核构件。",
                        last_inspection_at=_dt("2026-03-11T08:10:00+08:00"),
                        node_ids=["pillar-east-front", "pillar-east-back", "pillar-south"],
                        focus_point=(4.4, 4.8, 5.7),
                        metrics=[
                            TwinMetricRecord(key="moisture_rate", label="材质含水率", value_number=18.4, unit="%", precision=1),
                            TwinMetricRecord(key="crack_width", label="裂缝宽度", value_number=3.2, unit=" mm", precision=1),
                            TwinMetricRecord(key="risk_band", label="风险等级", value_text="III 级"),
                        ],
                        related_damage_ids=["damage-east-pillar-crack"],
                    ),
                    TwinComponentRecord(
                        id="component-pillar-west",
                        name="西北外檐柱组",
                        category="柱体",
                        material="木柱",
                        risk_level=TwinRiskLevel.LOW,
                        status=TwinComponentStatus.STABLE,
                        summary="西北向外檐柱组作为对照构件保留在档案中，当前监测状态稳定。",
                        last_inspection_at=_dt("2026-03-09T16:30:00+08:00"),
                        node_ids=["pillar-west-front", "pillar-west-back", "pillar-north"],
                        focus_point=(-4.8, 4.8, -5.7),
                        metrics=[
                            TwinMetricRecord(key="monitoring_frequency", label="监测频率", value_text="每周一次"),
                            TwinMetricRecord(key="tilt_angle", label="当前倾角", value_number=0.3, unit="°", precision=1),
                            TwinMetricRecord(key="risk_band", label="风险等级", value_text="I 级"),
                        ],
                        related_damage_ids=[],
                    ),
                ],
                damage_points=[
                    TwinDamagePointRecord(
                        id="damage-east-pillar-crack",
                        name="东南外檐柱纵向裂缝",
                        component_id="component-pillar-east",
                        type="裂缝",
                        risk_level=TwinRiskLevel.HIGH,
                        severity_score=0.92,
                        status=TwinDamageStatus.PENDING_REVIEW,
                        description="柱身迎风面出现纵向裂缝候选区域，当前以高风险热点展示并联动柱组档案。",
                        suggestion="建议补拍近景并结合含水率复核，再决定是否进入灌注修补工单。",
                        position=(5.95, 5.9, 5.95),
                        anchor_node_id="pillar-east-front",
                        inspected_at=_dt("2026-03-11T08:16:00+08:00"),
                    ),
                    TwinDamagePointRecord(
                        id="damage-roof-shift",
                        name="上层檐口瓦件位移",
                        component_id="component-roof",
                        type="松动",
                        risk_level=TwinRiskLevel.HIGH,
                        severity_score=0.87,
                        status=TwinDamageStatus.ALERTING,
                        description="四层檐口转折位置检测到瓦件滑移，需要结合无人机测量坐标与天气数据判断位移趋势。",
                        suggestion="建议叠加近 72 小时风雨数据，确认是否需要立即设置封控半径。",
                        position=(4.8, 9.35, 4.8),
                        anchor_node_id="floor-4-eave",
                        inspected_at=_dt("2026-03-11T11:43:00+08:00"),
                    ),
                    TwinDamagePointRecord(
                        id="damage-platform-seepage",
                        name="台基前缘渗水",
                        component_id="component-platform",
                        type="渗水",
                        risk_level=TwinRiskLevel.MEDIUM,
                        severity_score=0.71,
                        status=TwinDamageStatus.MONITORING,
                        description="台基南侧出现返碱与潮湿带，可与环境传感器数据做时间序列对齐。",
                        suggestion="建议先核查排水路径，并保留病害点与环境监测点的一一映射。",
                        position=(0, 1.18, 8.1),
                        anchor_node_id="foundation-upper",
                        inspected_at=_dt("2026-03-10T14:25:00+08:00"),
                    ),
                    TwinDamagePointRecord(
                        id="damage-paint-weathering",
                        name="塔身彩画风化",
                        component_id="component-body",
                        type="风化",
                        risk_level=TwinRiskLevel.MEDIUM,
                        severity_score=0.64,
                        status=TwinDamageStatus.NEEDS_CAPTURE,
                        description="二层外檐彩画局部褪色，已归入五层八角塔身构件档案。",
                        suggestion="建议补充多光谱图像，并记录构件表面位置与贴图坐标。",
                        position=(-4.65, 5.25, 5.8),
                        anchor_node_id="floor-2-body",
                        inspected_at=_dt("2026-03-11T09:18:00+08:00"),
                    ),
                ],
                default_damage_id="damage-east-pillar-crack",
            )
        }
    )
