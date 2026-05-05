from typing import Annotated

from fastapi import APIRouter, Depends, Request

from backend.app.modules.knowledge.schemas import KnowledgePagePayload, KnowledgeRecommendation
from backend.app.modules.knowledge.service import KnowledgePageService, get_knowledge_page_service
from backend.app.schemas.common import ApiEnvelope, ListPayload, build_response

router = APIRouter(tags=["knowledge"])
pages_router = APIRouter(prefix="/pages")
knowledge_router = APIRouter(prefix="/knowledge")


@pages_router.get(
    "/knowledge",
    response_model=ApiEnvelope[KnowledgePagePayload],
    summary="Get knowledge page aggregate payload",
)
async def read_knowledge_page(
    request: Request,
    service: Annotated[KnowledgePageService, Depends(get_knowledge_page_service)],
) -> ApiEnvelope[KnowledgePagePayload]:
    payload = service.get_page_payload()
    return build_response(data=payload, request_id=request.state.request_id)


@knowledge_router.get(
    "/recommendations",
    response_model=ApiEnvelope[ListPayload[KnowledgeRecommendation]],
    summary="List knowledge recommendations generated from reviewed detection results",
)
async def list_knowledge_recommendations(
    request: Request,
    service: Annotated[KnowledgePageService, Depends(get_knowledge_page_service)],
) -> ApiEnvelope[ListPayload[KnowledgeRecommendation]]:
    items = service.list_recommendations()
    return build_response(
        data=ListPayload[KnowledgeRecommendation](items=items, total=len(items)),
        request_id=request.state.request_id,
    )


router.include_router(pages_router)
router.include_router(knowledge_router)
