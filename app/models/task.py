"""SQLAlchemy ORM model for Tasks."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(String(36), unique=True, index=True, default=generate_uuid, nullable=False)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Priority: low, medium, high, urgent
    priority = Column(String(20), default="medium", nullable=False, index=True)
    
    # Category: personal, study, work, health, finance, etc.
    category = Column(String(50), default="personal", nullable=False, index=True)
    
    # Status: pending, in_progress, completed, archived
    status = Column(String(20), default="pending", nullable=False, index=True)
    done = Column(Boolean, default=False, nullable=False, index=True)
    
    # Due date formatted as YYYY-MM-DD
    due = Column(String(50), nullable=True, index=True)
    
    # AI Assisted attributes
    is_ai_generated = Column(Boolean, default=False, nullable=False)
    ai_reasoning = Column(Text, nullable=True)
    
    # JSON serialized list of subtasks: [{"id": "...", "title": "...", "done": false}]
    subtasks = Column(Text, default="[]", nullable=False)
    
    # Recurrence: none, daily, weekly, monthly
    recurrence = Column(String(20), default="none", nullable=False)
    
    # Soft deletion / Archiving
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        """Serialize model to dictionary."""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "category": self.category,
            "status": self.status,
            "done": self.done,
            "due": self.due,
            "is_ai_generated": self.is_ai_generated,
            "ai_reasoning": self.ai_reasoning,
            "subtasks": self.subtasks,
            "recurrence": self.recurrence,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
