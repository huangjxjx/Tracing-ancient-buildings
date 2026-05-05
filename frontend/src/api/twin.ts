import type { TwinPagePayload } from "../types/twin";
import { apiRequest } from "./client";

export type { TwinPagePayload } from "../types/twin";

export function getTwinPage(siteId = "site_001") {
  return apiRequest<TwinPagePayload>(`/api/v1/pages/twin?siteId=${encodeURIComponent(siteId)}`);
}
