export type ApiEnvelope<T> = {
  code: string;
  message: string;
  requestId: string;
  data: T;
};

export class ApiError extends Error {
  status: number;
  requestId?: string;

  constructor(message: string, status: number, requestId?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.requestId = requestId;
  }
}

type ApiRequestOptions = RequestInit & {
  timeoutMs?: number;
};

const DEFAULT_API_BASE_URL = "http://localhost:8000";

export function resolveApiBaseUrl() {
  const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  return (configuredBaseUrl || DEFAULT_API_BASE_URL).replace(/\/+$/, "");
}

async function parseJsonResponse<T>(response: Response): Promise<T | null> {
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    return null;
  }

  return (await response.json()) as T;
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { timeoutMs = 10000, headers, ...init } = options;
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${resolveApiBaseUrl()}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...headers
      },
      signal: controller.signal
    });

    const payload = await parseJsonResponse<ApiEnvelope<T> | { detail?: string }>(response);

    if (!response.ok) {
      const detailMessage =
        payload && "detail" in payload && typeof payload.detail === "string"
          ? payload.detail
          : response.statusText || "请求失败";

      const requestId =
        payload && "requestId" in payload && typeof payload.requestId === "string" ? payload.requestId : undefined;

      throw new ApiError(detailMessage, response.status, requestId);
    }

    if (!payload || !("data" in payload)) {
      throw new ApiError("接口返回格式不正确。", response.status);
    }

    return payload.data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("请求超时，请确认后端服务已启动。", 408);
    }

    throw new ApiError("无法连接后端服务，请确认接口地址和服务状态。", 0);
  } finally {
    window.clearTimeout(timeoutId);
  }
}
