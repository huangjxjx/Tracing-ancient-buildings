import type {
  CreateDetectionBatchPayload,
  CreateDetectionBatchRequest,
  DamageFlowScenario,
  DetectionBatchDetailPayload,
  DetectionBatchListPayload,
  DetectionBatchStatus,
  DetectionResult,
  DetectionResultListPayload,
  ReviewDetectionResultRequest
} from "../types/detection";
import { apiRequest } from "./client";

export type {
  CreateDetectionBatchPayload,
  CreateDetectionBatchRequest,
  DetectionBatchDetailPayload,
  DetectionBatchListPayload,
  DetectionBatchStatus,
  DetectionResult,
  DetectionResultListPayload,
  ReviewDetectionResultRequest
} from "../types/detection";

const detectionScenarioMeta: Record<DetectionBatchStatus, { id: DamageFlowScenario["id"]; label: string; helper: string }> = {
  queued: {
    id: "idle",
    label: "等待识别",
    helper: "批次已创建，后台任务即将开始。"
  },
  running: {
    id: "processing",
    label: "识别中",
    helper: "后台任务正在处理图像。"
  },
  completed: {
    id: "completed",
    label: "已完成",
    helper: "病害档案已写入数据库。"
  },
  failed: {
    id: "idle",
    label: "识别失败",
    helper: "后台任务执行失败，请检查上传文件或后端日志后重新创建批次。"
  }
};

export async function getLatestDetectionBatch() {
  const payload = await apiRequest<DetectionBatchListPayload>("/api/v1/detection/batches?limit=1");
  return payload.items[0] ?? null;
}

export function getDetectionBatches(limit = 12) {
  return apiRequest<DetectionBatchListPayload>(`/api/v1/detection/batches?limit=${limit}`);
}

export function getDetectionBatch(batchId: string) {
  return apiRequest<DetectionBatchDetailPayload>(`/api/v1/detection/batches/${encodeURIComponent(batchId)}`);
}

export function deleteDetectionBatch(batchId: string) {
  return apiRequest<{ batchId: string }>(`/api/v1/detection/batches/${encodeURIComponent(batchId)}`, {
    method: "DELETE"
  });
}

export function createDetectionBatch(payload: CreateDetectionBatchRequest) {
  return apiRequest<CreateDetectionBatchPayload>("/api/v1/detection/batches", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getDetectionBatchResults(batchId: string) {
  return apiRequest<DetectionResultListPayload>(`/api/v1/detection/batches/${encodeURIComponent(batchId)}/results`);
}

export function getDetectionResult(resultId: string) {
  return apiRequest<DetectionResult>(`/api/v1/detection/results/${encodeURIComponent(resultId)}`);
}

export function reviewDetectionResult(resultId: string, payload: ReviewDetectionResultRequest) {
  return apiRequest<DetectionResult>(`/api/v1/detection/results/${encodeURIComponent(resultId)}/review`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function createDefaultDetectionBatchRequest(): CreateDetectionBatchRequest {
  return {
    siteId: "site_001",
    componentId: "component-pillar-east",
    assetIds: [`asset_capture_${Date.now()}`],
    source: "ground",
    capturedAt: new Date().toISOString()
  };
}

export function mapDetectionBatchToScenario(payload: DetectionBatchDetailPayload): DamageFlowScenario {
  const meta = detectionScenarioMeta[payload.status];

  return {
    id: meta.id,
    label: meta.label,
    helper: meta.helper,
    heroTitle: payload.heroTitle,
    heroDescription: payload.heroDescription,
    uploadHint: payload.uploadHint,
    uploadBadge: payload.uploadBadge,
    queueSummary: payload.queueSummary,
    asset: payload.asset,
    tasks: payload.tasks,
    results: payload.results
  };
}
