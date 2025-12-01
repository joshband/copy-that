"""JWT Authentication and password hashing"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # type: ignore[import-untyped]
from passlib.context import CryptContext  # type: ignore[import-untyped]
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db

# Configuration
_secret_key_env = os.getenv("SECRET_KEY")
_environment = os.getenv("ENVIRONMENT", "local")

if not _secret_key_env:
    if _environment == "production":
        raise ValueError(
            "SECRET_KEY environment variable must be set in production. "
            "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )
    # Only use default in non-production environments
    SECRET_KEY = "dev-secret-key-change-in-production"
else:
    SECRET_KEY = _secret_key_env

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


class TokenData(BaseModel):
    """Decoded token data"""

    user_id: str
    email: str
    roles: list[str] = []
    exp: datetime


class TokenPair(BaseModel):
    """Access and refresh token pair"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    result: bool = pwd_context.verify(plain_password, hashed_password)
    return result


def get_password_hash(password: str) -> str:
    """Hash a password for storage"""
    result: str = pwd_context.hash(password)
    return result


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    encoded: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def create_token_pair(user_id: str, email: str, roles: list[str]) -> TokenPair:
    """Create access and refresh token pair"""
    token_data = {"sub": user_id, "email": email, "roles": roles}
    return TokenPair(
        access_token=create_access_token(token_data), refresh_token=create_refresh_token(token_data)
    )


def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        roles = payload.get("roles", [])
        exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing user ID"
            )

        return TokenData(user_id=user_id, email=email, roles=roles, exp=exp)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> Any:
    """FastAPI dependency to get authenticated user"""
    from copy_that.domain.models import User

    token_data = decode_token(token)

    # Get user from database
    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled"
        )

    return user


def require_roles(*required_roles: str) -> Any:
    """Dependency factory for role-based access"""

    async def role_checker(
        token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ) -> Any:
        from copy_that.domain.models import User

        token_data = decode_token(token)

        result = await db.execute(select(User).where(User.id == token_data.user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        user_roles = set(user.roles or [])
        if not user_roles.intersection(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(required_roles)}",
            )
        return user

    return role_checker
