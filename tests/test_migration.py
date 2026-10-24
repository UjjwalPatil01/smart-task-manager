"""Tests for legacy data preservation, seeding, and migration."""
import json
import os
from app.models.task import Task
from app.services.task_service import TaskService

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "synthetic_tasks.json")

def test_synthetic_seed_and_idempotency(db_session):
    """Verify seeding logic with hermetic, synthetic fixtures."""
    assert os.path.exists(FIXTURE_PATH), "Synthetic test fixture must exist"

    # Seed from synthetic fixture
    seeded_count = TaskService.seed_from_legacy_json(db_session, file_path=FIXTURE_PATH)
    assert seeded_count == 5, "All 5 synthetic tasks must be successfully seeded"

    # Query tasks from SQLite in-memory test database
    tasks = db_session.query(Task).all()
    assert len(tasks) == 5

    # Verify task attributes
    titles = [t.title for t in tasks]
    assert "Complete quarterly project review" in titles
    assert "Schedule dentist checkup" in titles
    assert "Prepare final exam study guide" in titles

    # Verify category and status mapping
    study_task = next(t for t in tasks if "study" in t.title.lower())
    assert study_task.category == "study"
    assert study_task.done is False

    done_task = next(t for t in tasks if t.title == "Schedule dentist checkup")
    assert done_task.done is True
    assert done_task.status == "completed"

    # Verify idempotency: seeding into non-empty database returns 0
    second_seed = TaskService.seed_from_legacy_json(db_session, file_path=FIXTURE_PATH)
    assert second_seed == 0

def test_local_legacy_data_integrity():
    """Optional validation: verify local legacy file format if present on developer drive."""
    local_legacy = "data/tasks_legacy.json"
    if os.path.exists(local_legacy):
        with open(local_legacy, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 7, "Local recovered legacy snapshot must retain exactly 7 tasks"

