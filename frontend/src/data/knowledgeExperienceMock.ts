export type KnowledgeMetric = {
  label: string;
  value: string;
  note: string;
};

export type KnowledgeOverviewCard = {
  highlight: string;
  title: string;
  summary: string;
  hint: string;
};

export type KnowledgeStandard = {
  title: string;
  category: string;
  summary: string;
  update: string;
  applicableTo: string;
  checkpoints: string[];
};

export type KnowledgeStrategy = {
  title: string;
  trigger: string;
  response: string;
  deliverable: string;
  collaboration: string;
};

export type KnowledgeCase = {
  title: string;
  site: string;
  issue: string;
  symptom: string;
  diagnosis: string;
  method: string;
  outcome: string;
  caution: string;
  tags: string[];
};

export type KnowledgeChecklist = {
  title: string;
  items: string[];
};

export type KnowledgeQuestion = {
  question: string;
  answer: string;
  recommendation: string;
  references: string[];
};

export type KnowledgeAction =
  | {
      kind: "route";
      title: string;
      entryLabel: string;
      target: string;
    }
  | {
      kind: "external";
      title: string;
      entryLabel: string;
      target: string;
    };

export const knowledgeMetrics: KnowledgeMetric[] = [
  {
    label: "已入库规范",
    value: "216",
    note: "覆盖木构、砖石、彩画、防潮排水与病害调查流程。"
  },
  {
    label: "修缮案例卡",
    value: "1,084",
    note: "按病害类型、构件类别与气候带建立可复用经验索引。"
  },
  {
    label: "联动策略包",
    value: "342",
    note: "可直接映射到病害复核与工单决策的策略集合。"
  }
];

export const knowledgeOverview: KnowledgeOverviewCard[] = [
  {
    highlight: "诊断入口",
    title: "识别结果直达修缮建议",
    summary: "按病害类型、严重等级和材质自动定位到推荐规范、案例和处置顺序。",
    hint: "适合承接病害识别完成后的人工复核。"
  },
  {
    highlight: "经验复用",
    title: "案例与规范同时对照",
    summary: "把条文要求和历史案例放到同一视图里，减少只看单一规则的误判。",
    hint: "支持木构裂缝、台基渗水和彩画保护等常见场景。"
  },
  {
    highlight: "落地动作",
    title: "输出清晰的下一步动作",
    summary: "直接给出复核建议、补采要求、临时控制和是否转工单的建议。",
    hint: "让智库不只是资料库，而是可执行的决策面板。"
  }
];

export const knowledgeStandards: KnowledgeStandard[] = [
  {
    title: "古建筑木构维修工艺指引",
    category: "规范条文",
    summary: "聚焦柱、梁、枋、斗栱裂缝与糟朽处置，支持按构件类别筛选工艺步骤。",
    update: "2026-03-12 更新",
    applicableTo: "木柱、梁枋、斗栱裂缝 / 糟朽 / 变形",
    checkpoints: ["含水率复核", "裂缝活性监测", "可逆性修补"]
  },
  {
    title: "南方高湿环境彩画保护案例集",
    category: "案例经验",
    summary: "整理彩画褪色、起甲与表层污染的分级处置路径，适合联动轻重分级判断。",
    update: "2026-03-10 更新",
    applicableTo: "湿热环境下的彩画褪色、污染与起甲",
    checkpoints: ["多光谱补采", "材料复核", "样区试验"]
  },
  {
    title: "台基渗水与排水路径诊断规则",
    category: "诊断策略",
    summary: "适用于砖石与台基返碱、潮湿带识别后的现场复核与排水排查。",
    update: "2026-03-08 更新",
    applicableTo: "台基返碱、渗水、排水路径异常",
    checkpoints: ["降雨回看", "排水路径核查", "导排方案预案"]
  }
];

export const knowledgeStrategies: KnowledgeStrategy[] = [
  {
    title: "高风险木构病害",
    trigger: "识别结果为高风险裂缝或糟朽，且近 72 小时存在降雨增幅。",
    response: "优先触发含水率复核、近景补拍与临时围控建议。",
    deliverable: "复核单 + 临时控制建议",
    collaboration: "联动病害工作台、孪生点位和现场巡检组。"
  },
  {
    title: "中风险台基潮湿带",
    trigger: "台基返碱、渗水持续出现，环境监测显示湿度异常。",
    response: "优先联动排水路径排查，并比对历史降雨与地表径流记录。",
    deliverable: "排水核查建议 + 环境复测清单",
    collaboration: "联动区域态势大屏的工单调度与江南片区巡检班组。"
  },
  {
    title: "低风险彩画表层病害",
    trigger: "表层褪色、轻微污染或局部起甲，未触发结构风险。",
    response: "建议补充多光谱图像与历史修缮记录，不直接进入施工。",
    deliverable: "补采计划 + 案例比对摘要",
    collaboration: "交由彩画专项组做二次判读，再决定是否立项。"
  }
];

export const knowledgeCases: KnowledgeCase[] = [
  {
    title: "东侧檐柱纵向裂缝修缮",
    site: "山门大殿",
    issue: "木柱裂缝",
    symptom: "裂缝沿木纹向上延伸，雨后宽度增加",
    diagnosis: "高湿环境叠加受力变化，需先排除活动裂缝",
    method: "含水率复核 + 裂缝活性监测 + 可逆性灌注",
    outcome: "三个月后裂缝宽度稳定，转入常规巡检。",
    caution: "未完成含水率复核前不建议直接灌注处理。",
    tags: ["木构", "高风险", "裂缝"]
  },
  {
    title: "台基前缘渗水整治",
    site: "祭台基座",
    issue: "返碱渗水",
    symptom: "雨后返碱带扩展，表层潮湿区域持续不退",
    diagnosis: "排水路径异常叠加地表径流冲刷",
    method: "排水路径排查 + 勾缝修补 + 环境监测点补录",
    outcome: "雨后渗水面积下降 41%，保留继续观察。",
    caution: "若源头未查清，不应先做大面积表层修补。",
    tags: ["台基", "排水", "返碱"]
  },
  {
    title: "正脊下方彩画褪色保护",
    site: "前殿额枋",
    issue: "彩画褪色",
    symptom: "局部褪色伴随轻微污染，边界不稳定",
    diagnosis: "需结合多光谱样本与历史修缮记录做二次判读",
    method: "多光谱补采 + 材料复核 + 小范围试样修护",
    outcome: "完成样区评估后再决定是否整段推进。",
    caution: "避免仅凭可见光图像直接判断为施工级问题。",
    tags: ["彩画", "补采", "低风险"]
  }
];

export const knowledgeChecklists: KnowledgeChecklist[] = [
  {
    title: "木构裂缝复核清单",
    items: ["确认裂缝是否活动", "复测含水率", "补拍近景与端部状态", "核查历史修缮记录"]
  },
  {
    title: "台基渗水排查清单",
    items: ["查看近 72 小时降雨", "核查排水坡向", "确认返碱边界", "比对环境点位数据"]
  },
  {
    title: "彩画病害补采清单",
    items: ["补采多光谱图像", "记录光照条件", "比对历史照片", "确认是否进入样区试验"]
  }
];

export const knowledgeQuestions: KnowledgeQuestion[] = [
  {
    question: "当木构裂缝被识别为高风险，第一步该看什么？",
    answer: "先确认裂缝是否活动、含水率是否异常，再决定是临时控制、补拍复核还是进入修缮建议生成。",
    recommendation: "优先调取木构维修工艺指引，并查看最近一次降雨与湿度记录。",
    references: ["木构维修工艺指引", "现场复核流程", "风险联动策略"]
  },
  {
    question: "病害识别结果怎样映射到修缮建议？",
    answer: "先按病害类型和严重等级分流，再结合构件材质、环境条件和既有案例生成建议路径。",
    recommendation: "高风险结果优先输出复核动作，中低风险结果优先输出补采与对比建议。",
    references: ["策略映射规则", "案例经验索引"]
  },
  {
    question: "什么时候应该暂缓施工、先做补采和复测？",
    answer: "当结果依赖环境变化明显、病害边界不稳定或历史记录缺失时，应优先补采图像、复测含水率或延长观察周期。",
    recommendation: "尤其是彩画表层病害和台基渗水问题，不要直接跳过复核环节。",
    references: ["排水诊断规则", "彩画保护案例集"]
  }
];

export const knowledgeActions: KnowledgeAction[] = [
  {
    kind: "route",
    title: "回到病害工作台",
    entryLabel: "查看识别结果",
    target: "/damage-workspace"
  },
  {
    kind: "route",
    title: "联动区域态势",
    entryLabel: "查看区域调度",
    target: "/regional-screen"
  },
  {
    kind: "external",
    title: "打开规范目录",
    entryLabel: "导出规范清单",
    target: "#standard-index"
  }
];
