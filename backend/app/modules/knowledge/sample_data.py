from backend.app.modules.knowledge.schemas import (
    KnowledgeCase,
    KnowledgeChecklist,
    KnowledgeExternalAction,
    KnowledgeMetric,
    KnowledgeOverviewCard,
    KnowledgePagePayload,
    KnowledgeQuestion,
    KnowledgeRouteAction,
    KnowledgeStandard,
    KnowledgeStrategy,
)


def build_knowledge_page_payload() -> KnowledgePagePayload:
    return KnowledgePagePayload(
        knowledge_metrics=[
            KnowledgeMetric(label="处理方法", value="12", note="围绕应县木塔木构、瓦作、台基和彩画病害组织"),
            KnowledgeMetric(label="参考资料", value="9", note="国家文物保护标准目录、研究机构资料和现场复核依据"),
            KnowledgeMetric(label="复核清单", value="4", note="可直接对应病害档案和现场处置任务"),
        ],
        knowledge_overview=[
            KnowledgeOverviewCard(
                highlight="档案联动",
                title="病害档案直达处理建议",
                summary="按病害类型、构件部位、风险等级和材料属性匹配复核清单、处理顺序和参考资料。",
                hint="适用于应县木塔上传照片检测完成后的档案复核。",
            ),
            KnowledgeOverviewCard(
                highlight="处置顺序",
                title="先复核，后修缮决策",
                summary="高风险木构裂缝和瓦件位移优先确认活性、位移趋势和环境诱因，再进入修缮方案。",
                hint="降低仅凭单张照片直接下结论的风险。",
            ),
            KnowledgeOverviewCard(
                highlight="资料依据",
                title="标准、案例和原始资料并列呈现",
                summary="每条建议都给出可追溯的参考来源，便于专家复核和现场队伍执行。",
                hint="参考资料以公开机构入口和标准目录为主。",
            ),
        ],
        knowledge_standards=[
            KnowledgeStandard(
                title="文物保护工程相关标准目录",
                category="标准目录",
                summary="用于核查木结构、瓦作、台基排水和彩画保护相关标准的适用范围。",
                update="国家文物局公开目录",
                applicable_to="木柱、塔檐、台基、彩画等文物建筑构件",
                checkpoints=["确认标准适用对象", "核查病害分级依据", "记录引用版本"],
            ),
            KnowledgeStandard(
                title="木构裂缝复核与干预原则",
                category="处理方法",
                summary="对柱身纵向裂缝先判断是否活动，再结合含水率、受力状态和历史修缮记录决定干预强度。",
                update="应县木塔档案规则",
                applicable_to="外槽柱、内槽柱、梁枋、斗栱裂缝",
                checkpoints=["裂缝宽度复测", "含水率复测", "端部状态记录", "历史裂缝对比"],
            ),
            KnowledgeStandard(
                title="塔檐瓦件位移复核规则",
                category="处理方法",
                summary="对瓦件滑移先复核位移范围、松动程度和天气影响，再决定临时围控与修整顺序。",
                update="应县木塔档案规则",
                applicable_to="五层六檐屋面、瓦件、屋脊转折部位",
                checkpoints=["无人机近景补拍", "位移边界标注", "风雨记录对照", "通行风险评估"],
            ),
            KnowledgeStandard(
                title="台基渗水与返碱排查规则",
                category="诊断方法",
                summary="对台基潮湿带和返碱边界先追踪水源，核查排水坡向、地表径流和近期降雨。",
                update="应县木塔档案规则",
                applicable_to="台基、散水、排水沟、周边汇水区",
                checkpoints=["降雨记录回看", "排水坡向核查", "返碱边界拍照", "环境点位复测"],
            ),
        ],
        knowledge_strategies=[
            KnowledgeStrategy(
                title="高风险木构裂缝",
                trigger="识别结果为木构裂缝，且裂缝宽度、位置或发展趋势达到高风险阈值。",
                response="当天完成近景补拍、裂缝宽度复测、含水率复测和端部状态记录。",
                deliverable="复核记录 + 临时控制建议 + 是否进入修补工序的意见",
                collaboration="联动图片检测、数字档案、木构复核组和监管告警。",
            ),
            KnowledgeStrategy(
                title="塔檐瓦件位移",
                trigger="无人机或地面照片识别到瓦件滑移、松动或局部错位。",
                response="先确认位移范围和趋势，再评估临时围控半径与修整时机。",
                deliverable="位移复核图 + 风险范围 + 现场处置建议",
                collaboration="联动无人机巡检组、监管页派工和数字档案点位。",
            ),
            KnowledgeStrategy(
                title="台基渗水返碱",
                trigger="台基前缘出现潮湿带、返碱边界扩大或雨后长时间不退。",
                response="优先核查排水路径和汇水原因，未确认水源前不做大面积表层修补。",
                deliverable="排水核查记录 + 环境复测清单 + 临时导排建议",
                collaboration="联动环境排水组和佛宫寺片区监管任务。",
            ),
        ],
        knowledge_cases=[
            KnowledgeCase(
                title="应县木塔东南外槽柱纵向裂缝复核",
                site="应县木塔（佛宫寺释迦塔）",
                issue="木构裂缝",
                symptom="柱身迎风面出现纵向裂缝，检测结果提示高风险。",
                diagnosis="需要先判断裂缝是否活动，并结合含水率、受力位置和历史记录综合判断。",
                method="近景补拍 + 裂缝宽度复测 + 含水率复测 + 端部状态记录",
                outcome="形成是否进入灌注、嵌补或持续观察的复核意见。",
                caution="未确认裂缝活性前，不宜直接进行不可逆修补。",
                tags=["木构", "裂缝", "高风险"],
            ),
            KnowledgeCase(
                title="应县木塔上层塔檐瓦件位移复核",
                site="应县木塔（佛宫寺释迦塔）",
                issue="瓦件位移",
                symptom="塔檐转折部位出现局部滑移，可能影响下方通行安全。",
                diagnosis="需结合无人机近景影像、风雨记录和瓦件松动程度判断趋势。",
                method="无人机补拍 + 位移边界标注 + 临时围控评估",
                outcome="确认是否需要立即修整或先扩大观察频次。",
                caution="现场处置前需评估高空作业和开放管理影响。",
                tags=["瓦作", "塔檐", "位移"],
            ),
            KnowledgeCase(
                title="应县木塔南侧台基渗水返碱排查",
                site="应县木塔（佛宫寺释迦塔）",
                issue="台基渗水",
                symptom="台基前缘出现潮湿带和返碱边界，雨后消退较慢。",
                diagnosis="重点排查排水坡向、地表径流和周边汇水条件。",
                method="排水路径核查 + 降雨记录对照 + 环境监测点补测",
                outcome="形成临时导排、持续监测或局部整治建议。",
                caution="水源未确认前，不宜先做大面积表面封闭。",
                tags=["台基", "排水", "返碱"],
            ),
        ],
        knowledge_checklists=[
            KnowledgeChecklist(
                title="木构裂缝复核清单",
                items=["复测裂缝宽度", "复测构件含水率", "记录裂缝端部状态", "对比历史照片和修缮记录"],
            ),
            KnowledgeChecklist(
                title="瓦件位移复核清单",
                items=["补拍无人机近景", "标注位移边界", "核查松动程度", "评估临时围控范围"],
            ),
            KnowledgeChecklist(
                title="台基渗水排查清单",
                items=["回看近 72 小时降雨", "核查排水坡向", "记录返碱边界", "比对环境监测数据"],
            ),
            KnowledgeChecklist(
                title="彩画风化补采清单",
                items=["补采多光谱图像", "记录光照条件", "对比历史照片", "确认是否进入样区试验"],
            ),
        ],
        knowledge_questions=[
            KnowledgeQuestion(
                question="木构裂缝识别为高风险后，第一步看什么？",
                answer="先确认裂缝是否活动、含水率是否异常、端部是否继续发展，再决定临时控制或修补路径。",
                recommendation="优先调用木构裂缝复核清单，并查看最近一次降雨、湿度和历史修缮记录。",
                references=["全国文物保护标准目录", "木构裂缝复核与干预原则"],
            ),
            KnowledgeQuestion(
                question="塔檐瓦件位移如何决定是否立即处置？",
                answer="看位移范围、松动程度、下方通行风险和近期风雨条件；趋势不明时先补拍和围控。",
                recommendation="优先生成无人机补拍任务，并在监管页同步临时围控事项。",
                references=["塔檐瓦件位移复核规则", "应县木塔构件档案"],
            ),
            KnowledgeQuestion(
                question="台基渗水为什么不能直接做表层修补？",
                answer="如果水源和排水路径没有查清，表层修补可能遮蔽问题并加重局部潮湿。",
                recommendation="先完成排水坡向、地表径流和返碱边界核查，再决定整治方式。",
                references=["台基渗水与返碱排查规则", "佛宫寺片区环境记录"],
            ),
        ],
        knowledge_actions=[
            KnowledgeRouteAction(kind="route", title="图片检测", entry_label="上传巡检照片", target="/damage-workspace"),
            KnowledgeRouteAction(kind="route", title="数字档案", entry_label="查看构件档案", target="/twin-workspace"),
            KnowledgeExternalAction(
                kind="external",
                title="国家文物局标准目录",
                entry_label="打开标准目录",
                target="https://www.ncha.gov.cn/col/col2422/index.html",
            ),
        ],
    )
