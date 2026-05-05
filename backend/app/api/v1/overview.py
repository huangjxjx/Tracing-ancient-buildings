from typing import Annotated

from fastapi import APIRouter, Depends, Request

from backend.app.modules.overview.schemas import OverviewPagePayload
from backend.app.modules.overview.service import OverviewPageService, get_overview_page_service
from backend.app.schemas.common import ApiEnvelope, build_response

router = APIRouter(prefix="/pages", tags=["overview"])


@router.get(
    "/overview",
    response_model=ApiEnvelope[OverviewPagePayload],
    summary="Get overview page aggregate payload",
)
async def read_overview_page(
    request: Request,
    service: Annotated[OverviewPageService, Depends(get_overview_page_service)],
) -> ApiEnvelope[OverviewPagePayload]:
    payload = service.get_page_payload()
    return build_response(data=payload, request_id=request.state.request_id)
