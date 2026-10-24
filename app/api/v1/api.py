"""Root router for API v1."""
from fastapi import APIRouter
from app.api.v1.endpoints import tasks, ai, analytics

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
