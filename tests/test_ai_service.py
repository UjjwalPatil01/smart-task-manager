"""Unit tests for AIService and offline resilience."""
from app.services.ai_service import AIService

def test_suggest_priority_urgent_keyword():
    res = AIService.suggest_priority("Final semester exam preparation", "Must submit before 5pm")
    assert res["priority"] in ["high", "urgent"]
    assert "reasoning" in res
    assert res["suggested_category"] == "study"

def test_suggest_priority_routine():
    res = AIService.suggest_priority("Watch a casual movie", "Relaxation")
    assert res["priority"] == "low"
    assert "reasoning" in res

def test_decompose_task_fallback():
    res = AIService.decompose_task("Build full-stack web application")
    assert "subtasks" in res
    assert len(res["subtasks"]) >= 3
    assert isinstance(res["subtasks"], list)

def test_productivity_insights():
    summary_data = {
        "total": 10,
        "completed": 8,
        "pending": 2,
        "overdue": 0,
        "completion_rate": 80.0,
        "high_priority": 1
    }
    insights = AIService.generate_productivity_insights(summary_data)
    assert "summary" in insights
    assert "actionable_recommendations" in insights
    assert insights["productivity_score"] >= 70
