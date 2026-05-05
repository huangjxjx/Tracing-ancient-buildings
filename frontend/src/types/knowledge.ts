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

export type KnowledgeRecommendation = {
  resultId: string;
  title: string;
  severity: string;
  triggerReason: string;
  suggestedStandard: string;
  recommendedAction: string;
  checklistTitle: string;
  workOrderStatus: string;
  references: {
    title: string;
    url: string;
    excerpt: string;
  }[];
};

export type KnowledgePagePayload = {
  knowledgeMetrics: KnowledgeMetric[];
  knowledgeOverview: KnowledgeOverviewCard[];
  knowledgeStandards: KnowledgeStandard[];
  knowledgeStrategies: KnowledgeStrategy[];
  knowledgeCases: KnowledgeCase[];
  knowledgeChecklists: KnowledgeChecklist[];
  knowledgeQuestions: KnowledgeQuestion[];
  knowledgeActions: KnowledgeAction[];
  knowledgeRecommendations: KnowledgeRecommendation[];
};

export type KnowledgeRecommendationListPayload = {
  items: KnowledgeRecommendation[];
  total: number;
};
