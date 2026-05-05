export type RoutedWorkbenchId = "overview" | "twin" | "damage";

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
    title: "首页总览",
    shortLabel: "总览",
    path: "/",
    description: "查看全局指标、模块入口与联动态势。",
    status: "工作台已接入"
  },
  {
    id: "twin",
    title: "数字孪生工作台",
    shortLabel: "数字孪生",
    path: "/twin-workspace",
    description: "联动三维场景、构件档案与病害点位。",
    status: "场景联动中"
  },
  {
    id: "damage",
    title: "病害检测工作台",
    shortLabel: "病害检测",
    path: "/damage-workspace",
    description: "承接图像上传、识别任务与结果复核。",
    status: "流程可演示"
  }
];

export const overviewWorkbenchCards: OverviewWorkbenchCard[] = [
  {
    id: "twin",
    title: "数字孪生工作台",
    shortLabel: "数字孪生",
    path: "/twin-workspace",
    description: "浏览场景结构、风险点位和档案侧栏联动。",
    status: "可进入",
    availability: "available",
    stage: "01 场景联动"
  },
  {
    id: "damage",
    title: "病害检测工作台",
    shortLabel: "病害检测",
    path: "/damage-workspace",
    description: "模拟图像上传、识别执行与结果复核闭环。",
    status: "可进入",
    availability: "available",
    stage: "02 上传识别"
  },
  {
    id: "overview",
    title: "修缮智库",
    shortLabel: "修缮智库",
    path: "/",
    description: "规划接入规范知识、案例经验和修缮策略映射。",
    status: "规划中",
    availability: "planned",
    stage: "03 决策支撑"
  }
];
