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

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import time
import os

from core.config import settings
from core.rate_limit import SimpleRateLimitMiddleware
from utils.logger import setup_logger, log_request_start, log_request_end, generate_request_id, set_request_id
from core.database import async_engine, Base
from api.health import router as health_router
from api.auth import router as auth_router
from api.assignments import router as assignments_router
from api.qa import router as qa_router
from api.students import router as students_router
from api.teachers import router as teachers_router
from api.submissions import router as submissions_router
from api.files import router as files_router
from api.analysis import router as analysis_router
from api.report_analysis import router as report_analysis_router
from api.ai import router as ai_router
from api.feedback_templates import router as feedback_templates_router
from api.personalized_feedback import router as personalized_feedback_router
from api.evaluation import router as evaluation_router
from api.knowledge_base import router as knowledge_base_router
from api.triage import router as triage_router
from api.rubrics import router as rubrics_router
from api.grading import router as grading_router

# Setup enhanced logger
logger = setup_logger(
    name="ai_teaching_assistant",
    level=os.getenv("LOG_LEVEL", "INFO"),
    log_file="logs/app.log" if os.getenv("ENABLE_FILE_LOGGING", "false").lower() == "true" else None,
    enable_colors=os.getenv("PRETTY_PRINT_LOGS", "true").lower() == "true",
    pretty_print=os.getenv("PRETTY_PRINT_LOGS", "true").lower() == "true"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📚 API Documentation available at: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")
    logger.info(f"📊 Request logging: {os.getenv('ENABLE_REQUEST_LOGGING', 'false')}")
    logger.info(f"⚡ Performance monitoring: {os.getenv('ENABLE_PERFORMANCE_MONITORING', 'false')}")

    # Initialize database tables
    async with async_engine.begin() as conn:
        # Import all models to ensure they are registered with Base
        from models import (
            Student, Teacher, Assignment, Submission, GradingResult,
            Question, Answer, PlagiarismCheck, Rubric, CodeFile,
            FeedbackTemplate, AIInteraction, KnowledgeBaseEntry, QALog
        )
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables initialized")

    yield

    # Shutdown
    logger.info(f"👋 Shutting down {settings.APP_NAME}")
    await async_engine.dispose()


async def log_requests_middleware(request: Request, call_next):
    """Enhanced request logging middleware with performance tracking"""

    # Generate request ID
    request_id = generate_request_id()
    set_request_id(request_id)

    # Add request ID to response headers
    start_time = time.time()

    # Log request start (if enabled)
    if os.getenv("ENABLE_REQUEST_LOGGING", "false").lower() == "true":
        log_request_start(request.method, str(request.url), request_id)

        # Log request details in debug mode
        if logger.level <= 10:  # DEBUG level
            logger.debug(f"📋 Headers: {dict(request.headers)}")
            if request.method in ["POST", "PUT", "PATCH"]:
                # Note: We can't easily log request body here without consuming the stream
                logger.debug(f"📦 Content-Type: {request.headers.get('content-type', 'N/A')}")

    # Process request
    try:
        response = await call_next(request)

        # Calculate response time
        process_time = time.time() - start_time

        # Add performance headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{process_time:.3f}s"

        # Log request completion
        if os.getenv("ENABLE_REQUEST_LOGGING", "false").lower() == "true":
            log_request_end(request.method, str(request.url), response.status_code, process_time)

        # Performance monitoring
        if os.getenv("ENABLE_PERFORMANCE_MONITORING", "false").lower() == "true":
            if process_time > 2.0:
                logger.warning(f"🐌 Slow request: {request.method} {request.url} took {process_time:.3f}s")
            elif process_time > 1.0:
                logger.info(f"⏰ Request: {request.method} {request.url} took {process_time:.3f}s")

        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"💥 Request failed: {request.method} {request.url} after {process_time:.3f}s - {str(e)}")
        raise


def create_app(testing: bool = False) -> FastAPI:
    """
    FastAPI 应用工厂函数

    Args:
        testing: 是否为测试模式。测试模式下会跳过某些初始化步骤。

    Returns:
        FastAPI 应用实例
    """

    # 在测试模式下，使用简化的 lifespan
    if testing:
        @asynccontextmanager
        async def test_lifespan(app: FastAPI):
            """测试模式的简化 lifespan"""
            if os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL", "")).startswith("sqlite"):
                # SQLite in-memory needs schema creation per test app lifecycle.
                async with async_engine.begin() as conn:
                    # 导入所有模型以确保它们被注册到 Base.metadata
                    from models import (
                        Student, Teacher, Assignment, Submission, GradingResult,
                        Question, Answer, PlagiarismCheck, Rubric, CodeFile,
                        AnalysisResult, FeedbackTemplate, AIInteraction,
                        KnowledgeBaseEntry, QALog
                    )
                    await conn.run_sync(Base.metadata.create_all)
            yield
            await async_engine.dispose()

        app_lifespan = test_lifespan
    else:
        app_lifespan = lifespan

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=app_lifespan
    )

    # Add request logging middleware
    app.middleware("http")(log_requests_middleware)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting middleware (toggle via settings.RATE_LIMIT_ENABLED)
    app.add_middleware(SimpleRateLimitMiddleware)

    # Include routers
    app.include_router(health_router)
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
    app.include_router(assignments_router, prefix=settings.API_V1_PREFIX)
    app.include_router(qa_router, prefix=settings.API_V1_PREFIX)
    app.include_router(students_router, prefix=settings.API_V1_PREFIX)
    app.include_router(teachers_router, prefix=settings.API_V1_PREFIX)
    app.include_router(submissions_router, prefix=settings.API_V1_PREFIX)
    app.include_router(files_router, prefix=settings.API_V1_PREFIX)
    app.include_router(analysis_router, prefix=settings.API_V1_PREFIX)
    app.include_router(report_analysis_router, prefix=settings.API_V1_PREFIX)
    app.include_router(ai_router, prefix=settings.API_V1_PREFIX)
    app.include_router(feedback_templates_router, prefix=settings.API_V1_PREFIX)
    app.include_router(personalized_feedback_router, prefix=settings.API_V1_PREFIX)
    app.include_router(evaluation_router, prefix=settings.API_V1_PREFIX)
    app.include_router(knowledge_base_router, prefix=settings.API_V1_PREFIX)
    app.include_router(triage_router, prefix=settings.API_V1_PREFIX)
    app.include_router(rubrics_router, prefix=settings.API_V1_PREFIX)
    app.include_router(grading_router, prefix=settings.API_V1_PREFIX)

    return app


# Create the application instance (向后兼容)
app = create_app()


# 保留旧函数名以向后兼容
def create_application() -> FastAPI:
    """
    已弃用：请使用 create_app() 代替

    为了向后兼容保留此函数
    """
    return create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
