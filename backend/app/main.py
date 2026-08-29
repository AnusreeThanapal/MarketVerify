import json
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func

from backend.app.config import get_settings
from backend.app.core.logging import logger
from backend.app.core.database import engine, Base, AsyncSessionLocal
from backend.app.core.redis_client import redis_service
from backend.app.core.qdrant_client import qdrant_service
from backend.app.models.source_trajectory import SourceTrajectory
from backend.app.api.router import api_router
from backend.ingestion.run_all_ingestions import run_all

settings = get_settings()


async def seed_source_trajectories_if_empty():
    """Seeds SourceTrajectory table from seed_trust_tier.json if currently empty."""
    try:
        async with AsyncSessionLocal() as session:
            count_res = await session.execute(select(func.count(SourceTrajectory.id)))
            count = count_res.scalar_one()
            if count == 0:
                logger.info("Seeding initial Source Trajectories into database...")
                seed_path = os.path.join(
                    Path(__file__).parent.parent, "data", "seed_trust_tier.json"
                )
                with open(seed_path, "r", encoding="utf-8") as f:
                    records = json.load(f)

                from datetime import datetime, timezone
                for item in records:
                    t = SourceTrajectory(
                        id=item["id"],
                        source_handle=item["source_handle"],
                        source_name=item.get("source_name"),
                        past_claim_text=item["past_claim_text"],
                        ticker=item.get("ticker"),
                        was_accurate=item["was_accurate"],
                        lag_hours=item.get("lag_hours", 24),
                        category=item.get("category", "rumor"),
                        outcome_summary=item["outcome_summary"],
                        outcome_date=datetime.fromisoformat(item["outcome_date"].replace("Z", "+00:00")),
                        recorded_at=datetime.now(timezone.utc),
                    )
                    session.add(t)
                await session.commit()
                logger.info(f"Seeded {len(records)} source trajectories successfully.")
    except Exception as e:
        logger.warning(f"Could not seed source trajectories: {e}")


from backend.scripts.seed_demo_users import seed_demo_users_and_claims

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} backend...")
    
    # 1. Connect to Redis
    await redis_service.connect()

    # 2. Ensure Qdrant collections are initialized
    await qdrant_service.init_collections()

    # 3. Create database tables if not existing and seed users/claims
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schemas initialized.")
        await seed_source_trajectories_if_empty()
        await seed_demo_users_and_claims()
    except Exception as e:
        logger.warning(f"Could not automatically sync database schemas or seed demo accounts: {e}")

    # 4. Ingest seed data into Qdrant collections
    try:
        run_all()
    except Exception as e:
        logger.warning(f"Initial Qdrant ingestion warning: {e}")

    yield

    # Cleanup
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
    await redis_service.close()
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=(
            "Multi-agent, retrieval-grounded system that verifies Indian stock-market "
            "rumors and claims (in English & Tamil) against official SEBI/exchange filings, "
            "source credibility trajectories, and market sentiment dynamics using LangGraph."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API Routes
    app.include_router(api_router)

    @app.get("/", summary="MarketVerify Root Status")
    async def root():
        return {
            "name": "MarketVerify Backend API",
            "version": "1.0.0",
            "status": "operational",
            "documentation": "/docs",
            "health": "/health",
            "claims_api": "/api/v1/claims",
            "frontend_ui": "http://localhost:3005",
        }

    # Global Exception Handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global unhandled exception on {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(exc) if settings.DEBUG else "An unexpected error occurred.",
            },
        )

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
