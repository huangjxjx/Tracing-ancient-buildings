export type Metric = {
  label: string;
  value: string;
  note: string;
};

export type ArchiveNode = {
  name: string;
  state: string;
  risk: string;
  update: string;
};

export type Ranking = {
  name: string;
  value: number;
};

export type RegionalHealth = {
  region: string;
  status: string;
  value: string;
};

export type WorkOrder = {
  stage: string;
  done: number;
  total: number;
};

export type OverviewBriefing = {
  title: string;
  summary: string;
  status: string;
};

export type CoordinationEvent = {
  title: string;
  module: string;
  time: string;
  detail: string;
};

export const heroMetrics: Metric[] = [
  { label: "接入古建", value: "128", note: "覆盖祠堂、古塔、牌坊与传统民居等巡检对象" },
  { label: "累计病害识别", value: "3,426", note: "裂缝、腐朽、脱落、渗水等结果持续归档" },
  { label: "修缮建议生成", value: "864", note: "结合规范条文、历史档案与环境条件形成建议" },
  { label: "高风险预警", value: "19", note: "近 72 小时内需要人工复核的重点问题" }
];

export const archiveNodes: ArchiveNode[] = [
  { name: "东侧檐柱", state: "中度裂缝", risk: "III 级", update: "2 小时前复测" },
  { name: "抱梁节点", state: "轻微倾斜", risk: "I 级", update: "昨日更新" },
  { name: "西南斗拱", state: "局部腐朽", risk: "II 级", update: "待修缮决策" },
  { name: "正脊彩画", state: "颜料褪色", risk: "III 级", update: "已进入监测计划" }
];

export const issueRanking: Ranking[] = [
  { name: "木构裂缝", value: 86 },
  { name: "砖石剥蚀", value: 73 },
  { name: "构件倾斜", value: 61 },
  { name: "彩画褪色", value: 47 },
  { name: "瓦件松动", value: 35 }
];

export const regionalHealth: RegionalHealth[] = [
  { region: "华北监测区", status: "高压运行", value: "17 处高风险点待复核" },
  { region: "江南监测区", status: "稳定", value: "巡检完成率 92%" },
  { region: "西南监测区", status: "关注", value: "湿度增幅 12%" },
  { region: "西北监测区", status: "稳定", value: "风化病害占比上升" }
];

export const workOrders: WorkOrder[] = [
  { stage: "图像入库", done: 128, total: 128 },
  { stage: "AI 识别", done: 117, total: 128 },
  { stage: "专家复核", done: 64, total: 128 },
  { stage: "修缮立项", done: 19, total: 128 }
];

export const overviewBriefings: OverviewBriefing[] = [
  {
    title: "高风险木构复核进入快车道",
    summary: "华北监测区新增 3 处柱体裂缝复测任务，检测结果已同步到数字孪生点位。",
    status: "病害识别已回写"
  },
  {
    title: "修缮智库完成新一轮策略沉淀",
    summary: "新增湿热环境彩画保护与台基排水诊断条目，可直接服务工单决策。",
    status: "策略库持续扩容"
  },
  {
    title: "区域大屏联动现场调度",
    summary: "江南监测区排水核查任务已转入现场执行，工单推进与队伍调度状态实时同步。",
    status: "联动链路在线"
  }
];

export const coordinationEvents: CoordinationEvent[] = [
  {
    time: "09:20",
    module: "病害检测",
    title: "东侧檐柱批次完成识别",
    detail: "本批次生成 3 条候选结果，其中 1 条高风险裂缝已进入人工复核。"
  },
  {
    time: "10:05",
    module: "数字孪生",
    title: "高风险点位同步到构件档案",
    detail: "东侧檐柱、屋面瓦件与台基渗水点已完成场景锚定和档案联动。"
  },
  {
    time: "11:30",
    module: "修缮智库",
    title: "生成排水与裂缝处置建议",
    detail: "根据构件材质、病害等级和环境条件输出复核建议与修缮路径。"
  },
  {
    time: "13:15",
    module: "区域态势",
    title: "江南监测区进入重点关注",
    detail: "连续降雨触发台基返碱预警，现场调度已升级为跨组联动模式。"
  }
];
