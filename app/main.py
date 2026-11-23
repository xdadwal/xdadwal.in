import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from datetime import timedelta

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import LOGPOSE_REQUIRED_ENV, get_settings, missing_logpose_env
from app.routes import assistant, blog, home, projects
from app.services.assistant import build_runtime, cleanup_loop, close_runtime

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.assistant = None
    if not settings.assistant_enabled:
        missing = missing_logpose_env()
        if len(missing) < len(LOGPOSE_REQUIRED_ENV):
            # Partly configured is almost certainly a mistake; say which variables are missing.
            logger.warning("assistant disabled: %s not set", ", ".join(missing))
        yield
        return

    runtime = build_runtime(settings)
    app.state.assistant = runtime
    retention = timedelta(days=settings.assistant_retention_days)
    cleanup = asyncio.create_task(cleanup_loop(runtime.agent, retention))
    try:
        yield
    finally:
        cleanup.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup
        await close_runtime(runtime)


app = FastAPI(title="xdadwal.in", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(projects.router)
app.include_router(blog.router)
app.include_router(assistant.router)
