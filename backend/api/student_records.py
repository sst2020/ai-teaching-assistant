"""
Student Record Management Router - 学生记录 CRUD 接口
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from core.database import get_db
from core.security import hash_password
from schemas.student_record import (
    StudentRecordCreate,
    StudentRecordUpdate,
    StudentRecordResponse,
    StudentRecordListResponse,
)
from schemas.common import APIResponse
from utils.crud import crud_student_record

router = APIRouter(prefix="/student-records", tags=["Student Records"])


@router.post("", response_model=StudentRecordResponse, status_code=201)
async def create_student_record(
    record_in: StudentRecordCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    创建学生记录。

    包含姓名、学号、密码和作业编号。
    密码将以 bcrypt 哈希形式存储。

    Raises:
        HTTPException 400: 学号已存在
    """
    existing = await crud_student_record.get_by_student_id(db, record_in.student_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"学号 '{record_in.student_id}' 已存在",
        )

    record_data = record_in.model_dump()
    record_data["password_hash"] = hash_password(record_data.pop("password"))
    record = await crud_student_record.create(db, record_data)
    return record


@router.get("", response_model=StudentRecordListResponse)
async def list_student_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    assignment_number: Optional[str] = Query(None, description="按作业编号筛选"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取学生记录列表（分页）。

    支持按作业编号筛选。
    """
    skip = (page - 1) * page_size
    filters = {}
    if assignment_number:
        filters["assignment_number"] = assignment_number

    records = await crud_student_record.get_multi(db, skip=skip, limit=page_size, filters=filters)
    total = await crud_student_record.count(db, filters=filters)
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return StudentRecordListResponse(
        items=[StudentRecordResponse.model_validate(r) for r in records],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{student_id}", response_model=StudentRecordResponse)
async def get_student_record(
    student_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    根据学号获取单条记录。

    Raises:
        HTTPException 404: 记录不存在
    """
    record = await crud_student_record.get_by_student_id(db, student_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"学号 '{student_id}' 的记录不存在")
    return record


@router.put("/{student_id}", response_model=StudentRecordResponse)
async def update_student_record(
    student_id: str,
    record_in: StudentRecordUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    更新学生记录。

    仅更新请求中提供的字段。若提供新密码则重新哈希。

    Raises:
        HTTPException 404: 记录不存在
    """
    record = await crud_student_record.get_by_student_id(db, student_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"学号 '{student_id}' 的记录不存在")

    update_data = record_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    elif "password" in update_data:
        del update_data["password"]

    updated = await crud_student_record.update(db, record, update_data)
    return updated


@router.delete("/{student_id}", response_model=APIResponse)
async def delete_student_record(
    student_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    删除学生记录。

    Raises:
        HTTPException 404: 记录不存在
    """
    record = await crud_student_record.get_by_student_id(db, student_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"学号 '{student_id}' 的记录不存在")

    await crud_student_record.delete(db, record.id)
    return APIResponse(
        success=True,
        message=f"学号 '{student_id}' 的记录已删除",
    )
