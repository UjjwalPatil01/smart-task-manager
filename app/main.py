"""FastAPI main application entrypoint."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import engine, Base, SessionLocal
from app.models.task import Task
from app.services.task_service import TaskService
from app.api.v1.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed legacy data non-destructively
    db = SessionLocal()
    try:
        count = TaskService.seed_from_legacy_json(db, settings.LEGACY_TASKS_FILE)
        if count > 0:
            print(f"[SEED] Successfully seeded {count} legacy tasks into SQLite database.")
    except Exception as e:
        print(f"[WARN] Notice on auto-seed: {e}")
    finally:
        db.close()

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI-powered Smart Task Manager with FastAPI and Streamlit",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["health"])
def health_check():
    """Service health and meta status."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs"
    }
