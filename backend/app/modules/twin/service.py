from __future__ import annotations

from datetime import datetime
from typing import Annotated, Protocol
from zoneinfo import ZoneInfo

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db_session
from backend.app.modules.detection.repository import DetectionBatchRepository
from backend.app.modules.detection.schemas import DetectionPageResultRecord, DetectionReviewWritebackRecord, DetectionSeverity
from backend.app.modules.twin.sample_data import build_twin_sample_dataset
from backend.app.modules.twin.schemas import (
    TwinComponentCard,
    TwinComponentRecord,
    TwinComponentStatus,
    TwinDamagePointCard,
    TwinDamagePointRecord,
    TwinDamageStatus,
    TwinMetricCard,
    TwinMetricRecord,
    TwinPagePayload,
    TwinRiskLevel,
    TwinSceneNodeRecord,
    TwinScenePrimitive,
    TwinSampleDataset,
    TwinSiteRecord,
    TwinSiteSnapshotRecord,
)

DISPLAY_TIMEZONE = ZoneInfo("Asia/Shanghai")


class TwinSiteNotFoundError(LookupError):
    def __init__(self, site_id: str) -> None:
        self.site_id = site_id
        super().__init__(f"Unknown twin site: {site_id}")


class TwinDataIntegrityError(RuntimeError):
    pass


class TwinDataProvider(Protocol):
    def get_site_snapshot(self, site_id: str) -> TwinSiteSnapshotRecord | None: ...


class StaticTwinDataProvider:
    def __init__(self, dataset: TwinSampleDataset | None = None) -> None:
        self._dataset = dataset or build_twin_sample_dataset()

    def get_site_snapshot(self, site_id: str) -> TwinSiteSnapshotRecord | None:
        return self._dataset.snapshots.get(site_id)


class TwinPageService:
    def __init__(self, provider: TwinDataProvider | None = None, session: Session | None = None) -> None:
        self._provider = provider or StaticTwinDataProvider()
        self._session = session

    def get_page_payload(self, site_id: str) -> TwinPagePayload:
        snapshot = self._provider.get_site_snapshot(site_id)
        if snapshot is None:
            dynamic_payload = self._build_detection_archive_payload(site_id)
            if dynamic_payload is not None:
                return dynamic_payload
            raise TwinSiteNotFoundError(site_id)

        self._validate_snapshot(snapshot)
        payload = TwinPagePayload(
            site=snapshot.site,
            scene_nodes=snapshot.scene_nodes,
            components=[self._build_component_card(component) for component in snapshot.components],
            damage_points=[self._build_damage_card(damage) for damage in snapshot.damage_points],
            default_damage_id=snapshot.default_damage_id,
        )
        self._apply_detection_results(payload)
        self._apply_review_writebacks(payload)
        return payload

    def _build_detection_archive_payload(self, site_id: str) -> TwinPagePayload | None:
        if self._session is None:
            return None

        results = [
            result
            for result in DetectionBatchRepository(self._session).list_page_results(limit=100)
            if result.site_id == site_id
        ]
        if not results:
            return None

        component_ids = list(dict.fromkeys(result.component_id for result in results))
        components: list[TwinComponentCard] = []
        scene_nodes: list[TwinSceneNodeRecord] = []
        damage_points: list[TwinDamagePointCard] = []
        severity_score_map = {
            DetectionSeverity.HIGH: 0.91,
            DetectionSeverity.MEDIUM: 0.72,
            DetectionSeverity.LOW: 0.48,
        }
        risk_level_map = {
            DetectionSeverity.HIGH: TwinRiskLevel.HIGH,
            DetectionSeverity.MEDIUM: TwinRiskLevel.MEDIUM,
            DetectionSeverity.LOW: TwinRiskLevel.LOW,
        }

        for index, component_id in enumerate(component_ids):
            component_results = [result for result in results if result.component_id == component_id]
            highest_severity = max(component_results, key=lambda item: severity_score_map[item.severity]).severity
            node_id = f"{component_id}_archive_node"
            position = (float(index * 3), 0.0, 0.0)
            scene_nodes.append(
                TwinSceneNodeRecord(
                    id=node_id,
                    label=component_results[0].component_name,
                    primitive=TwinScenePrimitive.BOX,
                    size=(1.6, 2.2, 0.8),
                    position=position,
                    color="#d6a15f",
                    wire_color="#8a5a2b",
                    roughness=0.7,
                )
            )
            components.append(
                TwinComponentCard(
                    id=component_id,
                    name=component_results[0].component_name,
                    category="检测生成构件档案",
                    material="待现场复核",
                    risk_level=risk_level_map[highest_severity],
                    status="检测生成",
                    summary=f"由 {len(component_results)} 条病害档案自动生成，来自上传图片检测结果。",
                    last_inspection=self._format_display_time(max(result.detected_at for result in component_results)),
                    node_ids=[node_id],
                    focus_point=position,
                    metrics=[
                        TwinMetricCard(label="病害档案", value=str(len(component_results))),
                        TwinMetricCard(label="最高风险", value=self._severity_label(highest_severity)),
                    ],
                    related_damage_ids=[result.result_id for result in component_results],
                )
            )

        component_focus = {component.id: component.focus_point for component in components}
        component_node = {component.id: component.node_ids[0] for component in components}
        for result in results:
            damage_points.append(
                TwinDamagePointCard(
                    id=result.result_id,
                    name=result.title,
                    component_id=result.component_id,
                    type=result.damage_type_name,
                    risk_level=risk_level_map[result.severity],
                    severity_score=severity_score_map[result.severity],
                    status=result.review_status,
                    description=result.location_text,
                    suggestion=result.suggestion,
                    position=component_focus[result.component_id],
                    anchor_node_id=component_node[result.component_id],
                    inspected_at=self._format_display_time(result.detected_at),
                )
            )

        return TwinPagePayload(
            site=TwinSiteRecord(
                id=site_id,
                name=site_id,
                region_name="上传检测生成档案",
                scene_version="detection-generated-v1",
                model_asset_key=None,
                coordinate_reference="local-upload",
            ),
            scene_nodes=scene_nodes,
            components=components,
            damage_points=damage_points,
            default_damage_id=damage_points[0].id if damage_points else None,
        )

    def _apply_detection_results(self, payload: TwinPagePayload) -> None:
        if self._session is None:
            return

        existing_ids = {damage.id for damage in payload.damage_points}
        components = {component.id: component for component in payload.components}
        for result in DetectionBatchRepository(self._session).list_page_results(limit=4):
            if result.site_id != payload.site.id or result.result_id in existing_ids:
                continue

            component = components.get(result.component_id)
            if component is None:
                continue

            payload.damage_points.append(self._build_detection_damage_card(result, component))
            existing_ids.add(result.result_id)

    def _apply_review_writebacks(self, payload: TwinPagePayload) -> None:
        if self._session is None:
            return

        existing_ids = {damage.id for damage in payload.damage_points}
        components = {component.id: component for component in payload.components}
        for writeback in DetectionBatchRepository(self._session).list_review_writebacks(limit=4):
            if writeback.site_id != payload.site.id or writeback.result_id in existing_ids:
                continue

            component = components.get(writeback.component_id)
            if component is None:
                continue

            payload.damage_points.append(self._build_review_damage_card(writeback, component))
            existing_ids.add(writeback.result_id)

    @staticmethod
    def _validate_snapshot(snapshot: TwinSiteSnapshotRecord) -> None:
        node_ids = {node.id for node in snapshot.scene_nodes}
        components_by_id = {component.id: component for component in snapshot.components}
        damages_by_id = {damage.id: damage for damage in snapshot.damage_points}

        for component in snapshot.components:
            missing_node_ids = [node_id for node_id in component.node_ids if node_id not in node_ids]
            if missing_node_ids:
                raise TwinDataIntegrityError(
                    f"Component {component.id} references missing scene nodes: {', '.join(missing_node_ids)}"
                )

            missing_damage_ids = [damage_id for damage_id in component.related_damage_ids if damage_id not in damages_by_id]
            if missing_damage_ids:
                raise TwinDataIntegrityError(
                    f"Component {component.id} references missing damage points: {', '.join(missing_damage_ids)}"
                )

            mismatched_damage_ids = [
                damage_id
                for damage_id in component.related_damage_ids
                if damages_by_id[damage_id].component_id != component.id
            ]
            if mismatched_damage_ids:
                raise TwinDataIntegrityError(
                    f"Component {component.id} has damage bindings owned by another component: "
                    f"{', '.join(mismatched_damage_ids)}"
                )

        for damage in snapshot.damage_points:
            component = components_by_id.get(damage.component_id)
            if component is None:
                raise TwinDataIntegrityError(
                    f"Damage point {damage.id} references missing component: {damage.component_id}"
                )

            if damage.anchor_node_id not in node_ids:
                raise TwinDataIntegrityError(
                    f"Damage point {damage.id} references missing anchor node: {damage.anchor_node_id}"
                )

            if damage.anchor_node_id not in component.node_ids:
                raise TwinDataIntegrityError(
                    f"Damage point {damage.id} is anchored to node {damage.anchor_node_id} outside component "
                    f"{component.id}"
                )

        if snapshot.default_damage_id and snapshot.default_damage_id not in damages_by_id:
            raise TwinDataIntegrityError(
                f"Default damage id {snapshot.default_damage_id} does not exist in the damage point list"
            )

    @staticmethod
    def _severity_label(severity: DetectionSeverity) -> str:
        return {
            DetectionSeverity.HIGH: "高风险",
            DetectionSeverity.MEDIUM: "中风险",
            DetectionSeverity.LOW: "低风险",
        }[severity]

    @staticmethod
    def _build_component_card(record: TwinComponentRecord) -> TwinComponentCard:
        status_map = {
            TwinComponentStatus.STABLE: "状态稳定",
            TwinComponentStatus.MOISTURE_SENSITIVE: "潮湿敏感",
            TwinComponentStatus.WEATHERING_ATTENTION: "彩画褪色",
            TwinComponentStatus.TILE_DISPLACEMENT: "瓦件松动",
            TwinComponentStatus.CRACK_WARNING: "纵向裂缝",
        }
        return TwinComponentCard(
            id=record.id,
            name=record.name,
            category=record.category,
            material=record.material,
            risk_level=record.risk_level,
            status=status_map[record.status],
            summary=record.summary,
            last_inspection=TwinPageService._format_display_time(record.last_inspection_at),
            node_ids=record.node_ids,
            focus_point=record.focus_point,
            metrics=[TwinMetricCard(label=metric.label, value=TwinPageService._format_metric(metric)) for metric in record.metrics],
            related_damage_ids=record.related_damage_ids,
        )

    @staticmethod
    def _build_damage_card(record: TwinDamagePointRecord) -> TwinDamagePointCard:
        status_map = {
            TwinDamageStatus.PENDING_REVIEW: "待复核",
            TwinDamageStatus.ALERTING: "预警中",
            TwinDamageStatus.MONITORING: "持续监测",
            TwinDamageStatus.NEEDS_CAPTURE: "待补采",
        }
        return TwinDamagePointCard(
            id=record.id,
            name=record.name,
            component_id=record.component_id,
            type=record.type,
            risk_level=record.risk_level,
            severity_score=record.severity_score,
            status=status_map[record.status],
            description=record.description,
            suggestion=record.suggestion,
            position=record.position,
            anchor_node_id=record.anchor_node_id,
            inspected_at=TwinPageService._format_display_time(record.inspected_at),
        )

    @staticmethod
    def _build_review_damage_card(
        record: DetectionReviewWritebackRecord,
        component: TwinComponentCard,
    ) -> TwinDamagePointCard:
        severity_score_map = {
            DetectionSeverity.HIGH: 0.91,
            DetectionSeverity.MEDIUM: 0.72,
            DetectionSeverity.LOW: 0.48,
        }
        risk_level_map = {
            DetectionSeverity.HIGH: TwinRiskLevel.HIGH,
            DetectionSeverity.MEDIUM: TwinRiskLevel.MEDIUM,
            DetectionSeverity.LOW: TwinRiskLevel.LOW,
        }
        return TwinDamagePointCard(
            id=record.result_id,
            name=record.title,
            component_id=record.component_id,
            type=record.damage_type_name,
            risk_level=risk_level_map[record.severity],
            severity_score=severity_score_map[record.severity],
            status=record.review_status,
            description=record.location_text,
            suggestion=record.suggestion,
            position=component.focus_point,
            anchor_node_id=component.node_ids[0],
            inspected_at=TwinPageService._format_display_time(record.reviewed_at),
        )

    @staticmethod
    def _build_detection_damage_card(
        record: DetectionPageResultRecord,
        component: TwinComponentCard,
    ) -> TwinDamagePointCard:
        severity_score_map = {
            DetectionSeverity.HIGH: 0.91,
            DetectionSeverity.MEDIUM: 0.72,
            DetectionSeverity.LOW: 0.48,
        }
        risk_level_map = {
            DetectionSeverity.HIGH: TwinRiskLevel.HIGH,
            DetectionSeverity.MEDIUM: TwinRiskLevel.MEDIUM,
            DetectionSeverity.LOW: TwinRiskLevel.LOW,
        }
        return TwinDamagePointCard(
            id=record.result_id,
            name=record.title,
            component_id=record.component_id,
            type=record.damage_type_name,
            risk_level=risk_level_map[record.severity],
            severity_score=severity_score_map[record.severity],
            status=record.review_status,
            description=record.location_text,
            suggestion=record.suggestion,
            position=component.focus_point,
            anchor_node_id=component.node_ids[0],
            inspected_at=TwinPageService._format_display_time(record.detected_at),
        )

    @staticmethod
    def _format_metric(metric: TwinMetricRecord) -> str:
        if metric.value_text is not None:
            return metric.value_text
        if metric.value_number is None:
            return ""

        if float(metric.value_number).is_integer():
            base_value = str(int(metric.value_number))
        else:
            base_value = f"{metric.value_number:.{metric.precision}f}"

        return f"{base_value}{metric.unit or ''}"

    @staticmethod
    def _format_display_time(value: datetime) -> str:
        return value.astimezone(DISPLAY_TIMEZONE).strftime("%Y-%m-%d %H:%M")


def get_twin_page_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> TwinPageService:
    return TwinPageService(session=session)
