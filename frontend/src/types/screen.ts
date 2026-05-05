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

export type ScreenCoverageStatus = "critical" | "watch" | "stable";

export type ScreenCoverageRegion = {
  region: string;
  healthIndex: number;
  connectedSites: number;
  highRiskCount: number;
  workOrderProgress: number;
  status: ScreenCoverageStatus;
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

export type ScreenAlertSeverity = "high" | "medium" | "low";

export type ScreenAlert = {
  title: string;
  region: string;
  severity: ScreenAlertSeverity;
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

export type ScreenPagePayload = {
  screenMetrics: ScreenMetric[];
  screenCommandNotes: ScreenCommandNote[];
  screenCoverageRegions: ScreenCoverageRegion[];
  screenIssuesTop5: ScreenIssue[];
  screenWorkOrderStages: ScreenWorkOrderStage[];
  screenAlerts: ScreenAlert[];
  screenDispatches: ScreenDispatch[];
  screenRegionDetails: ScreenRegionDetail[];
  screenEvents: ScreenEvent[];
};
