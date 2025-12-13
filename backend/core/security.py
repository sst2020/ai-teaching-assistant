"""
安全工具模块

提供密码哈希、JWT Token 生成和验证等安全相关功能。
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

from jose import JWTError, jwt
import bcrypt
from fastapi.security import OAuth2PasswordBearer

from core.config import settings


# OAuth2 密码流配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ============ 密码哈希函数 ============

def hash_password(password: str) -> str:
    """
    使用 bcrypt 哈希密码。

    Args:
        password: 明文密码

    Returns:
        哈希后的密码

    Note:
        Bcrypt 限制密码最大 72 字节,超过部分会被截断
    """
    # Bcrypt 限制密码最大 72 字节
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配。

    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码

    Returns:
        密码是否匹配

    Note:
        Bcrypt 限制密码最大 72 字节,超过部分会被截断
    """
    # Bcrypt 限制密码最大 72 字节
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ============ JWT Token 函数 ============

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT Access Token。
    
    Args:
        data: 要编码到 token 中的数据 (通常包含 sub, email, role)
        expires_delta: 过期时间增量,默认使用配置中的值
        
    Returns:
        编码后的 JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # 添加标准 JWT claims
    to_encode.update({
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at
        "jti": secrets.token_urlsafe(16)  # JWT ID (用于黑名单)
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """
    创建 Refresh Token (随机字符串,不是 JWT)。
    
    Args:
        user_id: 用户 ID
        
    Returns:
        随机生成的 refresh token
    """
    return secrets.token_urlsafe(32)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码并验证 JWT Access Token。
    
    Args:
        token: JWT token 字符串
        
    Returns:
        解码后的 payload,如果验证失败返回 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def get_token_jti(token: str) -> Optional[str]:
    """
    从 JWT token 中提取 JTI (JWT ID)。
    
    Args:
        token: JWT token 字符串
        
    Returns:
        JTI 字符串,如果提取失败返回 None
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("jti")
    return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    从 JWT token 中提取过期时间。
    
    Args:
        token: JWT token 字符串
        
    Returns:
        过期时间,如果提取失败返回 None
    """
    payload = decode_access_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None

