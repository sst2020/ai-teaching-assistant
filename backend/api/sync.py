"""
数据同步 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import json
import os

from core.database import get_db
from services.assignment_sync_service import assignment_sync_service, SyncResult

router = APIRouter(prefix="/sync", tags=["Data Synchronization"])


@router.post("/assignments", response_model=SyncResult)
async def sync_assignments_from_management_system(
    db: AsyncSession = Depends(get_db)
):
    """
    从管理系统同步作业数据
    
    - 读取管理系统的任务数据
    - 映射为学生端作业格式
    - 去重后保存到数据库
    - 返回同步结果
    
    需要管理员权限（TODO: 添加权限检查）
    """
    try:
        result = await assignment_sync_service.sync_assignments(db)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/logs")
async def get_sync_logs(limit: int = 20):
    """
    获取同步日志
    
    返回最近的同步记录
    
    Args:
        limit: 返回的日志条数，默认 20 条
    """
    log_path = "data/sync_log.json"
    if not os.path.exists(log_path):
        return []
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # 返回最近的 N 条日志
        return logs[-limit:] if len(logs) > limit else logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")

