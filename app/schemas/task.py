"""Pydantic schemas for request validation and response serialization."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class SubTask(BaseModel):
    id: str = Field(..., description="Unique subtask ID")
    title: str = Field(..., min_length=1, max_length=255)
    done: bool = False

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task notes or details")
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")
    category: str = Field("personal", min_length=1, max_length=50)
    due: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")
    recurrence: str = Field("none", pattern="^(none|daily|weekly|monthly)$")

class TaskCreate(TaskBase):
    is_ai_generated: bool = False
    ai_reasoning: Optional[str] = None
    subtasks: List[SubTask] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|archived)$")
    done: Optional[bool] = None
    due: Optional[str] = None
    recurrence: Optional[str] = Field(None, pattern="^(none|daily|weekly|monthly)$")
    is_archived: Optional[bool] = None
    ai_reasoning: Optional[str] = None
    subtasks: Optional[List[SubTask]] = None

class TaskResponse(TaskBase):
    id: int
    uuid: str
    status: str
    done: bool
    is_ai_generated: bool
    ai_reasoning: Optional[str] = None
    subtasks: str = "[]"
    is_archived: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TaskStats(BaseModel):
    total: int
    completed: int
    pending: int
    overdue: int
    high_priority: int
    completion_rate: float
    categories: Dict[str, int]
    priorities: Dict[str, int]

class AISuggestionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class AISuggestionResponse(BaseModel):
    priority: str
    reasoning: str
    suggested_category: str
    offline_fallback: bool = False

class AIDecomposeRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class AIDecomposeResponse(BaseModel):
    subtasks: List[str]
    offline_fallback: bool = False

class AIInsightResponse(BaseModel):
    summary: str
    actionable_recommendations: List[str]
    productivity_score: int
    offline_fallback: bool = False
