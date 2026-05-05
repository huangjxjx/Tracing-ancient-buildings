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

export type OverviewBriefing = {
  title: string;
  summary: string;
  status: string;
};

export type CoordinationEvent = {
  title: string;
  module: string;
  time: string;
  detail: string;
};

export type OverviewPagePayload = {
  heroMetrics: Metric[];
  archiveNodes: ArchiveNode[];
  issueRanking: Ranking[];
  regionalHealth: RegionalHealth[];
  workOrders: WorkOrder[];
  overviewBriefings: OverviewBriefing[];
  coordinationEvents: CoordinationEvent[];
};
