"""
AI Teaching Assistant Backend API

Main FastAPI application entry point.
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import async_engine, Base
from api.health import router as health_router
from api.auth import router as auth_router
from api.assignments import router as assignments_router
from api.qa import router as qa_router
from api.students import router as students_router
from api.submissions import router as submissions_router
from api.files import router as files_router
from api.analysis import router as analysis_router
from api.ai import router as ai_router
from api.feedback_templates import router as feedback_templates_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📚 API Documentation available at: http://{settings.HOST}:{settings.PORT}/docs")

    # Initialize database tables
    async with async_engine.begin() as conn:
        # Import all models to ensure they are registered with Base
        from models import (
            Student, Assignment, Submission, GradingResult,
            Question, Answer, PlagiarismCheck, Rubric, CodeFile,
            FeedbackTemplate, AIInteraction
        )
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables initialized")

    yield

    # Shutdown
    print(f"👋 Shutting down {settings.APP_NAME}")
    await async_engine.dispose()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health_router)
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
    app.include_router(assignments_router, prefix=settings.API_V1_PREFIX)
    app.include_router(qa_router, prefix=settings.API_V1_PREFIX)
    app.include_router(students_router, prefix=settings.API_V1_PREFIX)
    app.include_router(submissions_router, prefix=settings.API_V1_PREFIX)
    app.include_router(files_router, prefix=settings.API_V1_PREFIX)
    app.include_router(analysis_router, prefix=settings.API_V1_PREFIX)
    app.include_router(ai_router, prefix=settings.API_V1_PREFIX)
    app.include_router(feedback_templates_router, prefix=settings.API_V1_PREFIX)

    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
