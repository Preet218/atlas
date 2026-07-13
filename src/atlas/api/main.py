from contextlib import asynccontextmanager

from fastapi import FastAPI

from atlas.api.routes.health import router as health_router
from atlas.config.settings import get_settings
from atlas.utils.logger import configure_logger

logger = configure_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    logger.info("Atlas shutdown complete")

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(health_router)
