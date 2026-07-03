"""Basic Auth helpers for the admin dashboard."""

from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import Settings
from app.dependencies import get_app_settings

basic_auth = HTTPBasic(auto_error=False)


def require_admin_auth(
    request: Request,
    credentials: Annotated[HTTPBasicCredentials | None, Depends(basic_auth)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> None:
    if credentials is None or settings is None:
        raise _auth_error()

    if not _is_valid_credentials(credentials.username, credentials.password, settings):
        raise _auth_error()

    request.state.admin_username = credentials.username


def _is_valid_credentials(username: str, password: str, settings: Settings) -> bool:
    if not settings.admin_username or not settings.admin_password:
        return False
    return secrets.compare_digest(username, settings.admin_username) and secrets.compare_digest(
        password, settings.admin_password
    )


def _auth_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Basic"},
    )
