export type ScreenMetric = {
  label: string;
  value: string;
  delta: string;
};

export type ScreenCommandNote = {
  label: string;
  value: string;
  detail: string;
};

export type ScreenCoverageRegion = {
  region: string;
  healthIndex: number;
  connectedSites: number;
  highRiskCount: number;
  workOrderProgress: number;
  status: "critical" | "watch" | "stable";
};

export type ScreenIssue = {
  label: string;
  value: number;
  count: string;
};

export type ScreenWorkOrderStage = {
  stage: string;
  done: number;
  total: number;
  note: string;
};

export type ScreenAlert = {
  title: string;
  region: string;
  severity: "high" | "medium" | "low";
  detail: string;
};

export type ScreenDispatch = {
  team: string;
  region: string;
  mission: string;
  progress: number;
};

export type ScreenRegionDetail = {
  region: string;
  commanderWindow: string;
  responseMode: string;
  focus: string;
  nextAction: string;
};

export type ScreenEvent = {
  time: string;
  type: string;
  title: string;
  detail: string;
};

export const screenMetrics: ScreenMetric[] = [
  { label: "接入古建", value: "128", delta: "今日新增 4 处" },
  { label: "高风险预警", value: "19", delta: "7 项需 24 小时内处置" },
  { label: "区域接入率", value: "92%", delta: "西南片区补点中" },
  { label: "在途工单", value: "57", delta: "12 单已进入现场阶段" }
];

export const screenCommandNotes: ScreenCommandNote[] = [
  {
    label: "指挥关注",
    value: "华北木构裂缝",
    detail: "新增高风险点位集中在檐柱与屋面交界区域。"
  },
  {
    label: "联动节奏",
    value: "识别 -> 复核 -> 调度",
    detail: "病害批次结果已开始回写工单与区域大屏。"
  },
  {
    label: "响应窗口",
    value: "24 小时",
    detail: "高风险预警要求当天完成专家确认和现场排查。"
  }
];

export const screenCoverageRegions: ScreenCoverageRegion[] = [
  {
    region: "华北监测区",
    healthIndex: 68,
    connectedSites: 34,
    highRiskCount: 7,
    workOrderProgress: 76,
    status: "critical"
  },
  {
    region: "江南监测区",
    healthIndex: 74,
    connectedSites: 38,
    highRiskCount: 5,
    workOrderProgress: 64,
    status: "watch"
  },
  {
    region: "西南监测区",
    healthIndex: 79,
    connectedSites: 29,
    highRiskCount: 4,
    workOrderProgress: 58,
    status: "watch"
  },
  {
    region: "西北监测区",
    healthIndex: 87,
    connectedSites: 27,
    highRiskCount: 2,
    workOrderProgress: 81,
    status: "stable"
  }
];

export const screenIssuesTop5: ScreenIssue[] = [
  { label: "木构裂缝", value: 86, count: "214 处" },
  { label: "渗水返碱", value: 72, count: "173 处" },
  { label: "砖石剥蚀", value: 64, count: "149 处" },
  { label: "彩画褪色", value: 48, count: "103 处" },
  { label: "瓦件松动", value: 39, count: "88 处" }
];

export const screenWorkOrderStages: ScreenWorkOrderStage[] = [
  { stage: "预警入池", done: 57, total: 57, note: "全部已建立责任区域" },
  { stage: "人工复核", done: 41, total: 57, note: "高风险优先处理" },
  { stage: "现场执行", done: 29, total: 57, note: "跨区域任务 8 单" },
  { stage: "回写归档", done: 18, total: 57, note: "已同步智库和孪生" }
];

export const screenAlerts: ScreenAlert[] = [
  {
    title: "东南坡瓦件位移预警",
    region: "华北监测区",
    severity: "high",
    detail: "无人机复测显示位移趋势加快，建议优先围控并复核。"
  },
  {
    title: "台基前缘渗水范围扩大",
    region: "江南监测区",
    severity: "medium",
    detail: "连续降雨后返碱带扩展，建议同步检查排水路径。"
  },
  {
    title: "额枋彩画褪色需补采",
    region: "西南监测区",
    severity: "low",
    detail: "当前更适合补充多光谱样本，不建议直接施工。"
  }
];

export const screenDispatches: ScreenDispatch[] = [
  {
    team: "巡检一组",
    region: "华北监测区",
    mission: "屋面松动点位复核",
    progress: 82
  },
  {
    team: "环境二组",
    region: "江南监测区",
    mission: "台基排水路径排查",
    progress: 56
  },
  {
    team: "彩画专项组",
    region: "西南监测区",
    mission: "彩画褪色样本补采",
    progress: 43
  }
];

export const screenRegionDetails: ScreenRegionDetail[] = [
  {
    region: "华北监测区",
    commanderWindow: "09:00 - 18:00 高频轮巡",
    responseMode: "高风险快反",
    focus: "屋面瓦件位移、檐柱裂缝复测",
    nextAction: "优先完成无人机补拍与木构含水率复核，再决定封控半径。"
  },
  {
    region: "江南监测区",
    commanderWindow: "全天湿度监测值守",
    responseMode: "排水联动",
    focus: "台基返碱、渗水路径核查",
    nextAction: "同步排查排水路径与地表径流，必要时转入临时导排方案。"
  },
  {
    region: "西南监测区",
    commanderWindow: "11:00 - 20:00 彩画专班跟进",
    responseMode: "补采复核",
    focus: "额枋彩画表层褪色与污染",
    nextAction: "继续补采多光谱图像，结合历史修缮记录做二次判读。"
  }
];

export const screenEvents: ScreenEvent[] = [
  {
    time: "09:10",
    type: "预警",
    title: "华北监测区新增 2 条高风险裂缝提醒",
    detail: "检测结果已同步到数字孪生和专家复核队列。"
  },
  {
    time: "10:40",
    type: "调度",
    title: "江南排水核查任务升级为跨组联动",
    detail: "环境组与现场组共同接单，优先追查返碱源头。"
  },
  {
    time: "12:05",
    type: "智库",
    title: "修缮智库推送彩画补采建议",
    detail: "针对西南片区额枋褪色问题，建议以补采和对比判读为先。"
  },
  {
    time: "14:30",
    type: "工单",
    title: "东侧檐柱复测结果准备转入修缮决策",
    detail: "待专家签字后生成工单并回写区域大屏状态。"
  }
];
