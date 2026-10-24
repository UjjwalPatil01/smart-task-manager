"""Controlled database seeding utility for Smart Task Manager."""
import argparse
import os
import sys

# Ensure root directory is on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.core.database import SessionLocal, Base, engine
from app.models.task import Task
from app.services.task_service import TaskService

def seed(source_json: str, force: bool = False):
    print("=" * 60)
    print("[SEED] SMART TASK MANAGER - DATABASE SEED UTILITY")
    print("=" * 60)

    if not os.path.exists(source_json):
        print(f"[FAIL] Source JSON file not found: {source_json}")
        return False

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        current_count = db.query(Task).count()
        print(f"[*] Current task count in database: {current_count}")

        if current_count > 0 and not force:
            print("[WARN] Database already contains tasks. Seeding skipped to preserve existing data.")
            print("       (Use --force only if you wish to append tasks non-destructively).")
            return True

        count = TaskService.seed_from_legacy_json(db, file_path=source_json)
        print(f"[SUCCESS] Successfully seeded {count} tasks from {source_json}.")
        return True
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Smart Task Manager database from JSON")
    parser.add_argument("--source", default="data/tasks.example.json", help="Path to source JSON file")
    parser.add_argument("--force", action="store_true", help="Force append even if DB is not empty")
    args = parser.parse_args()

    success = seed(args.source, force=args.force)
    sys.exit(0 if success else 1)
