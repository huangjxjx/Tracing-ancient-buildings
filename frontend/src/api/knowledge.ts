import type {
  KnowledgePagePayload,
  KnowledgeRecommendation,
  KnowledgeRecommendationListPayload
} from "../types/knowledge";
import { apiRequest } from "./client";

export type {
  KnowledgePagePayload,
  KnowledgeRecommendation,
  KnowledgeRecommendationListPayload
} from "../types/knowledge";

export function getKnowledgePage() {
  return apiRequest<KnowledgePagePayload>("/api/v1/pages/knowledge");
}

export function getKnowledgeRecommendations() {
  return apiRequest<KnowledgeRecommendationListPayload>("/api/v1/knowledge/recommendations");
}
