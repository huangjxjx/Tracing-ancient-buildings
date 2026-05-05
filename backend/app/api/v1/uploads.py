from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.db.session import get_db_session
from backend.app.core.config import Settings, get_settings
from backend.app.modules.detection.repository import DetectionBatchRepository
from backend.app.modules.uploads.schemas import PresignUploadPayload, PresignUploadRequest, UploadAssetPayload
from backend.app.modules.uploads.service import UploadAssetNotFoundError, UploadedFileNotAvailableError, UploadService
from backend.app.schemas.common import ApiEnvelope, build_response

router = APIRouter(prefix="/uploads", tags=["uploads"])


def get_upload_service(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UploadService:
    return UploadService(DetectionBatchRepository(session), settings)


@router.post(
    "/presign",
    response_model=ApiEnvelope[PresignUploadPayload],
    summary="Create a local upload session",
)
async def create_upload_presign(
    payload: PresignUploadRequest,
    request: Request,
    service: Annotated[UploadService, Depends(get_upload_service)],
) -> ApiEnvelope[PresignUploadPayload]:
    result = service.create_presign(payload)
    return build_response(data=result, request_id=request.state.request_id)


@router.put(
    "/files/{asset_id}",
    response_model=ApiEnvelope[UploadAssetPayload],
    summary="Upload a file into local storage",
)
async def upload_asset_file(
    asset_id: str,
    request: Request,
    service: Annotated[UploadService, Depends(get_upload_service)],
) -> ApiEnvelope[UploadAssetPayload]:
    content = await request.body()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    try:
        result = service.complete_upload(
            asset_id=asset_id,
            content=content,
            content_type=request.headers.get("content-type"),
        )
    except UploadAssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Upload asset {asset_id} not found") from exc

    return build_response(data=result, request_id=request.state.request_id)


@router.get(
    "/files/{asset_id}",
    summary="Read an uploaded file from local storage",
)
async def read_uploaded_asset_file(
    asset_id: str,
    service: Annotated[UploadService, Depends(get_upload_service)],
) -> FileResponse:
    try:
        storage_path, filename, content_type = service.get_uploaded_file(asset_id)
    except UploadAssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Upload asset {asset_id} not found") from exc
    except UploadedFileNotAvailableError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Upload asset {asset_id} file is not available") from exc

    return FileResponse(path=storage_path, media_type=content_type, headers={"content-disposition": f'inline; filename="{filename}"'})
