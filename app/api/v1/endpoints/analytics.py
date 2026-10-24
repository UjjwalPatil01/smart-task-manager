"""Analytics and productivity insights endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.task import TaskStats, AIInsightResponse
from app.services.task_service import TaskService
from app.services.ai_service import AIService

router = APIRouter()

@router.get("/stats", response_model=TaskStats)
def get_task_statistics(db: Session = Depends(get_db)):
    """Fetch live completion, overdue, and category metrics."""
    return TaskService.get_stats(db)

@router.get("/insights", response_model=AIInsightResponse)
def get_productivity_insights(db: Session = Depends(get_db)):
    """Generate productivity review and recommendations based on task metrics."""
    stats = TaskService.get_stats(db)
    insights = AIService.generate_productivity_insights(stats.model_dump())
    return AIInsightResponse(**insights)
