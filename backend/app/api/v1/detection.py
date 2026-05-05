from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from backend.app.modules.detection.schemas import (
    CreateDetectionBatchPayload,
    CreateDetectionBatchRequest,
    DetectionBatchDetailPayload,
    DetectionResultPayload,
    ReviewDetectionResultRequest,
)
from backend.app.modules.detection.service import DetectionBatchService, get_detection_batch_service
from backend.app.schemas.common import ApiEnvelope, ListPayload, build_response

router = APIRouter(prefix="/detection", tags=["detection"])


@router.get(
    "/batches",
    response_model=ApiEnvelope[ListPayload[DetectionBatchDetailPayload]],
    summary="List recent detection batches",
)
async def list_detection_batches(
    request: Request,
    service: Annotated[DetectionBatchService, Depends(get_detection_batch_service)],
    limit: int = 20,
    include_demo: bool = False,
) -> ApiEnvelope[ListPayload[DetectionBatchDetailPayload]]:
    batches = service.list_batches(limit=limit, include_demo=include_demo)
    return build_response(
        data=ListPayload[DetectionBatchDetailPayload](items=batches, total=len(batches)),
        request_id=request.state.request_id,
    )


@router.post(
    "/batches",
    response_model=ApiEnvelope[CreateDetectionBatchPayload],
    status_code=status.HTTP_201_CREATED,
    summary="Create a detection batch (Phase 1)",
)
async def create_detection_batch(
    payload: CreateDetectionBatchRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    service: Annotated[DetectionBatchService, Depends(get_detection_batch_service)],
) -> ApiEnvelope[CreateDetectionBatchPayload]:
    result = service.create_batch(payload, background_tasks=background_tasks)
    return build_response(data=result, request_id=request.state.request_id)


@router.get(
    "/batches/{batch_id}",
    response_model=ApiEnvelope[DetectionBatchDetailPayload],
    summary="Read a detection batch (Phase 1)",
)
async def read_detection_batch(
    batch_id: str,
    request: Request,
    service: Annotated[DetectionBatchService, Depends(get_detection_batch_service)],
) -> ApiEnvelope[DetectionBatchDetailPayload]:
    result = service.get_batch(batch_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应的病害识别批次。")
    return build_response(data=result, request_id=request.state.request_id)


@router.delete(
    "/batches/{batch_id}",
    response_model=ApiEnvelope[dict[str, str]],
    summary="Delete one detection history record",
)
async def delete_detection_batch(
    batch_id: str,
    request: Request,
    service: Annotated[DetectionBatchService, Depends(get_detection_batch_service)],
) -> ApiEnvelope[dict[str, str]]:
    deleted = service.delete_batch(batch_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应的检测历史。")
    return build_response(data={"batchId": batch_id}, request_id=request.state.request_id)


@router.get(
    "/batches/{batch_id}/results",
    response_model=ApiEnvelope[ListPayload[DetectionResultPayload]],
    summary="List detection results for a batch",
)
async def list_detection_results(
    batch_id: str,
    request: Request,
    service: Annotated[DetectionBatchService, Depends(get_detection_batch_service)],
) -> ApiEnvelope[ListPayload[DetectionResultPayload]]:
    results = service.list_batch_results(batch_id)
    if results is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应的病害识别批次。")
    return build_response(
        data=ListPayload[DetectionResultPayload](items=results, total=len(results)),
        request_id=request.state.request_id,
    )


@router.get(
    "/results/{result_id}",
    response_model=ApiEnvelope[DetectionResultPayload],
    summary="Read one detection result",
)
async def read_detection_result(
    result_id: str,
    request: Request,
    service: Annotated[DetectionBatchService, Depends(get_detection_batch_service)],
) -> ApiEnvelope[DetectionResultPayload]:
    result = service.get_result(result_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应的病害识别结果。")
    return build_response(data=result, request_id=request.state.request_id)


@router.patch(
    "/results/{result_id}/review",
    response_model=ApiEnvelope[DetectionResultPayload],
    summary="Review one detection result",
)
async def review_detection_result(
    result_id: str,
    payload: ReviewDetectionResultRequest,
    request: Request,
    service: Annotated[DetectionBatchService, Depends(get_detection_batch_service)],
) -> ApiEnvelope[DetectionResultPayload]:
    result = service.review_result(result_id, payload)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应的病害识别结果。")
    return build_response(data=result, request_id=request.state.request_id)
