from __future__ import annotations

import re
from pathlib import Path

from backend.app.core.config import Settings
from backend.app.modules.detection.repository import DetectionBatchRepository
from backend.app.modules.uploads.schemas import PresignUploadPayload, PresignUploadRequest, UploadAssetPayload


class UploadAssetNotFoundError(Exception):
    pass


class UploadedFileNotAvailableError(Exception):
    pass


class UploadService:
    def __init__(self, repository: DetectionBatchRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    def create_presign(self, payload: PresignUploadRequest) -> PresignUploadPayload:
        filename = self._sanitize_filename(payload.filename)
        asset_id, object_key = self._repository.create_upload_asset(
            filename=filename,
            content_type=payload.content_type,
            biz_type=self._sanitize_path_part(payload.biz_type),
        )
        return PresignUploadPayload(
            asset_id=asset_id,
            upload_url=f"{self._settings.upload_public_base_url.rstrip('/')}/{asset_id}",
            object_key=object_key,
            method="PUT",
        )

    def complete_upload(self, *, asset_id: str, content: bytes, content_type: str | None) -> UploadAssetPayload:
        asset_model = self._repository.get_upload_asset(asset_id)
        if asset_model is None or not asset_model.object_key:
            raise UploadAssetNotFoundError(asset_id)

        storage_root = Path(self._settings.local_storage_root).resolve()
        storage_path = (storage_root / "uploads" / asset_model.object_key).resolve()
        if not storage_path.is_relative_to(storage_root):
            raise ValueError("Resolved upload path escaped local storage root")

        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(content)

        updated_model = self._repository.mark_upload_completed(
            asset_id=asset_id,
            storage_path=str(storage_path),
            file_size=len(content),
            content_type=content_type or asset_model.content_type or "application/octet-stream",
        )
        if updated_model is None:
            raise UploadAssetNotFoundError(asset_id)

        return UploadAssetPayload(
            asset_id=updated_model.asset_id,
            filename=updated_model.file_name,
            content_type=updated_model.content_type or "application/octet-stream",
            file_size=updated_model.file_size or 0,
            object_key=updated_model.object_key or "",
            upload_status=updated_model.upload_status or "uploaded",
        )

    def get_uploaded_file(self, asset_id: str) -> tuple[Path, str, str]:
        asset_model = self._repository.get_upload_asset(asset_id)
        if asset_model is None:
            raise UploadAssetNotFoundError(asset_id)
        if asset_model.upload_status != "uploaded" or not asset_model.storage_path:
            raise UploadedFileNotAvailableError(asset_id)

        storage_root = Path(self._settings.local_storage_root).resolve()
        storage_path = Path(asset_model.storage_path).resolve()
        if not storage_path.is_relative_to(storage_root) or not storage_path.exists():
            raise UploadedFileNotAvailableError(asset_id)

        return (
            storage_path,
            asset_model.file_name,
            asset_model.content_type or "application/octet-stream",
        )

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        cleaned = Path(filename).name.strip()
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", cleaned)
        return cleaned or "upload.bin"

    @staticmethod
    def _sanitize_path_part(value: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
        return cleaned or "general"
