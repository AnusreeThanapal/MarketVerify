from fastapi import APIRouter
from sqlalchemy import text
from backend.app.schemas.common import HealthStatus
from backend.app.core.database import AsyncSessionLocal
from backend.app.core.redis_client import get_redis
from backend.app.core.qdrant_client import get_qdrant_service
from backend.app.core.logging import logger

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthStatus,
    summary="System Health Check",
    description="Validates connectivity to PostgreSQL, Redis, and Qdrant vector database.",
)
async def health_check() -> HealthStatus:
    # 1. Check PostgreSQL
    db_healthy = False
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_healthy = True
    except Exception as e:
        logger.debug(f"Health check DB error: {e}")
        db_healthy = False

    # 2. Check Redis
    redis_service = await get_redis()
    redis_healthy = await redis_service.is_healthy()

    # 3. Check Qdrant
    qdrant_service = get_qdrant_service()
    qdrant_healthy = await qdrant_service.is_healthy()

    overall_status = "healthy" if (db_healthy and redis_healthy and qdrant_healthy) else "degraded"

    return HealthStatus(
        status=overall_status,
        version="1.0.0",
        database=db_healthy,
        redis=redis_healthy,
        qdrant=qdrant_healthy,
    )
