from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from backend.app.modules.twin.schemas import TwinPagePayload
from backend.app.modules.twin.service import TwinPageService, TwinSiteNotFoundError, get_twin_page_service
from backend.app.schemas.common import ApiEnvelope, build_response

router = APIRouter(prefix="/pages", tags=["twin"])


@router.get(
    "/twin",
    response_model=ApiEnvelope[TwinPagePayload],
    summary="Get twin workspace aggregate payload",
    response_description="Twin page aggregate payload with site, scene nodes, components, and damage points.",
)
async def read_twin_page(
    request: Request,
    site_id: Annotated[
        str,
        Query(alias="siteId", min_length=1, description="Ancient building site identifier, such as site_001."),
    ],
    service: Annotated[TwinPageService, Depends(get_twin_page_service)],
):
    try:
        payload = service.get_page_payload(site_id)
    except TwinSiteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到编号为 {exc.site_id} 的古建站点。",
        ) from exc

    return build_response(data=payload, request_id=request.state.request_id)
