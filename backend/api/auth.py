"""
认证 API 端点

提供生产级 JWT 认证功能,包括登录、注册、Token 刷新、登出等。
使用数据库存储、bcrypt 密码哈希、Token 黑名单机制。
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.config import settings
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_token_jti,
    get_token_expiration,
    oauth2_scheme,
)
from core.dependencies import get_current_active_user
from models import User, Student
from utils.crud import (
    crud_user,
    crud_student,
    crud_refresh_token,
    crud_token_blacklist,
)
from schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    LogoutResponse,
    RevokeAllTokensResponse,
    Token,
    UserResponse,
)
from services.auth_monitor import AuthMonitorService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_client_ip(request: Request) -> Optional[str]:
    """获取客户端 IP 地址"""
    # 优先从 X-Forwarded-For 获取(如果使用了代理)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    # 否则从 X-Real-IP 获取
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    # 最后使用直接连接的 IP
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> Optional[str]:
    """获取用户代理字符串"""
    return request.headers.get("User-Agent")



# ============ Helper Functions ============

async def _create_tokens_for_user(db: AsyncSession, user: User) -> Token:
    """
    为用户创建 Access Token 和 Refresh Token。

    Args:
        db: 数据库会话
        user: 用户对象

    Returns:
        Token 对象 (包含 access_token 和 refresh_token)
    """
    # 创建 Access Token (JWT)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        },
        expires_delta=access_token_expires
    )

    # 创建 Refresh Token (随机字符串)
    refresh_token_str = create_refresh_token(user.id)
    refresh_token_expires = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    # 存储 Refresh Token 到数据库
    await crud_refresh_token.create_token(
        db=db,
        user_id=user.id,
        token=refresh_token_str,
        expires_at=refresh_token_expires
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


# ============ Endpoints ============

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    注册新用户。

    - 创建 User 记录
    - 如果提供了 student_id,同时创建 Student 记录
    - 返回 JWT tokens
    """
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # 检查邮箱是否已存在
    existing_user = await crud_user.get_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    # 哈希密码
    password_hashed = hash_password(data.password)

    # 创建用户
    user = await crud_user.create_with_password(
        db=db,
        email=data.email,
        password_hash=password_hashed,
        role=data.role
    )

    # 如果提供了 student_id,创建 Student 记录
    if data.student_id:
        # 检查 student_id 是否已存在
        existing_student = await crud_student.get_by_student_id(db, data.student_id)
        if existing_student:
            # 回滚用户创建
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"学号 '{data.student_id}' 已存在"
            )

        # 创建 Student 记录
        student_data = {
            "student_id": data.student_id,
            "name": data.name,
            "email": data.email
        }
        student = await crud_student.create(db, student_data)

        # 关联 User 和 Student
        student.user_id = user.id

    # 提交事务
    await db.commit()
    await db.refresh(user)

    # 创建 tokens
    tokens = await _create_tokens_for_user(db, user)
    await db.commit()

    # 记录注册事件
    await AuthMonitorService.log_auth_event(
        db=db,
        email=data.email,
        event_type="register",
        status="success",
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return RegisterResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens,
        message="注册成功"
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录。

    - 验证邮箱和密码
    - 更新最后登录时间
    - 返回 JWT tokens
    """
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # 检查是否被锁定
    lockout_info = await AuthMonitorService.check_failed_login_attempts(
        db=db,
        email=credentials.email
    )

    if lockout_info['is_locked']:
        # 记录被锁定的登录尝试
        await AuthMonitorService.log_auth_event(
            db=db,
            email=credentials.email,
            event_type="login_failed",
            status="failure",
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=f"账户已被锁定,剩余 {lockout_info['remaining_lockout_minutes']} 分钟"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录失败次数过多,账户已被锁定 {lockout_info['remaining_lockout_minutes']} 分钟"
        )

    # 查找用户
    user = await crud_user.get_by_email(db, credentials.email)
    if not user:
        # 记录失败的登录尝试(用户不存在)
        await AuthMonitorService.log_auth_event(
            db=db,
            email=credentials.email,
            event_type="login_failed",
            status="failure",
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason="用户不存在"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # 验证密码
    if not verify_password(credentials.password, user.password_hash):
        # 记录失败的登录尝试(密码错误)
        await AuthMonitorService.log_auth_event(
            db=db,
            email=credentials.email,
            event_type="login_failed",
            status="failure",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason="密码错误"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # 检查用户是否激活
    if not user.is_active:
        # 记录失败的登录尝试(账户未激活)
        await AuthMonitorService.log_auth_event(
            db=db,
            email=credentials.email,
            event_type="login_failed",
            status="failure",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason="账户已被停用"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被停用"
        )

    # 更新最后登录时间
    await crud_user.update_last_login(db, user.id)

    # 创建 tokens
    tokens = await _create_tokens_for_user(db, user)
    await db.commit()

    # 刷新 user 对象以加载所有属性
    await db.refresh(user)

    # 记录成功的登录事件
    await AuthMonitorService.log_auth_event(
        db=db,
        email=credentials.email,
        event_type="login",
        status="success",
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return LoginResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens,
        message="登录成功"
    )



@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_access_token(
    request_data: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新 Access Token。

    - 验证 Refresh Token
    - 撤销旧的 Refresh Token (Rotation)
    - 生成新的 Access Token 和 Refresh Token
    """
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # 查找 Refresh Token
    refresh_token = await crud_refresh_token.get_by_token(db, request_data.refresh_token)

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Refresh Token"
        )

    # 检查是否已撤销
    if refresh_token.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token 已被撤销"
        )

    # 检查是否过期
    if refresh_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token 已过期"
        )

    # 获取用户
    user = await crud_user.get(db, refresh_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被停用"
        )

    # 撤销旧的 Refresh Token (Rotation 机制)
    await crud_refresh_token.revoke_token(db, request_data.refresh_token)

    # 创建新的 tokens
    new_tokens = await _create_tokens_for_user(db, user)
    await db.commit()

    # 记录 token 刷新事件
    await AuthMonitorService.log_auth_event(
        db=db,
        email=user.email,
        event_type="token_refresh",
        status="success",
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return RefreshTokenResponse(
        access_token=new_tokens.access_token,
        refresh_token=new_tokens.refresh_token,
        token_type="bearer",
        expires_in=new_tokens.expires_in
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    authorization: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登出。

    - 将当前 Access Token 加入黑名单
    - 撤销所有 Refresh Tokens
    """
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # 提取 Access Token 的 JTI
    jti = get_token_jti(authorization)
    if jti:
        # 获取 Token 过期时间
        expires_at = get_token_expiration(authorization)
        if expires_at:
            # 加入黑名单
            await crud_token_blacklist.add_to_blacklist(
                db=db,
                jti=jti,
                user_id=current_user.id,
                token_type="access",
                expires_at=expires_at
            )

    # 撤销所有 Refresh Tokens
    await crud_refresh_token.revoke_all_user_tokens(db, current_user.id)
    await db.commit()

    # 记录登出事件
    await AuthMonitorService.log_auth_event(
        db=db,
        email=current_user.email,
        event_type="logout",
        status="success",
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return LogoutResponse(message="登出成功")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户信息。

    需要有效的 Access Token。
    """
    return UserResponse.model_validate(current_user)


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request_data: ChangePasswordRequest,
    http_request: Request,
    current_user: User = Depends(get_current_active_user),
    authorization: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码。

    - 验证旧密码
    - 更新为新密码
    - 撤销所有现有 tokens (强制重新登录)
    """
    ip_address = get_client_ip(http_request)
    user_agent = get_user_agent(http_request)

    # 验证旧密码
    if not verify_password(request_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 更新密码
    new_password_hash = hash_password(request_data.new_password)
    current_user.password_hash = new_password_hash

    # 将当前 Access Token 加入黑名单
    jti = get_token_jti(authorization)
    if jti:
        expires_at = get_token_expiration(authorization)
        if expires_at:
            await crud_token_blacklist.add_to_blacklist(
                db=db,
                jti=jti,
                user_id=current_user.id,
                token_type="access",
                expires_at=expires_at
            )

    # 撤销所有 Refresh Tokens
    await crud_refresh_token.revoke_all_user_tokens(db, current_user.id)
    await db.commit()

    # 记录密码修改事件
    await AuthMonitorService.log_auth_event(
        db=db,
        email=current_user.email,
        event_type="password_change",
        status="success",
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return ChangePasswordResponse(message="密码修改成功,所有设备已登出")


@router.post("/revoke-all", response_model=RevokeAllTokensResponse)
async def revoke_all_tokens(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    撤销所有 Refresh Tokens。

    用于安全事件响应,强制所有设备重新登录。
    """
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    revoked_count = await crud_refresh_token.revoke_all_user_tokens(db, current_user.id)
    await db.commit()

    # 记录撤销所有 tokens 事件
    await AuthMonitorService.log_auth_event(
        db=db,
        email=current_user.email,
        event_type="token_revoke",
        status="success",
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata={"revoked_count": revoked_count}
    )

    return RevokeAllTokensResponse(
        message="所有设备已登出",
        revoked_count=revoked_count
    )

