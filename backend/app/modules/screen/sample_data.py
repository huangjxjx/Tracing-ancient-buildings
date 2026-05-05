from backend.app.modules.screen.schemas import (
    ScreenAlert,
    ScreenCommandNote,
    ScreenCoverageRegion,
    ScreenDispatch,
    ScreenEvent,
    ScreenIssue,
    ScreenMetric,
    ScreenPagePayload,
    ScreenRegionDetail,
    ScreenWorkOrderStage,
)


def build_screen_page_payload() -> ScreenPagePayload:
    return ScreenPagePayload(
        screen_metrics=[
            ScreenMetric(label="监管对象", value="1", delta="应县木塔单体档案"),
            ScreenMetric(label="重点病害", value="4", delta="2 项处于高风险关注"),
            ScreenMetric(label="片区完成率", value="91%", delta="佛宫寺片区巡查任务"),
            ScreenMetric(label="处置事项", value="7", delta="3 项进入现场复核"),
        ],
        screen_command_notes=[
            ScreenCommandNote(
                label="监管范围",
                value="山西省朔州市应县佛宫寺片区",
                detail="范围覆盖木塔本体、核心保护范围、建设控制地带和周边排水汇水区。",
            ),
            ScreenCommandNote(
                label="优先事项",
                value="木构裂缝与塔檐瓦件位移",
                detail="高风险病害需要当天完成近景补拍、现场复核和处置意见确认。",
            ),
            ScreenCommandNote(
                label="联动链路",
                value="检测 -> 档案 -> 知识 -> 监管",
                detail="病害档案生成后自动进入数字档案和知识推荐，监管页同步任务进度。",
            ),
        ],
        screen_coverage_regions=[
            ScreenCoverageRegion(
                region="佛宫寺核心保护范围",
                health_index=66,
                connected_sites=1,
                high_risk_count=2,
                work_order_progress=74,
                status="critical",
            ),
            ScreenCoverageRegion(
                region="木塔本体缓冲巡查区",
                health_index=78,
                connected_sites=1,
                high_risk_count=1,
                work_order_progress=68,
                status="watch",
            ),
            ScreenCoverageRegion(
                region="周边排水汇水区",
                health_index=81,
                connected_sites=1,
                high_risk_count=1,
                work_order_progress=58,
                status="watch",
            ),
            ScreenCoverageRegion(
                region="游客通行与临时围控区",
                health_index=89,
                connected_sites=1,
                high_risk_count=0,
                work_order_progress=92,
                status="stable",
            ),
        ],
        screen_issues_top5=[
            ScreenIssue(label="木构裂缝", value=92, count="1 处高风险"),
            ScreenIssue(label="瓦件位移", value=84, count="1 处高风险"),
            ScreenIssue(label="台基渗水", value=68, count="1 处中风险"),
            ScreenIssue(label="彩画风化", value=57, count="1 处中风险"),
            ScreenIssue(label="构件倾斜", value=41, count="持续观测"),
        ],
        screen_work_order_stages=[
            ScreenWorkOrderStage(stage="影像入库", done=18, total=18, note="地面照片和无人机影像均已归档"),
            ScreenWorkOrderStage(stage="病害识别", done=18, total=18, note="识别结果已生成病害档案"),
            ScreenWorkOrderStage(stage="现场复核", done=11, total=18, note="高风险点位优先完成"),
            ScreenWorkOrderStage(stage="处置回写", done=3, total=4, note="复核意见同步到数字档案"),
        ],
        screen_alerts=[
            ScreenAlert(
                title="东南外槽柱纵向裂缝",
                region="佛宫寺核心保护范围",
                severity="high",
                detail="裂缝宽度达到高风险阈值，需复测含水率并确认裂缝端部是否继续发展。",
            ),
            ScreenAlert(
                title="上层塔檐瓦件位移",
                region="木塔本体缓冲巡查区",
                severity="high",
                detail="无人机影像显示局部瓦件滑移，需复核位移趋势并评估临时围控范围。",
            ),
            ScreenAlert(
                title="南侧台基前缘渗水返碱",
                region="周边排水汇水区",
                severity="medium",
                detail="台基前缘潮湿带扩大，需核查排水坡向、地表径流和近期降雨记录。",
            ),
            ScreenAlert(
                title="二层外檐彩画风化",
                region="佛宫寺核心保护范围",
                severity="medium",
                detail="表层褪色边界需要补充多光谱影像，并与历史照片进行对比判读。",
            ),
        ],
        screen_dispatches=[
            ScreenDispatch(team="木构复核组", region="佛宫寺核心保护范围", mission="外槽柱裂缝近景补拍与含水率复测", progress=82),
            ScreenDispatch(team="无人机巡检组", region="木塔本体缓冲巡查区", mission="上层塔檐瓦件位移复核", progress=76),
            ScreenDispatch(team="环境排水组", region="周边排水汇水区", mission="台基排水路径核查", progress=58),
            ScreenDispatch(team="彩画保护组", region="佛宫寺核心保护范围", mission="彩画风化补充影像采集", progress=43),
        ],
        screen_region_details=[
            ScreenRegionDetail(
                region="佛宫寺核心保护范围",
                commander_window="09:00 - 18:00 重点巡查",
                response_mode="高风险优先复核",
                focus="木构裂缝、瓦件位移、彩画风化",
                next_action="完成东南外槽柱近景补拍和含水率复测，形成是否进入修补工序的复核意见。",
            ),
            ScreenRegionDetail(
                region="周边排水汇水区",
                commander_window="降雨后 24 小时内复查",
                response_mode="排水联动",
                focus="台基渗水、返碱边界、地表径流",
                next_action="核查台基前缘排水路径，必要时形成临时导排和观察点布设方案。",
            ),
            ScreenRegionDetail(
                region="游客通行与临时围控区",
                commander_window="开放时段巡查",
                response_mode="秩序与安全协同",
                focus="高风险点位周边通行秩序",
                next_action="根据瓦件位移复核结果调整临时围控范围和巡查频次。",
            ),
        ],
        screen_events=[
            ScreenEvent(
                time="09:10",
                type="识别",
                title="东南外槽柱新增高风险裂缝档案",
                detail="检测结果已同步到数字档案、知识推荐和监管告警。",
            ),
            ScreenEvent(
                time="10:40",
                type="调度",
                title="无人机巡检组接收上层塔檐复核任务",
                detail="任务目标为确认瓦件位移范围和近期变化趋势。",
            ),
            ScreenEvent(
                time="12:05",
                type="知识",
                title="知识页生成木构裂缝复核清单",
                detail="清单包含裂缝活性、含水率、端部状态和历史修缮记录核查。",
            ),
            ScreenEvent(
                time="14:30",
                type="工单",
                title="台基渗水核查进入现场执行",
                detail="环境排水组开始核查排水坡向、积水点和返碱边界。",
            ),
        ],
    )
