from fastapi import APIRouter
from sqlalchemy import text

from atlas.database.session import engine

router = APIRouter(tags=["Database"])


@router.get("/health/db")
async def database_health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "postgres"}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}
