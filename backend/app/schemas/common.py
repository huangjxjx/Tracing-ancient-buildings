from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class SchemaModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ApiEnvelope(SchemaModel, Generic[T]):
    code: str = "OK"
    message: str = ""
    request_id: str = Field(serialization_alias="requestId")
    data: T


class ListPayload(SchemaModel, Generic[T]):
    items: list[T]
    total: int


class HealthPayload(SchemaModel):
    status: str
    service: str
    version: str
    environment: str


def build_response(*, data: Any, request_id: str, message: str = "") -> ApiEnvelope[Any]:
    return ApiEnvelope[Any](
        message=message,
        request_id=request_id,
        data=data,
    )
