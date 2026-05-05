from pydantic import Field

from backend.app.schemas.common import SchemaModel


class PresignUploadRequest(SchemaModel):
    filename: str
    content_type: str = Field(alias="contentType")
    biz_type: str = Field(alias="bizType")


class PresignUploadPayload(SchemaModel):
    asset_id: str = Field(alias="assetId")
    upload_url: str = Field(alias="uploadUrl")
    object_key: str = Field(alias="objectKey")
    method: str = "PUT"


class UploadAssetPayload(SchemaModel):
    asset_id: str = Field(alias="assetId")
    filename: str
    content_type: str = Field(alias="contentType")
    file_size: int = Field(alias="fileSize")
    object_key: str = Field(alias="objectKey")
    upload_status: str = Field(alias="uploadStatus")
