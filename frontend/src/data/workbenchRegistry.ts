export type RoutedWorkbenchId = "overview" | "twin" | "damage" | "knowledge" | "screen";

export type RoutedWorkbenchModule = {
  id: RoutedWorkbenchId;
  title: string;
  shortLabel: string;
  path: string;
  description: string;
  status: string;
};

export type OverviewWorkbenchCard = RoutedWorkbenchModule & {
  availability: "available" | "planned";
  stage: string;
};

export const routedWorkbenchModules: RoutedWorkbenchModule[] = [
  {
    id: "overview",
    title: "总览",
    shortLabel: "总览",
    path: "/",
    description: "查看应县木塔整体指标、页面入口与巡检协同状态。",
    status: "运行中"
  },
  {
    id: "twin",
    title: "应县木塔档案",
    shortLabel: "档案",
    path: "/twin-workspace",
    description: "联动建筑场景、构件档案与风险点位。",
    status: "已连接"
  },
  {
    id: "damage",
    title: "图片检测",
    shortLabel: "检测",
    path: "/damage-workspace",
    description: "上传应县木塔巡检照片，生成检测任务和病害档案。",
    status: "可上传"
  },
  {
    id: "knowledge",
    title: "处理知识",
    shortLabel: "知识",
    path: "/repair-knowledge",
    description: "沉淀规范、案例与处置策略，为复核和修缮决策提供支撑。",
    status: "已连接"
  },
  {
    id: "screen",
    title: "区域监管",
    shortLabel: "监管",
    path: "/regional-screen",
    description: "聚合佛宫寺片区态势、重点预警、队伍调度和闭环进度。",
    status: "已连接"
  }
];

export const overviewWorkbenchCards: OverviewWorkbenchCard[] = [
  {
    id: "twin",
    title: "应县木塔档案",
    shortLabel: "档案",
    path: "/twin-workspace",
    description: "浏览应县木塔档案、构件状态和病害点位。",
    status: "可进入",
    availability: "available",
    stage: "01 档案"
  },
  {
    id: "damage",
    title: "图片检测",
    shortLabel: "检测",
    path: "/damage-workspace",
    description: "上传应县木塔巡检照片，检测病害并生成档案。",
    status: "可进入",
    availability: "available",
    stage: "02 检测"
  },
  {
    id: "knowledge",
    title: "处理知识",
    shortLabel: "知识",
    path: "/repair-knowledge",
    description: "将修缮规范、案例经验和策略映射整合为知识入口。",
    status: "可进入",
    availability: "available",
    stage: "03 知识"
  },
  {
    id: "screen",
    title: "区域监管",
    shortLabel: "监管",
    path: "/regional-screen",
    description: "展示佛宫寺片区指标、重点预警、资源负载与现场执行节奏。",
    status: "可进入",
    availability: "available",
    stage: "04 监管"
  }
];
