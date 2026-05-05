from typing import Annotated, Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from backend.app.core.config import Settings, get_settings
from backend.app.db.session import get_db_session


def get_request_id(request: Request) -> str:
    return str(getattr(request.state, "request_id", ""))


SettingsDep = Annotated[Settings, Depends(get_settings)]
RequestIdDep = Annotated[str, Depends(get_request_id)]
DbSessionDep = Annotated[Session, Depends(get_db_session)]


def get_db() -> Generator[Session, None, None]:
    yield from get_db_session()
