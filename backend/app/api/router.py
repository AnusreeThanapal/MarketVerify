from fastapi import APIRouter
from backend.app.api.endpoints import claims, sources, health, auth, admin_data

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/api/v1")
api_router.include_router(claims.router, prefix="/api/v1")
api_router.include_router(sources.router, prefix="/api/v1")
api_router.include_router(admin_data.router, prefix="/api/v1")
