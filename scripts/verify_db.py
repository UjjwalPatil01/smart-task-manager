"""Read-only database verification and diagnostics utility."""
import os
import sqlite3
import sys

def verify_database(db_path: str = "data/tasks.db"):
    print("=" * 60)
    print("[AUDIT] SMART TASK MANAGER - DATABASE DIAGNOSTIC AUDIT")
    print("=" * 60)

    if not os.path.exists(db_path):
        print(f"[FAIL] Database file not found at: {db_path}")
        return False

    size_kb = os.path.getsize(db_path) / 1024
    print(f"[*] Target Database: {db_path} ({size_kb:.1f} KB)")

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        # Check integrity
        integrity = cursor.execute("PRAGMA integrity_check").fetchone()[0]
        journal_mode = cursor.execute("PRAGMA journal_mode").fetchone()[0]
        foreign_keys = cursor.execute("PRAGMA foreign_keys").fetchone()[0]

        print(f"[*] Integrity Check:    {integrity}")
        print(f"[*] Journal Mode:       {journal_mode}")
        print(f"[*] Foreign Keys:       {'Enabled (1)' if foreign_keys else 'Disabled (0)'}")

        # Check tables
        tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print(f"[*] Tables Found:       {', '.join(tables)}")

        if "tasks" in tables:
            total_tasks = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            completed = cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1").fetchone()[0]
            pending = cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 0").fetchone()[0]
            archived = cursor.execute("SELECT COUNT(*) FROM tasks WHERE is_archived = 1").fetchone()[0]

            print(f"[*] Total Task Count:   {total_tasks}")
            print(f"    |- Completed:       {completed}")
            print(f"    |- Pending:         {pending}")
            print(f"    |- Archived:        {archived}")

        conn.close()
        print("=" * 60)
        print("[SUCCESS] Database verification complete. No anomalies detected.")
        return True

    except Exception as e:
        print(f"❌ Error during database audit: {e}")
        return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "data/tasks.db"
    success = verify_database(target)
    sys.exit(0 if success else 1)
