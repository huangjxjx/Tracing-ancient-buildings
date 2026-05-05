from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from backend.app.modules.workorders.schemas import CreateWorkOrderRequest, UpdateWorkOrderStatusRequest, WorkOrderPayload
from backend.app.modules.workorders.service import WorkOrderService, get_work_order_service
from backend.app.schemas.common import ApiEnvelope, ListPayload, build_response

router = APIRouter(prefix="/workorders", tags=["workorders"])


@router.get(
    "",
    response_model=ApiEnvelope[ListPayload[WorkOrderPayload]],
    summary="List work orders",
)
async def list_work_orders(
    request: Request,
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
    limit: int = Query(default=20, ge=1, le=100),
) -> ApiEnvelope[ListPayload[WorkOrderPayload]]:
    items = service.list_work_orders(limit=limit)
    return build_response(
        data=ListPayload[WorkOrderPayload](items=items, total=len(items)),
        request_id=request.state.request_id,
    )


@router.post(
    "",
    response_model=ApiEnvelope[WorkOrderPayload],
    status_code=status.HTTP_200_OK,
    summary="Create or promote a work order from detection result",
)
async def create_work_order(
    payload: CreateWorkOrderRequest,
    request: Request,
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
) -> ApiEnvelope[WorkOrderPayload]:
    work_order = service.create_work_order(payload)
    if work_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应的病害识别结果。")
    return build_response(data=work_order, request_id=request.state.request_id)


@router.patch(
    "/{work_order_id}/status",
    response_model=ApiEnvelope[WorkOrderPayload],
    summary="Update work order status",
)
async def update_work_order_status(
    work_order_id: str,
    payload: UpdateWorkOrderStatusRequest,
    request: Request,
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
) -> ApiEnvelope[WorkOrderPayload]:
    work_order = service.update_work_order_status(work_order_id, payload)
    if work_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="æœªæ‰¾åˆ°å¯¹åº”çš„å·¥å•ã€‚")
    return build_response(data=work_order, request_id=request.state.request_id)


@router.get(
    "/{work_order_id}",
    response_model=ApiEnvelope[WorkOrderPayload],
    summary="Read one work order",
)
async def read_work_order(
    work_order_id: str,
    request: Request,
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
) -> ApiEnvelope[WorkOrderPayload]:
    work_order = service.get_work_order(work_order_id)
    if work_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应的工单。")
    return build_response(data=work_order, request_id=request.state.request_id)
