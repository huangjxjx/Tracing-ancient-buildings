export type ScreenMetric = {
  label: string;
  value: string;
  delta: string;
};

export type RegionPulse = {
  region: string;
  level: "high" | "medium" | "stable";
  summary: string;
  backlog: string;
  humidity: string;
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

export type ScreenTrend = {
  label: string;
  value: number;
};

export type ScreenTimeline = {
  time: string;
  title: string;
  detail: string;
};

export type ScreenCapacity = {
  label: string;
  value: string;
  note: string;
};

export const screenMetrics: ScreenMetric[] = [
  {
    label: "今日巡检批次",
    value: "28",
    delta: "较昨日 +4"
  },
  {
    label: "待复核高风险点",
    value: "19",
    delta: "3 项需在 24 小时内处理"
  },
  {
    label: "修缮联动建议",
    value: "57",
    delta: "其中 12 项已转工单"
  },
  {
    label: "区域接入率",
    value: "92%",
    delta: "西南监测区设备补点中"
  }
];

export const screenRegionPulse: RegionPulse[] = [
  {
    region: "华北监测区",
    level: "high",
    summary: "大风后屋面松动预警增加，需要优先复核。",
    backlog: "7 项待复核",
    humidity: "湿度 61%"
  },
  {
    region: "江南监测区",
    level: "medium",
    summary: "高湿环境下台基渗水点持续上升，排水排查压力增加。",
    backlog: "5 项处理中",
    humidity: "湿度 78%"
  },
  {
    region: "西南监测区",
    level: "medium",
    summary: "山地片区彩画病害复核密度提升，补拍需求增加。",
    backlog: "4 项待补拍",
    humidity: "湿度 74%"
  },
  {
    region: "西北监测区",
    level: "stable",
    summary: "风化类病害整体稳定，工作重心转向常规巡检。",
    backlog: "2 项跟踪中",
    humidity: "湿度 42%"
  }
];

export const screenAlerts: ScreenAlert[] = [
  {
    title: "东南坡瓦件位移预警",
    region: "华北监测区",
    severity: "high",
    detail: "无人机复测显示位移趋势加快，建议优先围控并现场复核。"
  },
  {
    title: "台基前缘渗水范围扩大",
    region: "江南监测区",
    severity: "medium",
    detail: "连续降雨后返碱带扩展，建议同步排查排水路径。"
  },
  {
    title: "额枋彩画褪色待补采",
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

export const screenTrends: ScreenTrend[] = [
  { label: "木构裂缝", value: 86 },
  { label: "砖石剥蚀", value: 73 },
  { label: "渗水返碱", value: 68 },
  { label: "彩画褪色", value: 49 }
];

export const screenTimeline: ScreenTimeline[] = [
  {
    time: "08:40",
    title: "华北监测区升级红色关注",
    detail: "屋面瓦件位移风险升高，已推送现场围控建议。"
  },
  {
    time: "10:15",
    title: "江南监测区追加排水排查",
    detail: "返碱带扩展后，新增 2 条现场核查路线。"
  },
  {
    time: "13:30",
    title: "西南监测区补拍任务派发",
    detail: "彩画病害样本不足，已派出专项组补采多光谱图像。"
  }
];

export const screenCapacity: ScreenCapacity[] = [
  {
    label: "在线巡检队伍",
    value: "11 组",
    note: "较昨日多 2 组，当前资源可支撑两区并行复核"
  },
  {
    label: "待处理工单池",
    value: "34 项",
    note: "12 项已具备修缮建议，可直接推进专家确认"
  },
  {
    label: "实时监测点",
    value: "276 个",
    note: "西南区新补点 18 个，环境数据接入仍在爬升"
  }
];
