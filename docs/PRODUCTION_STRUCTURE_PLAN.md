# Phase 5: Production-Ready Project Structure Optimization Plan
**Document Name:** `docs/PRODUCTION_STRUCTURE_PLAN.md`  
**Repository:** `https://github.com/UjjwalPatil01/smart-task-manager`  
**Working Branch:** `modernization-v2`  
**Status:** Approved & Implemented

---

## Executive Summary

The **Smart Task Manager** repository has undergone major modernization: transitioning from a single-file Flask application with JSON file storage to a modular, high-performance architecture utilizing **FastAPI**, **SQLAlchemy 2.0 (SQLite WAL mode)**, **Streamlit**, and **Google Gemini AI**. All original user data (7 tasks) has been verified and preserved, and the test suite reports 10 passing tests.

Structural reorganization addresses:
1. **Module/Package Collision Hazard:** Root-level `app.py` is safely archived into `legacy_flask/` and `delete_folder/`, eliminating import shadowing with the `app/` Python package.
2. **Personal User Data Tracked in Git:** Root `tasks.json` is untracked via `git rm --cached tasks.json` while remaining preserved locally on disk.
3. **Untracked Personal Data Vulnerability:** `data/tasks_legacy.json` is protected via updated `.gitignore` rules (`data/*.json`, `!data/tasks.example.json`).
4. **Hermetic Test Isolation:** Tests are refactored to utilize synthetic test fixtures (`tests/fixtures/synthetic_tasks.json`), decoupling the test suite from private user task history.
5. **Modern Packaging & Tooling Standard:** Added `pyproject.toml` and separated dev dependencies (`requirements-dev.txt`).

---

## Target Repository Structure

```
smart-task-manager/
├── .env.example                       # Application environment template
├── .gitignore                         # Comprehensive Git exclusion rules
├── README.md                          # Production documentation & setup guide
├── pyproject.toml                     # Modern Python project configuration & tool settings
├── requirements.txt                   # Core runtime dependencies (FastAPI, Streamlit, SQLAlchemy)
├── requirements-dev.txt               # Development & test tooling (pytest, ruff, mypy)
├── run.py                             # Unified application launcher (FastAPI + Streamlit)
│
├── app/                               # Core Backend Python Package (FastAPI)
│   ├── __init__.py                    # Package marker & version metadata
│   ├── config.py                      # Pydantic Settings application configuration
│   ├── main.py                        # FastAPI entrypoint, lifespan & health check
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py                 # API v1 central router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── ai.py              # AI assistant & decomposition endpoints
│   │           ├── analytics.py       # Metrics & summary stats endpoints
│   │           └── tasks.py           # Task CRUD & workflow endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── database.py                # Database connection, WAL pragmas, sessionmaker
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py                    # SQLAlchemy ORM models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py                    # Pydantic v2 validation & response models
│   └── services/
│       ├── __init__.py
│       ├── ai_service.py              # Gemini AI client with resilient heuristics fallback
│       └── task_service.py            # Business logic & transaction management
│
├── ui/                                # Frontend Dashboard Package (Streamlit)
│   └── streamlit_app.py               # Glassmorphic dark dashboard, charts, task UI
│
├── tests/                             # Automated Verification Suite
│   ├── __init__.py
│   ├── conftest.py                    # In-memory test SQLite fixtures & API client
│   ├── test_ai_service.py             # AIService logic & fallback tests
│   ├── test_api.py                    # FastAPI REST API integration tests
│   ├── test_migration.py              # Data seeding & migration verification tests
│   └── fixtures/                      # Hermetic, non-personal test fixtures
│       └── synthetic_tasks.json       # Synthetic task dataset for deterministic tests
│
├── scripts/                           # Safe Operational & DevOps Utilities
│   ├── __init__.py
│   ├── seed_data.py                   # Controlled CLI database seeder
│   └── verify_db.py                   # Read-only SQLite integrity & schema verifier
│
├── docs/                              # Project Documentation
│   ├── PRODUCTION_STRUCTURE_PLAN.md   # This comprehensive architectural plan
│   └── ARCHITECTURE.md                # System component diagram & data flow
│
├── data/                              # Local Runtime Data Directory (GIT-IGNORED)
│   ├── .gitkeep                       # Preserves directory in Git clones
│   ├── tasks.example.json             # Committed synthetic template for optional seeding
│   ├── tasks.db                       # Active SQLite database (LOCAL ONLY - IGNORED)
│   ├── tasks.db-wal                   # SQLite WAL journal (LOCAL ONLY - IGNORED)
│   ├── tasks.db-shm                   # SQLite shared memory (LOCAL ONLY - IGNORED)
│   └── tasks_legacy.json              # Recovered real user tasks (LOCAL ONLY - IGNORED)
│
├── legacy_flask/                      # Isolated Historical Reference (Non-Active)
│   ├── README.md                      # Historical documentation, architecture & known bugs
│   ├── app.py                         # Original Flask script (copied with SHA-256 verification)
│   ├── requirements.txt               # Legacy dependencies for running Flask standalone
│   ├── tasks.example.json             # Synthetic sample tasks for legacy testing
│   ├── static/
│   │   └── main.css                   # Original Flask CSS stylesheet
│   └── templates/
│       ├── index.html                 # Original Flask home page template
│       └── edit.html                  # Original Flask edit page template
│
└── delete_folder/                     # Non-destructive local archive (LOCAL ONLY - IGNORED)
    ├── README.md                      # Archive holding area notice
    ├── tasks.json                     # Original root user data file preserved locally
    └── app.py                         # Original root Flask script preserved locally
```
