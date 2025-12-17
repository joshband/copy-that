"""Authentication router"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from copy_that.application.errors import (
    AlreadyExistsError,
    AuthenticationFailedError,
    DisabledAccountError,
    InvalidRefreshTokenError,
)
from copy_that.application.ports.security import PasswordHasher, TokenCodec
from copy_that.application.ports.users import UserRepository
from copy_that.application.use_cases import auth as auth_use_cases
from copy_that.domain.users import User
from copy_that.interfaces.api import dependencies as deps

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# Request/Response models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(deps.get_user_repo),
    token_codec: TokenCodec = Depends(deps.get_token_codec),
) -> User:
    token_data = token_codec.decode(token)
    user = await user_repo.get_by_id(user_id=token_data.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled"
        )
    return user


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    user_repo: UserRepository = Depends(deps.get_user_repo),
    password_hasher: PasswordHasher = Depends(deps.get_password_hasher),
) -> UserResponse:
    """Register a new user"""
    try:
        user = await auth_use_cases.register_user(
            user_repo,
            password_hasher,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )
    except AlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        ) from exc

    logger.info(f"New user registered: {user.email}")

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
    )


@router.post("/token", response_model=TokenPairResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: UserRepository = Depends(deps.get_user_repo),
    password_hasher: PasswordHasher = Depends(deps.get_password_hasher),
    token_codec: TokenCodec = Depends(deps.get_token_codec),
) -> TokenPairResponse:
    """Authenticate and get tokens"""
    try:
        token_pair = await auth_use_cases.login_and_issue_tokens(
            user_repo,
            password_hasher,
            token_codec,
            email=form_data.username,
            password=form_data.password,
            now=datetime.now(UTC),
        )
    except AuthenticationFailedError as exc:
        logger.warning(f"Failed login attempt for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except DisabledAccountError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
        ) from exc

    logger.info(f"User logged in: {form_data.username}")

    return TokenPairResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
    )


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh_token(
    request: RefreshRequest,
    user_repo: UserRepository = Depends(deps.get_user_repo),
    token_codec: TokenCodec = Depends(deps.get_token_codec),
) -> TokenPairResponse:
    """Get new tokens using refresh token"""
    try:
        token_pair = await auth_use_cases.refresh_tokens(
            user_repo, token_codec, refresh_token=request.refresh_token
        )
    except InvalidRefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        ) from exc

    return TokenPairResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
    )
