# Smart Task Manager — AI-Powered Task Management 🚀

A modern, production-grade task intelligence application built with **FastAPI, Streamlit, SQLAlchemy 2.0, and Google Gemini**. Combines enterprise-grade REST API architecture with an interactive analytical dashboard and resilient AI-assisted productivity workflows.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg)](https://streamlit.io/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Tests-10%20Passed-brightgreen.svg)](https://pytest.org/)

---

## 🌟 Highlights & Key Features

- 🧠 **Resilient Gemini AI Engine:**
  - Automatic task priority suggestion with transparent, explainable reasoning.
  - One-click **AI Task Breakdown**: Decomposes complex goals into 3–5 actionable subtasks.
  - **AI Productivity Coach:** Generates weekly completion assessments and actionable focus recommendations.
  - **Bulletproof Offline Fallback:** If an API key is missing or network times out, intelligent keyword heuristics take over seamlessly without crashing.
- ⚡ **Production-Ready REST API (FastAPI):**
  - Fully typed Pydantic v2 validation models.
  - Interactive OpenAPI/Swagger documentation at `/docs`.
  - Permanent UUID & integer identifiers (permanently solving array-index mismatch bugs).
  - Search across titles, notes, and categories.
  - Multi-attribute filtering (priority, status, categories, overdue).
- 🎨 **Polished Streamlit Dashboard:**
  - Modern dark-mode UI with sleek glassmorphism and custom CSS.
  - Real-time productivity metrics: Total Tasks, Completed, Pending, Overdue, and Velocity.
  - Interactive task checklist with subtask tracking.
  - Interactive visual analytics powered by Altair (Category donut charts, Priority bars).
  - One-click CSV and JSON data export.
- 🛡️ **Zero Data-Loss Storage & Reliability:**
  - Relational SQLite persistence with WAL (Write-Ahead Logging) mode and foreign keys enabled.
  - Non-destructive legacy data migration: Preserves all recovered legacy tasks with 100% data fidelity.
  - Soft-delete (archiving) support to prevent accidental permanent deletions.

---

## 🏛️ System Architecture

```text
┌────────────────────────────────────────────────────────┐
│             Streamlit Dashboard (Frontend)             │
│        Interactive Kanban, KPI Metrics & Charts        │
│                 http://localhost:8501                  │
└───────────────────────────┬────────────────────────────┘
                            │ REST API Client
                            ▼
┌────────────────────────────────────────────────────────┐
│               FastAPI Backend (REST API)               │
│        Pydantic Validation & Swagger Docs (/docs)      │
│                 http://localhost:8000                  │
└─────────────┬───────────────────────────┬──────────────┘
              │                           │
┌─────────────▼─────────────┐ ┌───────────▼──────────────┐
│       SQLAlchemy 2.0      │ │    Resilient AI Engine   │
│     SQLite (WAL Mode)     │ │  Google Gemini REST API  │
│  data/tasks.db (Persistent)│ │  + Offline Heuristics   │
└───────────────────────────┘ └──────────────────────────┘
```

---

## 📁 Project Structure

```text
smart-task-manager/
├── .env.example              # Environment configuration template
├── .gitignore                # Comprehensive Git exclusion rules
├── README.md                 # Complete system documentation
├── pyproject.toml            # Project configuration & tool settings (pytest, ruff, mypy)
├── requirements.txt          # Core production dependencies
├── requirements-dev.txt      # Development & testing tooling
├── run.py                    # Unified single-command launcher
│
├── app/                      # Backend REST API Package (FastAPI)
│   ├── config.py             # Pydantic Settings configuration
│   ├── main.py               # FastAPI app factory & lifespan
│   ├── core/
│   │   └── database.py       # SQLAlchemy engine & SQLite WAL configuration
│   ├── models/
│   │   └── task.py           # Task ORM model (UUIDs, timestamps, subtasks)
│   ├── schemas/
│   │   └── task.py           # Pydantic v2 validation schemas
│   ├── services/
│   │   ├── task_service.py   # Business logic, queries, and legacy seed
│   │   └── ai_service.py     # Gemini client with offline heuristics fallback
│   └── api/
│       └── v1/
│           ├── api.py        # API router registration
│           └── endpoints/    # Tasks, AI, and Analytics endpoints
│
├── ui/                       # Frontend Dashboard (Streamlit)
│   └── streamlit_app.py      # Streamlit interactive dashboard with Altair analytics
│
├── scripts/                  # Operations & Maintenance Utilities
│   ├── verify_db.py          # Read-only database diagnostic & integrity audit
│   └── seed_data.py          # Controlled CLI database seeder
│
├── docs/                     # Project Documentation
│   ├── ARCHITECTURE.md       # Component architecture & data flow diagrams
│   └── PRODUCTION_STRUCTURE_PLAN.md # Structure optimization plan
│
├── legacy_flask/             # Isolated Historical Flask App (Reference)
│   ├── app.py                # Original Flask application
│   ├── README.md             # Legacy documentation & run instructions
│   ├── static/main.css       # Original stylesheet
│   └── templates/            # Original Jinja2 templates
│
├── data/                     # Local Runtime Data (Git-Ignored)
│   ├── tasks.example.json    # Committed synthetic template for new clones
│   └── tasks.db              # Active SQLite database (WAL mode, ignored)
│
├── delete_folder/            # Non-destructive local archive (Git-ignored)
│
└── tests/                    # Automated Verification Suite
    ├── conftest.py           # In-memory SQLite fixtures & TestClient
    ├── test_api.py           # API integration tests
    ├── test_ai_service.py    # AI heuristic & decomposition tests
    ├── test_migration.py     # Data preservation & idempotency tests
    └── fixtures/
        └── synthetic_tasks.json # Synthetic non-personal test data
```

---

## 🚀 Quick Start Guide

### 1. Clone Repository & Setup Virtual Environment

```bash
git clone https://github.com/UjjwalPatil01/smart-task-manager.git
cd smart-task-manager

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables (Optional)

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

To enable live Gemini AI classification and decomposition, add your Google API key:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

*(If no key is configured, the system automatically runs in Resilient Offline Mode using keyword heuristics).*

### 4. Run the Full Application (Single Command)

```bash
python run.py
```

- **Interactive Dashboard:** `http://localhost:8501`
- **FastAPI REST API Docs:** `http://localhost:8000/docs`
- **API Health Check:** `http://localhost:8000/`

You can also run components independently:
- **API Only:** `python run.py --api-only`
- **UI Only:** `python run.py --ui-only`

---

## 🧪 Running Automated Tests

A comprehensive `pytest` test suite is included, verifying API routes, AI offline fallbacks, and data migration preservation:

```bash
pytest -v
# or via runner:
python run.py --test
```

---

## 📊 Legacy Migration & Data Safety Guarantee

During the system upgrade, all 7 original tasks recovered from the legacy `tasks.json` were safely migrated and seeded into the SQLite relational database with:
- Unique Primary Keys and UUIDs.
- Validated category backfills.
- Status, due date, and AI flag normalization.
- 100% preservation of legacy files in both `data/tasks_legacy.json` and external snapshot backups.

---

## 🗺️ Roadmap & Future Enhancements

The current implementation provides a fully working local SQLite application with FastAPI, Streamlit, and Google Gemini offline resilience. Future development tracks include:
- **Alembic Database Migrations:** Versioned schema migration scripts for enterprise PostgreSQL deployments.
- **Formal Test Coverage Instrumentation:** Adding `pytest-cov` to CI/CD workflows for automated coverage metrics.
- **User Authentication:** Multi-tenant user isolation with JWT bearer authentication.
- **Push Reminders & Notifications:** Native browser push notifications for deadline-sensitive tasks.

---

## 👤 Author

**Ujjwal Pradip Patil**  
[GitHub](https://github.com/UjjwalPatil01) · [LinkedIn](https://www.linkedin.com/in/ujjwalpatil-ai) · [Portfolio](https://ujjwal-ai-portfolio.vercel.app)
