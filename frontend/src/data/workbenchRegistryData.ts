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
    description: "查看应县木塔整体档案、风险和处置状态。",
    status: "运行中"
  },
  {
    id: "twin",
    title: "应县木塔孪生",
    shortLabel: "孪生",
    path: "/twin-workspace",
    description: "查看真实三维孪生、构件档案、风险点和巡检记录。",
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
    title: "处置知识",
    shortLabel: "知识",
    path: "/repair-knowledge",
    description: "按病害档案查看处置方法、文献参考和现场清单。",
    status: "已连接"
  },
  {
    id: "screen",
    title: "区域监管",
    shortLabel: "监管",
    path: "/regional-screen",
    description: "查看佛宫寺片区风险、告警和派工进度。",
    status: "已连接"
  }
];

export const overviewWorkbenchCards: OverviewWorkbenchCard[] = routedWorkbenchModules
  .filter((item) => item.id !== "overview")
  .map((item, index) => ({
    ...item,
    availability: "available",
    stage: `0${index + 1}`
  }));
