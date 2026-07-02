"""Engine and session factory helpers."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings, get_settings


def create_engine_from_url(database_url: str, echo: bool = False) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, echo=echo, future=True, connect_args=connect_args)


def create_engine_from_settings(settings: Settings | None = None) -> Engine:
    resolved_settings = settings or get_settings()
    return create_engine_from_url(
        resolved_settings.database_url,
        echo=resolved_settings.database_echo,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@contextmanager
def session_scope(engine: Engine) -> Iterator[Session]:
    factory = create_session_factory(engine)
    session = factory()
    try:
        yield session
    finally:
        session.close()
