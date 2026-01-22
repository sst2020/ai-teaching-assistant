"""
认证相关的 Pydantic Schemas

用于请求验证和响应序列化。
"""
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


def validate_student_id_format(v: str) -> str:
    """验证学号格式：必须为10位数字"""
    if not re.match(r'^\d{10}$', v):
        raise ValueError('学号必须为10位数字')
    return v


# ============ User Schemas ============

class UserBase(BaseModel):
    """用户基础信息"""
    student_id: str = Field(..., min_length=10, max_length=10, description="学号（10位数字）")
    role: str = Field(default="student", pattern="^(student|teacher|admin)$")

    @field_validator('student_id')
    @classmethod
    def validate_student_id(cls, v: str) -> str:
        """验证学号格式"""
        return validate_student_id_format(v)


class UserCreate(UserBase):
    """用户注册请求"""
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=2, max_length=255)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度"""
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含至少一个字母')
        return v


class UserUpdate(BaseModel):
    """用户更新请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应 (不含密码)"""
    id: int
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """数据库中的用户 (含密码哈希)"""
    password_hash: str


# ============ Token Schemas ============

class Token(BaseModel):
    """JWT Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒


class TokenData(BaseModel):
    """Token 解析后的数据"""
    user_id: Optional[int] = None
    student_id: Optional[str] = None
    role: Optional[str] = None
    jti: Optional[str] = None


# ============ Authentication Schemas ============

class LoginRequest(BaseModel):
    """登录请求"""
    student_id: str = Field(..., min_length=10, max_length=10, description="学号（10位数字）")
    password: str = Field(..., min_length=1)

    @field_validator('student_id')
    @classmethod
    def validate_student_id(cls, v: str) -> str:
        """验证学号格式"""
        return validate_student_id_format(v)


class LoginResponse(BaseModel):
    """登录响应"""
    user: UserResponse
    tokens: Token
    message: str = "登录成功"


class RegisterRequest(UserCreate):
    """注册请求 (继承 UserCreate，student_id 已在 UserBase 中定义为必填)"""
    pass


class RegisterResponse(BaseModel):
    """注册响应"""
    user: UserResponse
    tokens: Token
    message: str = "注册成功"


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str = Field(..., min_length=1)


class RefreshTokenResponse(BaseModel):
    """刷新 Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """验证新密码强度"""
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含至少一个字母')
        return v


class ChangePasswordResponse(BaseModel):
    """修改密码响应"""
    message: str = "密码修改成功,所有设备已登出"


class LogoutResponse(BaseModel):
    """登出响应"""
    message: str = "登出成功"


class RevokeAllTokensResponse(BaseModel):
    """撤销所有 Token 响应"""
    message: str = "所有设备已登出"
    revoked_count: int


# ============ Profile Schemas ============

class UpdateProfileRequest(BaseModel):
    """更新用户资料请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="用户姓名")


class UpdateProfileResponse(BaseModel):
    """更新用户资料响应"""
    user: UserResponse
    message: str = "资料更新成功"


class AvatarUploadResponse(BaseModel):
    """头像上传响应"""
    avatar_url: str
    message: str = "头像上传成功"


class DeleteAccountRequest(BaseModel):
    """删除账户请求"""
    password: str = Field(..., min_length=1, description="当前密码确认")


class DeleteAccountResponse(BaseModel):
    """删除账户响应"""
    message: str = "账户已注销"

