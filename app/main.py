from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.intake import router as intake_router
from app.config import get_settings
from app.db.init_db import create_all
from app.db.session import create_engine_from_settings, create_session_factory
from app.services.worker import InProcessWorker


def create_app(settings=None) -> FastAPI:
    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = create_engine_from_settings(resolved_settings)
        create_all(engine)
        app.state.settings = resolved_settings
        app.state.engine = engine
        app.state.session_factory = create_session_factory(engine)
        app.state.worker = None
        if resolved_settings.worker_autostart:
            worker = InProcessWorker(
                app.state.session_factory,
                resolved_settings,
                poll_interval_seconds=resolved_settings.worker_poll_interval_seconds,
                batch_size=resolved_settings.worker_batch_size,
            )
            app.state.worker = worker
            worker.start()
        try:
            yield
        finally:
            worker = getattr(app.state, "worker", None)
            if worker is not None:
                worker.stop()
            engine.dispose()

    app = FastAPI(
        title=resolved_settings.app_name,
        debug=resolved_settings.debug,
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(intake_router)
    return app


app = create_app()
