from fastapi import APIRouter

from atlas.config.settings import get_settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
