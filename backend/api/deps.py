"""
Dependency functions for role-based access control.
"""
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from core.dependencies import get_current_user


async def check_permissions(
    current_user: User = Depends(get_current_user),
    required_roles: List[str] = []
):
    """
    检查用户权限的依赖项
    
    Args:
        current_user: 当前认证用户
        required_roles: 需要的角色列表
    """
    if not required_roles:
        return current_user
    
    if current_user.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: {', '.join(required_roles)}"
        )
    
    return current_user


async def get_current_student(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前学生用户"""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Students only."
        )
    return current_user


async def get_current_teacher(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前教师用户"""
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Teachers only."
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前管理员用户"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admins only."
        )
    return current_user


async def get_current_teacher_or_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前教师或管理员用户"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Teachers and admins only."
        )
    return current_user