import type { TwinComponentRecord, TwinDamagePoint, TwinSceneNode } from "../features/twin/types";

export const twinSceneNodes: TwinSceneNode[] = [
  {
    id: "site-ground",
    label: "场地地坪",
    primitive: "box",
    size: [36, 0.5, 36],
    position: [0, -0.25, 0],
    color: "#d7c7a9",
    wireColor: "#b49a73"
  },
  {
    id: "foundation-platform",
    label: "台基",
    primitive: "box",
    size: [18, 1.2, 14],
    position: [0, 0.6, 0],
    color: "#b89e79",
    wireColor: "#8c7655",
    roughness: 0.9
  },
  {
    id: "main-hall-body",
    label: "殿身主体",
    primitive: "box",
    size: [14.5, 7, 10.5],
    position: [0, 4.8, 0],
    color: "#d9c6a6",
    wireColor: "#9f8563"
  },
  {
    id: "roof-lower",
    label: "主屋面",
    primitive: "cone",
    radius: 11.2,
    height: 4.8,
    radialSegments: 4,
    position: [0, 9.5, 0],
    rotation: [0, Math.PI / 4, 0],
    color: "#914935",
    wireColor: "#6e3022",
    roughness: 0.72
  },
  {
    id: "roof-upper",
    label: "脊顶",
    primitive: "cone",
    radius: 6.5,
    height: 3,
    radialSegments: 4,
    position: [0, 12.6, 0],
    rotation: [0, Math.PI / 4, 0],
    color: "#a65a3d",
    wireColor: "#7d3d29",
    roughness: 0.7
  },
  {
    id: "pillar-east-front",
    label: "东前檐柱",
    primitive: "cylinder",
    radiusTop: 0.55,
    radiusBottom: 0.65,
    height: 6.8,
    position: [5.3, 4, 3.8],
    color: "#835439",
    wireColor: "#603924"
  },
  {
    id: "pillar-east-back",
    label: "东后檐柱",
    primitive: "cylinder",
    radiusTop: 0.55,
    radiusBottom: 0.65,
    height: 6.8,
    position: [5.3, 4, -3.8],
    color: "#835439",
    wireColor: "#603924"
  },
  {
    id: "pillar-west-front",
    label: "西前檐柱",
    primitive: "cylinder",
    radiusTop: 0.55,
    radiusBottom: 0.65,
    height: 6.8,
    position: [-5.3, 4, 3.8],
    color: "#8d6240",
    wireColor: "#664126"
  },
  {
    id: "pillar-west-back",
    label: "西后檐柱",
    primitive: "cylinder",
    radiusTop: 0.55,
    radiusBottom: 0.65,
    height: 6.8,
    position: [-5.3, 4, -3.8],
    color: "#8d6240",
    wireColor: "#664126"
  }
];

export const twinComponents: TwinComponentRecord[] = [
  {
    id: "component-platform",
    name: "须弥台基",
    category: "基础",
    material: "砖石",
    riskLevel: "medium",
    status: "潮湿敏感",
    summary: "台基前缘存在渗水返碱迹象，需要结合排水与雨量信息持续跟踪。",
    lastInspection: "2026-03-10 14:20",
    nodeIds: ["site-ground", "foundation-platform"],
    focusPoint: [0, 0.7, 0],
    metrics: [
      { label: "最近巡检", value: "48 小时内" },
      { label: "监测类型", value: "湿度 / 沉降" },
      { label: "风险等级", value: "II 级" }
    ],
    relatedDamageIds: ["damage-platform-seepage"]
  },
  {
    id: "component-body",
    name: "殿身主体",
    category: "主体",
    material: "木构架 + 砖墙",
    riskLevel: "medium",
    status: "彩画褪色",
    summary: "主体外檐存在彩画褪色现象，需结合构件档案和历史记录持续观察。",
    lastInspection: "2026-03-11 09:05",
    nodeIds: ["main-hall-body"],
    focusPoint: [0, 4.8, 0],
    metrics: [
      { label: "档案编号", value: "GJ-TWIN-01" },
      { label: "构件类别", value: "围护 / 彩画" },
      { label: "病害数量", value: "1 处" }
    ],
    relatedDamageIds: ["damage-paint-weathering"]
  },
  {
    id: "component-roof",
    name: "重檐屋面",
    category: "屋面",
    material: "木基层 + 筒瓦",
    riskLevel: "high",
    status: "瓦件松动",
    summary: "屋面存在瓦件松动风险，需重点关注风雨天气下的稳定性变化。",
    lastInspection: "2026-03-11 11:40",
    nodeIds: ["roof-lower", "roof-upper"],
    focusPoint: [0, 10.8, 0],
    metrics: [
      { label: "屋面坡向", value: "四坡顶" },
      { label: "预警来源", value: "无人机巡检" },
      { label: "风险等级", value: "III 级" }
    ],
    relatedDamageIds: ["damage-roof-shift"]
  },
  {
    id: "component-pillar-east",
    name: "东侧檐柱组",
    category: "柱体",
    material: "木柱",
    riskLevel: "high",
    status: "纵向裂缝",
    summary: "东侧柱组出现纵向裂缝，需要结合含水率和裂缝活性持续评估。",
    lastInspection: "2026-03-11 08:10",
    nodeIds: ["pillar-east-front", "pillar-east-back"],
    focusPoint: [5.3, 4, 0],
    metrics: [
      { label: "材质含水率", value: "18.4%" },
      { label: "裂缝宽度", value: "3.2 mm" },
      { label: "风险等级", value: "III 级" }
    ],
    relatedDamageIds: ["damage-east-pillar-crack"]
  },
  {
    id: "component-pillar-west",
    name: "西侧檐柱组",
    category: "柱体",
    material: "木柱",
    riskLevel: "low",
    status: "状态稳定",
    summary: "当前状态稳定，可作为同类木柱构件的健康对照对象。",
    lastInspection: "2026-03-09 16:30",
    nodeIds: ["pillar-west-front", "pillar-west-back"],
    focusPoint: [-5.3, 4, 0],
    metrics: [
      { label: "监测频率", value: "每周一次" },
      { label: "当前倾角", value: "0.3°" },
      { label: "风险等级", value: "I 级" }
    ],
    relatedDamageIds: []
  }
];

export const twinDamagePoints: TwinDamagePoint[] = [
  {
    id: "damage-east-pillar-crack",
    name: "东前檐柱纵向裂缝",
    componentId: "component-pillar-east",
    type: "裂缝",
    riskLevel: "high",
    severityScore: 0.92,
    status: "待复核",
    description: "柱身迎风面出现贯通倾向裂缝，需重点关注裂缝延伸趋势和受潮影响。",
    suggestion: "建议补拍近景并结合含水率复核，再决定是否进入灌注修补工单。",
    position: [5.85, 5.9, 4.2],
    anchorNodeId: "pillar-east-front",
    inspectedAt: "2026-03-11 08:16"
  },
  {
    id: "damage-roof-shift",
    name: "东南坡瓦件位移",
    componentId: "component-roof",
    type: "松动",
    riskLevel: "high",
    severityScore: 0.87,
    status: "预警中",
    description: "屋脊转折位置检测到瓦件滑移，存在风雨条件下进一步松动的风险。",
    suggestion: "建议叠加近 72 小时风雨数据，确认是否需要立即设置封控半径。",
    position: [5.2, 10.8, 5],
    anchorNodeId: "roof-lower",
    inspectedAt: "2026-03-11 11:43"
  },
  {
    id: "damage-platform-seepage",
    name: "台基前缘渗水",
    componentId: "component-platform",
    type: "渗水",
    riskLevel: "medium",
    severityScore: 0.71,
    status: "持续监测",
    description: "台基前侧出现返碱与潮湿带，应结合环境变化持续监测渗水范围。",
    suggestion: "建议先核查排水路径，并同步跟踪潮湿带扩散情况。",
    position: [0, 1.2, 6.6],
    anchorNodeId: "foundation-platform",
    inspectedAt: "2026-03-10 14:25"
  },
  {
    id: "damage-paint-weathering",
    name: "殿身彩画风化",
    componentId: "component-body",
    type: "风化",
    riskLevel: "medium",
    severityScore: 0.64,
    status: "待补采",
    description: "主体外檐彩画局部褪色，需结合近景影像核查表层病害范围。",
    suggestion: "建议补充多光谱图像，并进一步确认彩画表层病害边界。",
    position: [-4.8, 6.4, 5.35],
    anchorNodeId: "main-hall-body",
    inspectedAt: "2026-03-11 09:18"
  }
];

export const twinDefaultDamageId = "damage-east-pillar-crack";
