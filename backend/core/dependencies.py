"""
依赖注入函数

提供 FastAPI 路由中使用的依赖注入函数,用于认证和授权。
"""
from typing import Optional, Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import oauth2_scheme, decode_access_token
from models import User
from utils.crud import crud_user, crud_token_blacklist
from schemas.auth import TokenData


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    从 JWT Token 获取当前用户。
    
    验证步骤:
    1. 解码 JWT Token
    2. 检查 Token 是否在黑名单
    3. 从数据库获取用户
    4. 验证用户是否存在
    
    Args:
        token: JWT access token
        db: 数据库会话
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 401 如果认证失败
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 解码 Token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # 提取用户信息
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # 检查 Token 是否在黑名单
    jti: Optional[str] = payload.get("jti")
    if jti:
        is_blacklisted = await crud_token_blacklist.is_blacklisted(db, jti)
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 已失效,请重新登录",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # 从数据库获取用户
    user = await crud_user.get(db, int(user_id))
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户。
    
    Args:
        current_user: 当前用户
        
    Returns:
        活跃的用户对象
        
    Raises:
        HTTPException: 403 如果用户未激活
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被停用"
        )
    return current_user


def require_role(required_role: str) -> Callable:
    """
    角色权限检查装饰器工厂。
    
    用法:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role("admin"))):
            ...
    
    Args:
        required_role: 需要的角色 (student, teacher, admin)
        
    Returns:
        依赖注入函数
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要 {required_role} 角色权限"
            )
        return current_user
    
    return role_checker


def require_roles(allowed_roles: list[str]) -> Callable:
    """
    多角色权限检查装饰器工厂。
    
    用法:
        @router.get("/teacher-or-admin")
        async def endpoint(user: User = Depends(require_roles(["teacher", "admin"]))):
            ...
    
    Args:
        allowed_roles: 允许的角色列表
        
    Returns:
        依赖注入函数
    """
    async def roles_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色之一: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return roles_checker


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    获取可选的当前用户 (允许匿名访问)。
    
    如果提供了有效的 Token,返回用户对象;否则返回 None。
    
    Args:
        token: 可选的 JWT access token
        db: 数据库会话
        
    Returns:
        用户对象或 None
    """
    if not token:
        return None
    
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None

