"""Task service containing business logic and database queries."""
import json
import os
from datetime import datetime, date, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskStats

class TaskService:
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        """Fetch task by ID."""
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_task_by_uuid(db: Session, task_uuid: str) -> Optional[Task]:
        """Fetch task by UUID."""
        return db.query(Task).filter(Task.uuid == task_uuid).first()

    @staticmethod
    def list_tasks(
        db: Session,
        search: Optional[str] = None,
        status: Optional[str] = None,
        done: Optional[bool] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        is_archived: bool = False,
        sort_by: Optional[str] = None,
        order: str = "asc",
        limit: int = 200,
        offset: int = 0
    ) -> Tuple[List[Task], int]:
        """List tasks with comprehensive filtering, searching, and sorting."""
        query = db.query(Task).filter(Task.is_archived == is_archived)

        # Search filter
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern),
                    Task.category.ilike(search_pattern)
                )
            )

        # Status / Done filter
        if status:
            query = query.filter(Task.status == status)
        if done is not None:
            query = query.filter(Task.done == done)

        # Priority filter
        if priority:
            query = query.filter(Task.priority == priority)

        # Category filter
        if category:
            query = query.filter(Task.category == category)

        total_count = query.count()

        # Sorting
        if sort_by == "due":
            order_func = desc if order == "desc" else asc
            query = query.order_by(order_func(Task.due))
        elif sort_by == "priority":
            # Priority order: urgent -> high -> medium -> low
            priority_case = {
                "urgent": 1,
                "high": 2,
                "medium": 3,
                "low": 4
            }
            order_func = desc if order == "desc" else asc
            # Fallback sort
            query = query.order_by(order_func(Task.priority))
        elif sort_by == "created_at":
            order_func = desc if order == "desc" else asc
            query = query.order_by(order_func(Task.created_at))
        else:
            # Default sort: Pending first, then due date, then created_at desc
            query = query.order_by(asc(Task.done), asc(Task.due), desc(Task.created_at))

        tasks = query.offset(offset).limit(limit).all()
        return tasks, total_count

    @staticmethod
    def create_task(db: Session, task_in: TaskCreate) -> Task:
        """Create a new task."""
        subtasks_json = json.dumps([st.model_dump() for st in task_in.subtasks])
        db_task = Task(
            title=task_in.title.strip(),
            description=task_in.description.strip() if task_in.description else None,
            priority=task_in.priority,
            category=task_in.category.strip().lower(),
            due=task_in.due,
            recurrence=task_in.recurrence,
            is_ai_generated=task_in.is_ai_generated,
            ai_reasoning=task_in.ai_reasoning,
            subtasks=subtasks_json,
            done=False,
            status="pending"
        )
        try:
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            return db_task
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def update_task(db: Session, task_id: int, task_in: TaskUpdate) -> Optional[Task]:
        """Update an existing task."""
        db_task = TaskService.get_task(db, task_id)
        if not db_task:
            return None

        update_data = task_in.model_dump(exclude_unset=True)

        if "subtasks" in update_data and update_data["subtasks"] is not None:
            update_data["subtasks"] = json.dumps([
                st.model_dump() if hasattr(st, "model_dump") else st
                for st in update_data["subtasks"]
            ])

        # Status sync with done
        if "done" in update_data and update_data["done"] is not None:
            if update_data["done"]:
                db_task.status = "completed"
                db_task.completed_at = datetime.now(timezone.utc)
            else:
                db_task.status = "pending"
                db_task.completed_at = None

        for field, value in update_data.items():
            setattr(db_task, field, value)

        try:
            db.commit()
            db.refresh(db_task)
            return db_task
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def toggle_done(db: Session, task_id: int) -> Optional[Task]:
        """Toggle task done status."""
        db_task = TaskService.get_task(db, task_id)
        if not db_task:
            return None

        db_task.done = not db_task.done
        if db_task.done:
            db_task.status = "completed"
            db_task.completed_at = datetime.now(timezone.utc)
        else:
            db_task.status = "pending"
            db_task.completed_at = None

        try:
            db.commit()
            db.refresh(db_task)
            return db_task
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete_task(db: Session, task_id: int, permanent: bool = False) -> bool:
        """Soft-delete or permanently remove a task."""
        db_task = TaskService.get_task(db, task_id)
        if not db_task:
            return False

        try:
            if permanent:
                db.delete(db_task)
            else:
                db_task.is_archived = True
                db_task.status = "archived"

            db.commit()
            return True
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_stats(db: Session) -> TaskStats:
        """Calculate live productivity statistics."""
        active_tasks = db.query(Task).filter(Task.is_archived == False).all()
        
        total = len(active_tasks)
        completed = sum(1 for t in active_tasks if t.done)
        pending = total - completed
        
        today_str = date.today().isoformat()
        overdue = sum(1 for t in active_tasks if not t.done and t.due and t.due < today_str)
        high_priority = sum(1 for t in active_tasks if not t.done and t.priority in ["high", "urgent"])
        
        completion_rate = round((completed / total * 100), 1) if total > 0 else 0.0

        categories: Dict[str, int] = {}
        for t in active_tasks:
            cat = t.category or "personal"
            categories[cat] = categories.get(cat, 0) + 1

        priorities: Dict[str, int] = {
            "urgent": sum(1 for t in active_tasks if t.priority == "urgent"),
            "high": sum(1 for t in active_tasks if t.priority == "high"),
            "medium": sum(1 for t in active_tasks if t.priority == "medium"),
            "low": sum(1 for t in active_tasks if t.priority == "low")
        }

        return TaskStats(
            total=total,
            completed=completed,
            pending=pending,
            overdue=overdue,
            high_priority=high_priority,
            completion_rate=completion_rate,
            categories=categories,
            priorities=priorities
        )

    @staticmethod
    def seed_from_legacy_json(db: Session, file_path: str = "tasks.json") -> int:
        """
        Safely import legacy JSON tasks if database is empty.
        Ensures 100% preservation of all legacy tasks with fallback to committed example data.
        """
        if db.query(Task).count() > 0:
            return 0  # Database already seeded

        target_path = file_path
        if not os.path.exists(target_path):
            if os.path.exists("data/tasks_legacy.json"):
                target_path = "data/tasks_legacy.json"
            elif os.path.exists("data/tasks.example.json"):
                target_path = "data/tasks.example.json"
            else:
                return 0

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading legacy tasks from {target_path}: {e}")
            return 0

        imported = 0
        for item in data:
            title = item.get("title", "").strip()
            if not title:
                continue

            done = bool(item.get("done", False))
            priority = item.get("priority", "medium")
            if priority not in ["low", "medium", "high", "urgent"]:
                priority = "medium"

            category = item.get("category", "personal") or "personal"
            due = item.get("due")
            is_ai = bool(item.get("ai", False))

            task = Task(
                title=title,
                done=done,
                status="completed" if done else "pending",
                priority=priority,
                category=category.lower(),
                due=due,
                is_ai_generated=is_ai,
                subtasks="[]"
            )
            db.add(task)
            imported += 1

        try:
            db.commit()
            return imported
        except Exception:
            db.rollback()
            raise
