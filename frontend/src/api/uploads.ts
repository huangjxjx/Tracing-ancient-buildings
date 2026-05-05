import { ApiError, type ApiEnvelope, resolveApiBaseUrl } from "./client";

export type PresignUploadRequest = {
  filename: string;
  contentType: string;
  bizType: string;
};

export type PresignUploadPayload = {
  assetId: string;
  uploadUrl: string;
  objectKey: string;
  method: "PUT";
};

export type UploadAssetPayload = {
  assetId: string;
  filename: string;
  contentType: string;
  fileSize: number;
  objectKey: string;
  uploadStatus: string;
};

async function parseEnvelope<T>(response: Response): Promise<ApiEnvelope<T> | null> {
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    return null;
  }
  return (await response.json()) as ApiEnvelope<T>;
}

export async function createUploadSession(payload: PresignUploadRequest) {
  const response = await fetch(`${resolveApiBaseUrl()}/api/v1/uploads/presign`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const envelope = await parseEnvelope<PresignUploadPayload>(response);

  if (!response.ok || !envelope) {
    throw new ApiError(response.statusText || "Create upload session failed", response.status);
  }

  return envelope.data;
}

export async function uploadFileToLocalStorage(uploadUrl: string, file: File) {
  const resolvedUploadUrl = uploadUrl.startsWith("http") ? uploadUrl : `${resolveApiBaseUrl()}${uploadUrl}`;
  const response = await fetch(resolvedUploadUrl, {
    method: "PUT",
    headers: { "Content-Type": file.type || "application/octet-stream" },
    body: file
  });
  const envelope = await parseEnvelope<UploadAssetPayload>(response);

  if (!response.ok || !envelope) {
    throw new ApiError(response.statusText || "Upload file failed", response.status);
  }

  return envelope.data;
}

export function getUploadedFileUrl(assetId: string) {
  return `${resolveApiBaseUrl()}/api/v1/uploads/files/${encodeURIComponent(assetId)}`;
}
