from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import get_settings
from backend.app.db.base import Base


def _build_engine_options(database_url: str) -> dict[str, object]:
    options: dict[str, object] = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
    return options


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, **_build_engine_options(settings.database_url))


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    import backend.app.modules.detection.models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
    _migrate_sqlite_media_assets()
    _migrate_sqlite_detection_execution_columns()


def _migrate_sqlite_media_assets() -> None:
    engine = get_engine()
    if engine.dialect.name != "sqlite":
        return

    required_columns = {
        "content_type": "VARCHAR(128)",
        "file_size": "INTEGER",
        "object_key": "VARCHAR(512)",
        "storage_path": "VARCHAR(1024)",
        "upload_status": "VARCHAR(32)",
    }
    with engine.begin() as connection:
        existing_columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(media_assets)")).fetchall()
        }
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE media_assets ADD COLUMN {column_name} {column_type}"))


def _migrate_sqlite_detection_execution_columns() -> None:
    engine = get_engine()
    if engine.dialect.name != "sqlite":
        return

    table_columns = {
        "detection_batches": {
            "started_at": "DATETIME",
            "completed_at": "DATETIME",
            "failed_at": "DATETIME",
            "error_message": "TEXT",
        },
        "detection_tasks": {
            "started_at": "DATETIME",
            "completed_at": "DATETIME",
            "failed_at": "DATETIME",
            "error_message": "TEXT",
        },
    }
    with engine.begin() as connection:
        for table_name, required_columns in table_columns.items():
            existing_columns = {
                row[1]
                for row in connection.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
            }
            for column_name, column_type in required_columns.items():
                if column_name not in existing_columns:
                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
