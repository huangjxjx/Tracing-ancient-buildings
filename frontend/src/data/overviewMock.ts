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

export type OverviewSignal = {
  title: string;
  detail: string;
  tag: string;
};

export type OverviewTimeline = {
  time: string;
  title: string;
  detail: string;
};

export const heroMetrics: Metric[] = [
  {
    label: "接入古建",
    value: "128",
    note: "覆盖祠堂、古塔、牌坊与传统民居等多类巡检对象"
  },
  {
    label: "累计病害识别",
    value: "3,426",
    note: "裂缝、剥蚀、松动、渗水等识别结果持续归档"
  },
  {
    label: "修缮建议生成",
    value: "864",
    note: "结合规范条文、历史案例和环境条件形成处置建议"
  },
  {
    label: "高风险预警",
    value: "19",
    note: "近 72 小时内需要优先复核并推进现场核查"
  }
];

export const overviewSignals: OverviewSignal[] = [
  {
    title: "病害识别到修缮建议",
    detail: "检测结果已可直达修缮智库，复核时可同步查看策略映射。",
    tag: "闭环提速"
  },
  {
    title: "数字孪生定位风险点",
    detail: "构件和病害点位双向联动，便于定位高风险部位与历史记录。",
    tag: "空间感知"
  },
  {
    title: "区域态势实时聚合",
    detail: "大屏聚合重点预警、资源负载和队伍执行进度，支持跨区域比较。",
    tag: "总控调度"
  }
];

export const archiveNodes: ArchiveNode[] = [
  { name: "东侧檐柱", state: "中度纵向裂缝", risk: "III 级", update: "2 小时前复测" },
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

export const overviewTimeline: OverviewTimeline[] = [
  {
    time: "09:20",
    title: "华北监测区预警升级",
    detail: "屋面瓦件位移风险上升，已推送至态势大屏和病害复核队列。"
  },
  {
    time: "11:05",
    title: "东侧檐柱完成复测",
    detail: "识别结果已回写数字孪生点位，并同步打开修缮策略映射。"
  },
  {
    time: "14:30",
    title: "江南监测区排水排查中",
    detail: "现场队伍已接单，预计 2 小时后补充环境监测数据。"
  }
];
