from typing import Annotated

from fastapi import APIRouter, Depends, Request

from backend.app.modules.screen.schemas import ScreenPagePayload
from backend.app.modules.screen.service import ScreenPageService, get_screen_page_service
from backend.app.schemas.common import ApiEnvelope, build_response

router = APIRouter(prefix="/pages", tags=["screen"])


@router.get(
    "/screen",
    response_model=ApiEnvelope[ScreenPagePayload],
    summary="Get regional screen aggregate payload",
)
async def read_screen_page(
    request: Request,
    service: Annotated[ScreenPageService, Depends(get_screen_page_service)],
) -> ApiEnvelope[ScreenPagePayload]:
    payload = service.get_page_payload()
    return build_response(data=payload, request_id=request.state.request_id)
