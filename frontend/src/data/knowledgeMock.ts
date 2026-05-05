export type KnowledgeMetric = {
  label: string;
  value: string;
  note: string;
};

export type KnowledgeSource = {
  title: string;
  category: string;
  summary: string;
  update: string;
};

export type KnowledgeCase = {
  title: string;
  site: string;
  issue: string;
  method: string;
  outcome: string;
};

export type KnowledgeStrategy = {
  title: string;
  trigger: string;
  response: string;
};

export type KnowledgeQuestion = {
  question: string;
  answer: string;
  references: string[];
};

export type KnowledgeInsight = {
  title: string;
  detail: string;
  status: string;
};

export type KnowledgeCoverage = {
  scene: string;
  clue: string;
  action: string;
};

export const knowledgeMetrics: KnowledgeMetric[] = [
  {
    label: "已入库规范",
    value: "216",
    note: "覆盖木构、砖石、彩画、防潮排水与病害调查流程"
  },
  {
    label: "修缮案例卡",
    value: "1,084",
    note: "按病害类型、构件类别和气候带建立可复用经验索引"
  },
  {
    label: "联动建议",
    value: "342",
    note: "可直接映射到病害复核和工单决策的处置策略"
  }
];

export const knowledgeInsights: KnowledgeInsight[] = [
  {
    title: "今日高频策略",
    detail: "木构裂缝复核、台基排水排查和彩画补采是当前优先调用策略。",
    status: "已同步病害工作台"
  },
  {
    title: "知识缺口提醒",
    detail: "西南监测区高湿环境下彩画病害案例仍偏少，建议补充南方样本。",
    status: "建议新增专题"
  },
  {
    title: "复核闭环状态",
    detail: "12 条修缮建议已回写工单草案，支持继续追加专家意见。",
    status: "闭环推进中"
  }
];

export const knowledgeSources: KnowledgeSource[] = [
  {
    title: "古建筑木构维修工艺指引",
    category: "规范条文",
    summary: "聚焦檩、梁、斗拱和柱身裂缝与糟朽处置，支持按构件类别筛选工艺步骤。",
    update: "2026-03-12 更新"
  },
  {
    title: "南方高湿环境彩画保护案例集",
    category: "案例经验",
    summary: "整理彩画褪色、起甲和表层污渍的分级处置路径，适合联动轻中度病害判断。",
    update: "2026-03-10 更新"
  },
  {
    title: "台基渗水与排水路径诊断规则",
    category: "诊断策略",
    summary: "适用于砖石台基返碱、渗水识别后的现场复核与排水排查建议。",
    update: "2026-03-08 更新"
  }
];

export const knowledgeCases: KnowledgeCase[] = [
  {
    title: "东侧檐柱纵向裂缝修缮",
    site: "山门大殿",
    issue: "木柱裂缝",
    method: "含水率复核 + 裂缝活性监测 + 可逆性灌注",
    outcome: "三个月后裂缝宽度稳定，转入常规巡检"
  },
  {
    title: "台基前缘渗水整治",
    site: "祭台基座",
    issue: "返碱渗水",
    method: "排水路径排查 + 勾缝修补 + 环境监测点补设",
    outcome: "雨后渗水面积下降 41%，保留持续观测"
  },
  {
    title: "正脊下方彩画褪色保护",
    site: "前殿额枋",
    issue: "彩画褪色",
    method: "多光谱补采 + 材料复核 + 小范围试样修护",
    outcome: "完成试样区评估后再决定是否整段推进"
  }
];

export const knowledgeStrategies: KnowledgeStrategy[] = [
  {
    title: "高风险木构病害",
    trigger: "识别结果为高风险裂缝或糟朽，且近 72 小时存在降雨增幅。",
    response: "优先触发含水率复核、近景补拍与临时围控建议。"
  },
  {
    title: "中风险台基潮湿带",
    trigger: "台基返碱、渗水持续出现，环境监测显示湿度异常。",
    response: "优先联动排水路径排查，并对比历史降雨和地表径流记录。"
  },
  {
    title: "低风险彩画表层病害",
    trigger: "表层褪色、轻微污染或局部起甲，未触发结构风险。",
    response: "建议补充多光谱图像与历史修缮记录，不直接进入施工。"
  }
];

export const knowledgeQuestions: KnowledgeQuestion[] = [
  {
    question: "木构裂缝被识别为高风险后，现场第一步应该看什么？",
    answer: "先确认裂缝是否仍在活动、含水率是否异常，再决定是临时围控、补拍复核还是直接生成修缮建议。",
    references: ["木构维修工艺指引", "现场复核流程", "风险联动策略"]
  },
  {
    question: "病害识别结果怎样映射到修缮建议？",
    answer: "先按病害类型和严重等级分流，再结合构件材质、环境条件和既有案例生成建议路径。",
    references: ["策略映射规则", "案例经验索引"]
  }
];

export const knowledgeCoverage: KnowledgeCoverage[] = [
  {
    scene: "木构件裂缝",
    clue: "宽度增长、含水率偏高、连续阴雨",
    action: "优先复测并调用木构灌注与加固策略"
  },
  {
    scene: "台基渗水返碱",
    clue: "降雨后水迹扩张、湿度长时间高位",
    action: "排查排水路径并结合环境监测做持续跟踪"
  },
  {
    scene: "彩画表层褪色",
    clue: "表层亮度下降、局部起甲、历史修缮记录不完整",
    action: "补充多光谱采集，转入保护性修护评估"
  }
];
