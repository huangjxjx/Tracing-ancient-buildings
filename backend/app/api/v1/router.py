from importlib import import_module
from pathlib import Path

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from backend.app.core.config import get_settings
from backend.app.schemas.common import ApiEnvelope, build_response


class RouteSlot(BaseModel):
    name: str
    summary: str
    route_file: str = Field(serialization_alias="routeFile")
    module_dir: str = Field(serialization_alias="moduleDir")
    module_package: str = Field(serialization_alias="modulePackage")
    mount_path: str = Field(serialization_alias="mountPath")
    registered: bool


class ApiRegistryPayload(BaseModel):
    service: str
    version: str
    modules: list[RouteSlot]


PLANNED_ROUTE_SLOTS: tuple[RouteSlot, ...] = (
    RouteSlot(
        name="overview",
        summary="Overview page aggregate endpoint slot.",
        route_file="backend/app/api/v1/overview.py",
        module_dir="backend/app/modules/overview",
        module_package="backend.app.modules.overview",
        mount_path="/pages/overview",
        registered=False,
    ),
    RouteSlot(
        name="twin",
        summary="Twin workspace aggregate endpoint slot.",
        route_file="backend/app/api/v1/twin.py",
        module_dir="backend/app/modules/twin",
        module_package="backend.app.modules.twin",
        mount_path="/pages/twin",
        registered=False,
    ),
    RouteSlot(
        name="detection",
        summary="Detection batch endpoints slot.",
        route_file="backend/app/api/v1/detection.py",
        module_dir="backend/app/modules/detection",
        module_package="backend.app.modules.detection",
        mount_path="/detection",
        registered=False,
    ),
)


def _iter_route_modules() -> list[str]:
    route_dir = Path(__file__).resolve().parent
    return sorted(
        file_path.stem
        for file_path in route_dir.glob("*.py")
        if file_path.stem not in {"__init__", "router"} and not file_path.stem.startswith("_")
    )


def _register_feature_routers(api_router: APIRouter) -> dict[str, APIRouter]:
    registered_modules: dict[str, APIRouter] = {}
    for module_name in _iter_route_modules():
        module = import_module(f"{__package__}.{module_name}")
        module_router = getattr(module, "router", None)
        if isinstance(module_router, APIRouter):
            api_router.include_router(module_router)
            registered_modules[module_name] = module_router
    return registered_modules


def _build_registry_payload(registered_modules: dict[str, APIRouter]) -> ApiRegistryPayload:
    settings = get_settings()
    planned = {slot.name: slot for slot in PLANNED_ROUTE_SLOTS}
    modules: list[RouteSlot] = []

    for name, slot in planned.items():
        registered = name in registered_modules
        modules.append(
            RouteSlot(
                name=slot.name,
                summary=slot.summary,
                route_file=slot.route_file,
                module_dir=slot.module_dir,
                module_package=slot.module_package,
                mount_path=slot.mount_path,
                registered=registered,
            )
        )

    for name, module_router in sorted(registered_modules.items()):
        if name in planned:
            continue
        modules.append(
            RouteSlot(
                name=name,
                summary="Auto-discovered API router.",
                route_file=f"backend/app/api/v1/{name}.py",
                module_dir=f"backend/app/modules/{name}",
                module_package=f"backend.app.modules.{name}",
                mount_path=module_router.prefix or "/",
                registered=True,
            )
        )

    return ApiRegistryPayload(
        service=settings.app_name,
        version=settings.app_version,
        modules=modules,
    )


def build_api_router() -> APIRouter:
    api_router = APIRouter(tags=["v1"])
    registered_modules = _register_feature_routers(api_router)

    @api_router.get("", response_model=ApiEnvelope[ApiRegistryPayload], summary="API registry")
    async def read_api_registry(request: Request):
        payload = _build_registry_payload(registered_modules)
        return build_response(data=payload, request_id=request.state.request_id)

    return api_router


router = build_api_router()
