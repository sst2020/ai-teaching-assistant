"""
认证 API 端点

提供生产级 JWT 认证功能,包括登录、注册、Token 刷新、登出等。
使用数据库存储、bcrypt 密码哈希、Token 黑名单机制。
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status, Request, UploadFile
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
    UpdateProfileRequest,
    UpdateProfileResponse,
    AvatarUploadResponse,
    DeleteAccountRequest,
    DeleteAccountResponse,
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
            "student_id": user.student_id,
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
    - 同时创建 Student 记录（使用相同的 student_id）
    - 返回 JWT tokens
    """
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # 检查学号是否已存在
    existing_user = await crud_user.get_by_student_id(db, data.student_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该学号已被注册"
        )

    # 检查 Student 表中 student_id 是否已存在
    existing_student = await crud_student.get_by_student_id(db, data.student_id)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"学号 '{data.student_id}' 已存在"
        )

    # 哈希密码
    password_hashed = hash_password(data.password)

    # 创建用户
    user = await crud_user.create_with_password(
        db=db,
        student_id=data.student_id,
        password_hash=password_hashed,
        role=data.role
    )

    # 创建 Student 记录（与 User 使用相同的 student_id）
    student_data = {
        "student_id": data.student_id,
        "name": data.name,
        "email": f"{data.student_id}@student.local"  # 使用学号生成占位邮箱
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
        student_id=data.student_id,
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

    - 验证学号和密码
    - 更新最后登录时间
    - 返回 JWT tokens
    """
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # 检查是否被锁定
    lockout_info = await AuthMonitorService.check_failed_login_attempts(
        db=db,
        student_id=credentials.student_id
    )

    if lockout_info['is_locked']:
        # 记录被锁定的登录尝试
        await AuthMonitorService.log_auth_event(
            db=db,
            student_id=credentials.student_id,
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
    user = await crud_user.get_by_student_id(db, credentials.student_id)
    if not user:
        # 记录失败的登录尝试(用户不存在)
        await AuthMonitorService.log_auth_event(
            db=db,
            student_id=credentials.student_id,
            event_type="login_failed",
            status="failure",
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason="用户不存在"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学号或密码错误"
        )

    # 验证密码
    if not verify_password(credentials.password, user.password_hash):
        # 记录失败的登录尝试(密码错误)
        await AuthMonitorService.log_auth_event(
            db=db,
            student_id=credentials.student_id,
            event_type="login_failed",
            status="failure",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason="密码错误"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学号或密码错误"
        )

    # 检查用户是否激活
    if not user.is_active:
        # 记录失败的登录尝试(账户未激活)
        await AuthMonitorService.log_auth_event(
            db=db,
            student_id=credentials.student_id,
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
        student_id=credentials.student_id,
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
        student_id=user.student_id,
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
        student_id=current_user.student_id,
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
        student_id=current_user.student_id,
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
        student_id=current_user.student_id,
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


@router.patch("/profile", response_model=UpdateProfileResponse)
async def update_profile(
    request_data: UpdateProfileRequest,
    http_request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户资料。

    - 可更新姓名
    - 学号不可更改
    """
    ip_address = get_client_ip(http_request)
    user_agent = get_user_agent(http_request)

    # 更新用户信息
    if request_data.name is not None:
        current_user.name = request_data.name

    await db.flush()
    await db.refresh(current_user)
    await db.commit()

    # 记录资料更新事件
    await AuthMonitorService.log_auth_event(
        db=db,
        student_id=current_user.student_id,
        event_type="profile_update",
        status="success",
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return UpdateProfileResponse(
        user=UserResponse.model_validate(current_user),
        message="资料更新成功"
    )


@router.post("/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    file: UploadFile,
    http_request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上传用户头像。

    - 接受 multipart/form-data 格式的图片文件
    - 支持 jpg, jpeg, png, gif, webp 格式
    - 最大文件大小 5MB
    """
    import os
    import uuid
    from pathlib import Path

    # 验证文件类型
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file.content_type}。支持的类型: jpg, png, gif, webp"
        )

    # 读取文件内容
    content = await file.read()

    # 验证文件大小 (5MB)
    max_size = 5 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小超过限制 (最大 5MB)"
        )

    # 生成文件名
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"

    # 确保目录存在
    upload_dir = Path("uploads/avatars")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 删除旧头像文件（如果存在）
    if current_user.avatar_url:
        old_filename = current_user.avatar_url.split("/")[-1]
        old_path = upload_dir / old_filename
        if old_path.exists():
            try:
                old_path.unlink()
            except Exception:
                pass  # 忽略删除失败

    # 保存文件
    file_path = upload_dir / filename
    with open(file_path, "wb") as f:
        f.write(content)

    # 更新用户头像 URL
    avatar_url = f"/uploads/avatars/{filename}"
    current_user.avatar_url = avatar_url
    await db.flush()
    await db.refresh(current_user)
    await db.commit()

    ip_address = get_client_ip(http_request)
    user_agent = get_user_agent(http_request)

    # 记录头像更新事件
    await AuthMonitorService.log_auth_event(
        db=db,
        student_id=current_user.student_id,
        event_type="avatar_update",
        status="success",
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return AvatarUploadResponse(
        avatar_url=avatar_url,
        message="头像上传成功"
    )


@router.delete("/account", response_model=DeleteAccountResponse)
async def delete_account(
    request_data: DeleteAccountRequest,
    http_request: Request,
    current_user: User = Depends(get_current_active_user),
    authorization: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    注销账户。

    - 需要密码确认
    - 删除用户及所有关联数据
    - 此操作不可逆
    """
    ip_address = get_client_ip(http_request)
    user_agent = get_user_agent(http_request)

    # 验证密码
    if not verify_password(request_data.password, current_user.password_hash):
        # 记录失败的删除尝试
        await AuthMonitorService.log_auth_event(
            db=db,
            student_id=current_user.student_id,
            event_type="account_delete",
            status="failure",
            user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason="密码错误"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码错误"
        )

    # 记录删除事件（在删除之前）
    student_id = current_user.student_id
    user_id = current_user.id

    # 将当前 Access Token 加入黑名单
    jti = get_token_jti(authorization)
    if jti:
        expires_at = get_token_expiration(authorization)
        if expires_at:
            await crud_token_blacklist.add_to_blacklist(
                db=db,
                jti=jti,
                user_id=user_id,
                token_type="access",
                expires_at=expires_at
            )

    # 撤销所有 Refresh Tokens
    await crud_refresh_token.revoke_all_user_tokens(db, user_id)

    # 删除用户（级联删除关联数据）
    await crud_user.delete(db, user_id)
    await db.commit()

    # 记录账户删除事件
    await AuthMonitorService.log_auth_event(
        db=db,
        student_id=student_id,
        event_type="account_delete",
        status="success",
        user_id=None,  # 用户已删除
        ip_address=ip_address,
        user_agent=user_agent
    )

    return DeleteAccountResponse(message="账户已注销")
