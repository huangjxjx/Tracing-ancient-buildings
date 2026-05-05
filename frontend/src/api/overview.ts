import type { OverviewPagePayload } from "../types/overview";
import { apiRequest } from "./client";

export type { OverviewPagePayload } from "../types/overview";

export function getOverviewPage() {
  return apiRequest<OverviewPagePayload>("/api/v1/pages/overview");
}
