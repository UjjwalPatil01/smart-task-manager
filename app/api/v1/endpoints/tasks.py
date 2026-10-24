"""Tasks CRUD endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStats
from app.services.task_service import TaskService

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
def read_tasks(
    search: Optional[str] = Query(None, description="Search in title, description, or category"),
    status: Optional[str] = Query(None, description="Filter by status: pending, completed, archived"),
    done: Optional[bool] = Query(None, description="Filter by completed boolean"),
    priority: Optional[str] = Query(None, description="Filter by priority: low, medium, high, urgent"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_archived: bool = Query(False, description="Include archived tasks"),
    sort_by: Optional[str] = Query(None, description="Sort field: due, priority, created_at"),
    order: str = Query("asc", description="Sort order: asc or desc"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Retrieve tasks with multi-field filtering and sorting."""
    tasks, _ = TaskService.list_tasks(
        db=db,
        search=search,
        status=status,
        done=done,
        priority=priority,
        category=category,
        is_archived=is_archived,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset
    )
    return tasks

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    return TaskService.create_task(db=db, task_in=task_in)

@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """Get single task by ID."""
    task = TaskService.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    """Update task details."""
    task = TaskService.update_task(db, task_id=task_id, task_in=task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}/toggle", response_model=TaskResponse)
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    """Toggle completion status of a task."""
    task = TaskService.toggle_done(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int,
    permanent: bool = Query(False, description="Permanently delete or soft-archive"),
    db: Session = Depends(get_db)
):
    """Delete a task (defaults to soft-delete/archive)."""
    success = TaskService.delete_task(db, task_id=task_id, permanent=permanent)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success", "message": f"Task {task_id} {'permanently deleted' if permanent else 'archived'}."}

@router.post("/seed-legacy", status_code=status.HTTP_200_OK)
def seed_legacy(db: Session = Depends(get_db)):
    """Manually trigger seeding from tasks.json if database is unseeded."""
    count = TaskService.seed_from_legacy_json(db)
    return {"status": "success", "imported_count": count}
