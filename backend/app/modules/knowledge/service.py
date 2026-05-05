from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db_session
from backend.app.modules.detection.repository import DetectionBatchRepository
from backend.app.modules.detection.schemas import DetectionPageResultRecord, DetectionSeverity
from backend.app.modules.knowledge.sample_data import build_knowledge_page_payload
from backend.app.modules.knowledge.schemas import KnowledgePagePayload, KnowledgeRecommendation, KnowledgeReference


RULEBOOK: dict[str, tuple[str, str, str, list[KnowledgeReference]]] = {
    "木构裂缝": (
        "木构裂缝复核与干预原则",
        "木构裂缝复核清单",
        "优先完成近景补拍、裂缝宽度复测、含水率复测和端部状态记录。",
        [
            KnowledgeReference(
                title="全国文物保护标准目录",
                url="https://www.ncha.gov.cn/col/col2422/index.html",
                excerpt="先核查现行文物保护工程相关标准，再结合现场复核数据制定处理方案。",
            ),
            KnowledgeReference(
                title="中国文化遗产研究院",
                url="https://www.cach.org.cn/",
                excerpt="木构病害处理应结合材料状态、历史修缮信息和现场复核结果综合判断。",
            ),
        ],
    ),
    "瓦件位移": (
        "塔檐瓦件位移复核规则",
        "瓦件位移复核清单",
        "建议补拍无人机近景，标注位移边界，并评估临时围控范围。",
        [
            KnowledgeReference(
                title="全国文物保护标准目录",
                url="https://www.ncha.gov.cn/col/col2422/index.html",
                excerpt="瓦作修缮需先确认病害范围、构造关系和安全影响，再确定处置方式。",
            ),
            KnowledgeReference(
                title="国家文物局",
                url="https://www.ncha.gov.cn/",
                excerpt="对高处构件和开放区域风险，应同步考虑文物安全、作业安全和参观秩序。",
            ),
        ],
    ),
    "彩画褪色": (
        "彩画风化补采与材料复核规则",
        "彩画病害补采清单",
        "建议补采多光谱图像并联动历史修缮记录，不直接进入施工。",
        [
            KnowledgeReference(
                title="中国文化遗产研究院资料入口",
                url="https://www.cach.org.cn/",
                excerpt="彩画表层病害需结合颜料层、基底和历史修缮记录综合判断，避免只凭可见光照片定性。",
            ),
            KnowledgeReference(
                title="彩画病害补采清单",
                url="https://www.ncha.gov.cn/",
                excerpt="建议补采多光谱图像，记录光照条件，并对比历史照片确认褪色边界是否稳定。",
            ),
        ],
    ),
    "default": (
        "台基渗水与排水路径诊断规则",
        "台基渗水排查清单",
        "建议先完成降雨回看、返碱边界记录和排水路径核查，再决定处置方式。",
        [
            KnowledgeReference(
                title="全国文物保护标准目录",
                url="https://www.ncha.gov.cn/col/col2422/index.html",
                excerpt="砖石、台基和排水类问题应结合降雨、地表径流和返碱边界变化进行综合诊断。",
            ),
            KnowledgeReference(
                title="台基渗水与排水路径诊断规则",
                url="https://www.ncha.gov.cn/",
                excerpt="若源头未查清，不应先做大面积表层修补，应优先排查排水坡向和积水路径。",
            ),
        ],
    ),
}


class KnowledgePageService:
    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    def get_page_payload(self) -> KnowledgePagePayload:
        payload = build_knowledge_page_payload()
        payload.knowledge_recommendations = self.list_recommendations(limit=4)
        return payload

    def list_recommendations(self, *, limit: int = 4) -> list[KnowledgeRecommendation]:
        if self._session is None:
            return []

        repository = DetectionBatchRepository(self._session)
        work_orders = {item.result_id: item for item in repository.list_work_orders(limit=50)}
        return [
            self._build_recommendation(record, work_orders.get(record.result_id))
            for record in repository.list_page_results(limit=limit)
        ]

    @staticmethod
    def _build_recommendation(
        record: DetectionPageResultRecord,
        work_order,
    ) -> KnowledgeRecommendation:
        standard, checklist, action, references = RULEBOOK.get(record.damage_type_name, RULEBOOK["default"])
        severity_label = {
            DetectionSeverity.HIGH: "高风险",
            DetectionSeverity.MEDIUM: "中风险",
            DetectionSeverity.LOW: "低风险",
        }[record.severity]

        return KnowledgeRecommendation(
            result_id=record.result_id,
            title=record.title,
            severity=severity_label,
            trigger_reason=f"{record.component_name} · {record.damage_type_name} · {record.location_text}",
            suggested_standard=standard,
            recommended_action=action,
            checklist_title=checklist,
            work_order_status=work_order.status if work_order is not None else "未转工单",
            references=references,
        )


def get_knowledge_page_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> KnowledgePageService:
    return KnowledgePageService(session=session)
