"""AI endpoints for Gemini-assisted workflows."""
from fastapi import APIRouter
from app.schemas.task import (
    AISuggestionRequest,
    AISuggestionResponse,
    AIDecomposeRequest,
    AIDecomposeResponse
)
from app.services.ai_service import AIService

router = APIRouter()

@router.get("/status")
def get_ai_status():
    """Return whether Gemini AI is configured and online."""
    configured = AIService.is_configured()
    return {
        "status": "online" if configured else "offline_fallback",
        "api_configured": configured,
        "message": "Gemini AI active" if configured else "Operating in resilient offline heuristic mode."
    }

@router.post("/suggest-priority", response_model=AISuggestionResponse)
def suggest_priority(payload: AISuggestionRequest):
    """Predict task priority and category with transparent reasoning."""
    result = AIService.suggest_priority(
        title=payload.title,
        description=payload.description
    )
    return AISuggestionResponse(**result)

@router.post("/decompose", response_model=AIDecomposeResponse)
def decompose_task(payload: AIDecomposeRequest):
    """Decompose a high-level task into actionable subtasks."""
    result = AIService.decompose_task(
        title=payload.title,
        description=payload.description
    )
    return AIDecomposeResponse(**result)
