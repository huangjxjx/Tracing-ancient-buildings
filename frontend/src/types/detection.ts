export type DamageFlowScenarioId = "idle" | "processing" | "completed";

export type DetectionBatchStatus = "queued" | "running" | "completed" | "failed";
export type DetectionTaskStatus = "pending" | "running" | "completed" | "failed";
export type DetectionSource = "drone" | "ground" | "mobile";
export type DamageSeverity = "high" | "medium" | "low";
export type DetectionReviewStatus = "pending" | "approved" | "rejected" | "needs_recheck";

export interface UploadInstruction {
  title: string;
  body: string;
}

export type LocalUploadState = "idle" | "uploading" | "uploaded" | "error";

export interface UploadAsset {
  id: string;
  name: string;
  source: string;
  capturedAt: string;
  progress: number;
  statusLabel: string;
}

export interface DetectionTask {
  id: string;
  title: string;
  description: string;
  status: DetectionTaskStatus;
  progress: number;
  eta: string;
  errorMessage?: string | null;
}

export interface DetectionResult {
  id: string;
  taskId: string;
  title: string;
  damageType: string;
  confidence: number;
  area: string;
  severity: DamageSeverity;
  location: string;
  component: string;
  boundingBox: string;
  suggestion: string;
  summary: string;
  reviewStatus: DetectionReviewStatus;
  modelVersion: string;
  tags: string[];
}

export interface DamageFlowScenario {
  id: DamageFlowScenarioId;
  label: string;
  helper: string;
  heroTitle: string;
  heroDescription: string;
  uploadHint: string;
  uploadBadge: string;
  queueSummary: string;
  asset: UploadAsset;
  tasks: DetectionTask[];
  results: DetectionResult[];
}

export type DetectionBatchDetailPayload = {
  batchId: string;
  siteId: string;
  componentId: string;
  source: DetectionSource;
  status: DetectionBatchStatus;
  progress: number;
  elapsedSeconds: number;
  errorMessage?: string | null;
  capturedAt: string;
  createdAt: string;
  heroTitle: string;
  heroDescription: string;
  uploadHint: string;
  uploadBadge: string;
  queueSummary: string;
  asset: UploadAsset;
  tasks: DetectionTask[];
  results: DetectionResult[];
};

export type CreateDetectionBatchRequest = {
  siteId: string;
  componentId: string;
  assetIds: string[];
  source: DetectionSource;
  capturedAt: string;
};

export type CreateDetectionBatchPayload = {
  batchId: string;
  status: DetectionBatchStatus;
};

export type DetectionResultListPayload = {
  items: DetectionResult[];
  total: number;
};

export type DetectionBatchListPayload = {
  items: DetectionBatchDetailPayload[];
  total: number;
};

export type ReviewDetectionResultRequest = {
  reviewStatus: DetectionReviewStatus;
  note?: string;
};
