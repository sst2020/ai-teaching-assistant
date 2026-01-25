"""
Health Check Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from typing import Optional

from schemas.common import HealthResponse
from core.config import settings
from core.database import get_db

router = APIRouter(tags=["Health"])


async def check_database_health(db: AsyncSession) -> tuple[bool, Optional[str]]:
    """Check if database connection is healthy."""
    try:
        await db.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        return False, str(e)


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    健康检查端点，验证 API 和数据库是否正常运行。

    Args:
        db: 异步数据库会话（自动注入）

    Returns:
        HealthResponse: 包含以下字段的健康状态响应：
            - status: 服务状态（"healthy" 或 "degraded"）
            - version: API 版本号
            - timestamp: 检查时间戳
            - database_status: 数据库连接状态
    """
    db_healthy, db_error = await check_database_health(db)

    # Determine overall status
    if db_healthy:
        status = "healthy"
    else:
        status = "degraded"

    return HealthResponse(
        status=status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        database_status="connected" if db_healthy else f"error: {db_error}"
    )


@router.get("/")
async def root():
    """
    根端点，返回 API 基本信息。

    Returns:
        dict: 包含以下字段的 API 信息：
            - name: 应用名称
            - version: 版本号
            - description: 应用描述
            - docs_url: Swagger 文档地址
            - health_check: 健康检查端点地址
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs_url": "/docs",
        "health_check": "/health"
    }

