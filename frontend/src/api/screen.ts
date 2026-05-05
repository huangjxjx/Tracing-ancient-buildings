import type { ScreenPagePayload } from "../types/screen";
import { apiRequest } from "./client";

export type { ScreenPagePayload } from "../types/screen";

export function getScreenPage() {
  return apiRequest<ScreenPagePayload>("/api/v1/pages/screen");
}
