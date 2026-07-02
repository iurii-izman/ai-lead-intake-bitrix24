"""Shared FastAPI dependencies."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import Session

from app.config import Settings, get_settings


def get_app_settings(request: Request) -> Settings:
    return getattr(request.app.state, "settings", get_settings())


def get_db_session(request: Request) -> Iterator[Session]:
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        raise RuntimeError("Database session factory is not initialized.")

    session = session_factory()
    try:
        yield session
    finally:
        session.close()
