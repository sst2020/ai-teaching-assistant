"""
Authentication API endpoints.

Provides login, registration, token refresh, and user management endpoints.
Note: This is a simplified implementation for development/testing purposes.
In production, use proper password hashing and JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory user store for development (replace with database in production)
_users_db: dict = {}
_tokens_db: dict = {}

# Token expiration settings
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============ Schemas ============

class LoginCredentials(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)


class RegisterData(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)
    role: str = Field(default="student")


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class User(BaseModel):
    id: str
    email: str
    name: str
    role: str
    created_at: datetime


class LoginResponse(BaseModel):
    user: User
    tokens: AuthTokens


class RegisterResponse(BaseModel):
    user: User
    tokens: AuthTokens
    message: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ============ Helper Functions ============

def hash_password(password: str) -> str:
    """Simple password hashing (use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    """Generate a random token."""
    return secrets.token_urlsafe(32)


def create_tokens(user_id: str) -> AuthTokens:
    """Create access and refresh tokens for a user."""
    access_token = generate_token()
    refresh_token = generate_token()

    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    _tokens_db[access_token] = {
        "user_id": user_id,
        "type": "access",
        "expires_at": expires_at
    }
    _tokens_db[refresh_token] = {
        "user_id": user_id,
        "type": "refresh",
        "expires_at": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }

    return AuthTokens(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def get_current_user_from_token(token: str) -> Optional[User]:
    """Validate token and return user."""
    token_data = _tokens_db.get(token)
    if not token_data:
        return None
    if token_data["expires_at"] < datetime.utcnow():
        del _tokens_db[token]
        return None

    user_data = _users_db.get(token_data["user_id"])
    if not user_data:
        return None

    return User(
        id=token_data["user_id"],
        email=user_data["email"],
        name=user_data["name"],
        role=user_data["role"],
        created_at=user_data["created_at"]
    )


# ============ Endpoints ============

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginCredentials):
    """Authenticate user and return tokens."""
    user_id = None
    user_data = None
    for uid, data in _users_db.items():
        if data["email"] == credentials.email:
            user_id = uid
            user_data = data
            break

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if user_data["password_hash"] != hash_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    tokens = create_tokens(user_id)
    user = User(
        id=user_id,
        email=user_data["email"],
        name=user_data["name"],
        role=user_data["role"],
        created_at=user_data["created_at"]
    )

    return LoginResponse(user=user, tokens=tokens)


@router.post("/register", response_model=RegisterResponse)
async def register(data: RegisterData):
    """Register a new user."""
    for user_data in _users_db.values():
        if user_data["email"] == data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    user_id = generate_token()[:16]
    now = datetime.utcnow()

    _users_db[user_id] = {
        "email": data.email,
        "password_hash": hash_password(data.password),
        "name": data.name,
        "role": data.role,
        "created_at": now
    }

    tokens = create_tokens(user_id)
    user = User(id=user_id, email=data.email, name=data.name, role=data.role, created_at=now)

    return RegisterResponse(user=user, tokens=tokens, message="Registration successful")


@router.post("/refresh", response_model=AuthTokens)
async def refresh_token(request: RefreshRequest):
    """Refresh access token using refresh token."""
    token_data = _tokens_db.get(request.refresh_token)

    if not token_data or token_data["type"] != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if token_data["expires_at"] < datetime.utcnow():
        del _tokens_db[request.refresh_token]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    del _tokens_db[request.refresh_token]
    return create_tokens(token_data["user_id"])


@router.post("/logout")
async def logout():
    """Logout user (client should clear tokens)."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=User)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user = get_current_user_from_token(token)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return user


# ============ Development Helper ============

def _create_test_user():
    """Create a test user for development purposes."""
    test_user_id = "test-user-001"
    if test_user_id not in _users_db:
        _users_db[test_user_id] = {
            "email": "test@example.com",
            "password_hash": hash_password("password123"),
            "name": "Test User",
            "role": "student",
            "created_at": datetime.utcnow()
        }

_create_test_user()
