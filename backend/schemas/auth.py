"""
认证相关的 Pydantic Schemas

用于请求验证和响应序列化。
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ============ User Schemas ============

class UserBase(BaseModel):
    """用户基础信息"""
    email: EmailStr
    role: str = Field(default="student", pattern="^(student|teacher|admin)$")


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
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应 (不含密码)"""
    id: int
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
    email: Optional[str] = None
    role: Optional[str] = None
    jti: Optional[str] = None


# ============ Authentication Schemas ============

class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """登录响应"""
    user: UserResponse
    tokens: Token
    message: str = "登录成功"


class RegisterRequest(UserCreate):
    """注册请求 (继承 UserCreate)"""
    student_id: Optional[str] = Field(None, min_length=1, max_length=50)


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

