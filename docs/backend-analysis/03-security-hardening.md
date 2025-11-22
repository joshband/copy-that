# Security Hardening Analysis

**Focus Area: 25% of Evaluation Effort**

---

## Table of Contents

1. [Security Audit Findings](#1-security-audit-findings)
2. [Authentication & Authorization Design](#2-authentication--authorization-design)
3. [Defense-in-Depth Strategy](#3-defense-in-depth-strategy)
4. [Dependency Security](#4-dependency-security)
5. [Implementation Examples](#5-implementation-examples)

---

## 1. Security Audit Findings

### 1.1 Critical Vulnerabilities

#### CRITICAL-1: No Authentication on Any API Endpoint

**Location**: All API routers
**Risk**: Anyone can access, modify, or delete any data
**CVSS Score**: 9.8 (Critical)

**Current State**:
```python
# colors.py - No authentication
@router.post("/extract")
async def extract_colors(
    request: ExtractColorsRequest,
    db: AsyncSession = Depends(get_db)  # No user verification
):
    # Anyone can call this endpoint
    ...
```

**Impact**:
- Unauthorized data access
- Data manipulation/deletion
- API abuse and cost exploitation
- Complete system compromise

---

#### CRITICAL-2: Hardcoded Credentials in Source Code

**Location**: `config.py:110-113`, `deployment_config.py:110-113`

```python
# config.py - EXPOSED CREDENTIALS
"staging": {
    "REDIS_URL": "redis://default:AZnUAAIncDI2ZDM0Y2Y1ZTBjYWI0NDBlOGFlNjYwMWE1OTAzZWY1Y3AyMzkzODA@literate-javelin-39380.upstash.io:6379",
}
```

**Risk**: Credential exposure in version control
**Impact**: Complete Redis access for anyone with repo access

---

#### CRITICAL-3: No Rate Limiting

**Location**: Not implemented
**Risk**: API abuse, DoS attacks, cost explosion

**Impact**:
- AI API cost overrun ($1000s in minutes)
- Database connection exhaustion
- Service unavailability

---

### 1.2 High-Priority Issues

#### HIGH-1: Information Disclosure via Error Messages

**Location**: `colors.py:149-154`

```python
# Current: Exposes internal errors
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Color extraction failed: {str(e)}"  # Leaks internals
    )
```

**Risk**: Attackers learn system internals

---

#### HIGH-2: Unsafe CORS Configuration

**Location**: `main.py:54-55`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # TOO PERMISSIVE
    allow_headers=["*"],  # TOO PERMISSIVE
)
```

**Risk**: Cross-site request exploitation

---

#### HIGH-3: DoS via Unbounded Base64 Uploads

**Location**: `colors.py:96`

```python
# No size validation
if request.image_base64:
    # Could be 100MB+ encoded image
    image_data = base64.b64decode(request.image_base64)
```

**Risk**: Memory exhaustion, service crash

---

#### HIGH-4: SSRF via Image URL

**Location**: `color_extractor.py`

```python
# No URL validation
response = requests.get(image_url)
image_data = response.content
```

**Risk**: Internal network scanning, cloud metadata access

---

### 1.3 Medium-Priority Issues

| Issue | Location | Risk |
|-------|----------|------|
| No resource ownership validation | All routers | Cross-user data access |
| Status endpoint exposes environment | `main.py:111-125` | Information disclosure |
| Silent exception handling | `database.py` | Debugging blind spots |
| No audit logging | N/A | No accountability trail |
| Missing security headers | N/A | XSS, clickjacking |

### 1.4 OWASP Top 10 Compliance

| OWASP Category | Status | Details |
|----------------|--------|---------|
| A01: Broken Access Control | **FAIL** | No auth, no ownership checks |
| A02: Cryptographic Failures | PARTIAL | Uses JWT libs but not implemented |
| A03: Injection | PASS | SQLAlchemy ORM protection |
| A04: Insecure Design | **FAIL** | Missing security architecture |
| A05: Security Misconfiguration | **FAIL** | Hardcoded secrets, CORS |
| A06: Vulnerable Components | CHECK | Need dependency audit |
| A07: Auth Failures | **FAIL** | No authentication |
| A08: Data Integrity Failures | PARTIAL | No input sanitization |
| A09: Logging Failures | **FAIL** | No security logging |
| A10: SSRF | **FAIL** | Unvalidated URLs |

---

## 2. Authentication & Authorization Design

### 2.1 JWT Authentication Implementation

#### Create Auth Infrastructure

```python
# src/copy_that/infrastructure/security/authentication.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


class TokenData(BaseModel):
    user_id: str
    email: str
    roles: list[str] = []
    exp: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storage"""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_token_pair(user_id: str, email: str, roles: list[str]) -> TokenPair:
    """Create access and refresh token pair"""
    token_data = {
        "sub": user_id,
        "email": email,
        "roles": roles
    }
    return TokenPair(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data)
    )


def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        roles = payload.get("roles", [])
        exp = datetime.fromtimestamp(payload.get("exp"))

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        return TokenData(
            user_id=user_id,
            email=email,
            roles=roles,
            exp=exp
        )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """FastAPI dependency to get authenticated user"""
    token_data = decode_token(token)

    # Get user from database
    result = await db.execute(
        select(User).where(User.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_roles(*required_roles: str):
    """Dependency factory for role-based access"""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        user_roles = set(current_user.roles)
        if not user_roles.intersection(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker
```

### 2.2 User Model

```python
# src/copy_that/domain/models.py

class User(Base):
    """User account model"""
    __tablename__ = "users"

    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password = mapped_column(String(255), nullable=False)
    full_name = mapped_column(String(255), nullable=True)

    # Account status
    is_active = mapped_column(Boolean, default=True)
    is_verified = mapped_column(Boolean, default=False)
    is_superuser = mapped_column(Boolean, default=False)

    # Roles (JSON array)
    roles = mapped_column(JSON, default=["user"])

    # Timestamps
    created_at = mapped_column(DateTime, default=utc_now)
    updated_at = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    last_login = mapped_column(DateTime, nullable=True)

    # Relationships
    projects: Mapped[list["Project"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    api_keys: Mapped[list["APIKey"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class APIKey(Base):
    """API key for programmatic access"""
    __tablename__ = "api_keys"

    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = mapped_column(ForeignKey("users.id"), nullable=False)
    name = mapped_column(String(255), nullable=False)
    key_hash = mapped_column(String(255), nullable=False)  # Hashed key
    key_prefix = mapped_column(String(8), nullable=False)  # First 8 chars for identification

    # Permissions
    scopes = mapped_column(JSON, default=["read"])  # read, write, delete

    # Status
    is_active = mapped_column(Boolean, default=True)
    expires_at = mapped_column(DateTime, nullable=True)
    last_used_at = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at = mapped_column(DateTime, default=utc_now)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="api_keys")
```

### 2.3 Auth Router Implementation

```python
# src/copy_that/interfaces/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["authentication"])


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if email exists
    existing = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/token", response_model=TokenPair)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Authenticate and get tokens"""
    # Get user
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Update last login
    user.last_login = utc_now()
    await db.commit()

    # Generate tokens
    return create_token_pair(user.id, user.email, user.roles)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Get new tokens using refresh token"""
    token_data = decode_token(refresh_token)

    # Verify it's a refresh token
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get user
    result = await db.execute(
        select(User).where(User.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )

    return create_token_pair(user.id, user.email, user.roles)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user
```

### 2.4 Resource Ownership Authorization

```python
# src/copy_that/infrastructure/security/authorization.py

from fastapi import HTTPException, status, Depends

async def get_owned_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Project:
    """Get project and verify ownership"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check ownership
    if project.owner_id != current_user.id:
        # Check if user is admin
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project"
            )

    return project


async def get_owned_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ExtractionSession:
    """Get session and verify ownership through project"""
    result = await db.execute(
        select(ExtractionSession)
        .where(ExtractionSession.id == session_id)
        .options(joinedload(ExtractionSession.project))
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Check ownership through project
    if session.project.owner_id != current_user.id:
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this session"
            )

    return session
```

### 2.5 Updating Routers with Auth

```python
# src/copy_that/interfaces/api/colors.py

from ..security.authentication import get_current_user
from ..security.authorization import get_owned_project

@router.post("/extract")
async def extract_colors(
    request: ExtractColorsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ADD AUTH
    project: Project = Depends(get_owned_project)     # ADD OWNERSHIP CHECK
):
    """Extract colors from image - requires authentication"""
    # ... rest of implementation
```

---

## 3. Defense-in-Depth Strategy

### 3.1 Input Validation Schemas

```python
# src/copy_that/interfaces/api/schemas.py

import re
from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional

# Regex patterns for validation
HEX_COLOR_PATTERN = re.compile(r'^#[0-9A-Fa-f]{6}$')
SAFE_STRING_PATTERN = re.compile(r'^[\w\s\-\.]+$')


class ExtractColorsRequest(BaseModel):
    """Validated color extraction request"""

    project_id: int = Field(..., gt=0)
    max_colors: int = Field(10, ge=1, le=50)

    # Image source (one required)
    image_url: Optional[HttpUrl] = None
    image_base64: Optional[str] = None

    @validator('image_url')
    def validate_url(cls, v):
        if v:
            # Block internal URLs (SSRF protection)
            blocked_hosts = [
                'localhost', '127.0.0.1', '0.0.0.0',
                '169.254.169.254',  # AWS metadata
                '10.', '172.16.', '172.17.', '172.18.',
                '172.19.', '172.20.', '172.21.', '172.22.',
                '172.23.', '172.24.', '172.25.', '172.26.',
                '172.27.', '172.28.', '172.29.', '172.30.',
                '172.31.', '192.168.'
            ]
            url_str = str(v).lower()
            for blocked in blocked_hosts:
                if blocked in url_str:
                    raise ValueError(f"URL host not allowed: {blocked}")

            # Only allow http/https
            if not url_str.startswith(('http://', 'https://')):
                raise ValueError("Only HTTP/HTTPS URLs allowed")

        return v

    @validator('image_base64')
    def validate_base64(cls, v):
        if v:
            # Check size (10MB max after decode ≈ 13.3MB base64)
            max_base64_size = 14 * 1024 * 1024  # 14MB
            if len(v) > max_base64_size:
                raise ValueError("Image too large (max 10MB)")

            # Validate base64 format
            try:
                import base64
                decoded = base64.b64decode(v)
                # Check decoded size
                if len(decoded) > 10 * 1024 * 1024:
                    raise ValueError("Decoded image too large")
            except Exception:
                raise ValueError("Invalid base64 encoding")

        return v

    @validator('image_url', 'image_base64')
    def at_least_one_source(cls, v, values):
        if not v and not values.get('image_url') and not values.get('image_base64'):
            raise ValueError("Either image_url or image_base64 required")
        return v


class ProjectCreate(BaseModel):
    """Validated project creation"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)

    @validator('name')
    def sanitize_name(cls, v):
        # Remove potentially dangerous characters
        v = v.strip()
        # Check for script injection
        if '<script' in v.lower() or 'javascript:' in v.lower():
            raise ValueError("Invalid characters in name")
        return v


class RoleAssignment(BaseModel):
    """Validated role assignment"""

    token_id: int = Field(..., gt=0)
    role: str = Field(...)

    @validator('role')
    def validate_role(cls, v):
        valid_roles = {
            'primary', 'secondary', 'accent', 'success', 'error',
            'warning', 'info', 'background', 'surface', 'text'
        }
        if v.lower() not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        return v.lower()
```

### 3.2 Rate Limiting Implementation

```python
# src/copy_that/infrastructure/security/rate_limiter.py

import time
from typing import Optional
from redis.asyncio import Redis
from fastapi import HTTPException, Request, status

class RateLimiter:
    """Redis-based rate limiting"""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int, int]:
        """
        Check if request is within rate limit

        Returns:
            (allowed, remaining, reset_at)
        """
        current_time = int(time.time())
        window_start = current_time - window_seconds

        # Redis sorted set key
        rate_key = f"ratelimit:{key}"

        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(rate_key, 0, window_start)

        # Count requests in window
        pipe.zcard(rate_key)

        # Add current request
        pipe.zadd(rate_key, {str(current_time): current_time})

        # Set expiry on key
        pipe.expire(rate_key, window_seconds)

        results = await pipe.execute()
        request_count = results[1]

        remaining = max(0, limit - request_count - 1)
        reset_at = current_time + window_seconds

        if request_count >= limit:
            return False, 0, reset_at

        return True, remaining, reset_at


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""

    def __init__(
        self,
        redis: Redis,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        self.limiter = RateLimiter(redis)
        self.per_minute = requests_per_minute
        self.per_hour = requests_per_hour

    async def __call__(self, request: Request, call_next):
        # Get client identifier
        client_id = self._get_client_id(request)

        # Check minute limit
        allowed, remaining, reset = await self.limiter.check_rate_limit(
            f"{client_id}:minute",
            self.per_minute,
            60
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded (per minute)",
                headers={
                    "X-RateLimit-Limit": str(self.per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset),
                    "Retry-After": str(reset - int(time.time()))
                }
            )

        # Check hour limit
        allowed, remaining_hour, reset_hour = await self.limiter.check_rate_limit(
            f"{client_id}:hour",
            self.per_hour,
            3600
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded (per hour)",
                headers={
                    "X-RateLimit-Limit": str(self.per_hour),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_hour),
                    "Retry-After": str(reset_hour - int(time.time()))
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from auth
        if hasattr(request.state, 'user'):
            return f"user:{request.state.user.id}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        return f"ip:{request.client.host}"


# Dependency for endpoint-specific limits
def rate_limit(requests: int, seconds: int):
    """Decorator for endpoint-specific rate limits"""
    async def dependency(
        request: Request,
        redis: Redis = Depends(get_redis)
    ):
        limiter = RateLimiter(redis)
        client_id = request.state.user.id if hasattr(request.state, 'user') else request.client.host

        allowed, remaining, reset = await limiter.check_rate_limit(
            f"{request.url.path}:{client_id}",
            requests,
            seconds
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit: {requests} requests per {seconds}s"
            )

    return Depends(dependency)


# Usage in router:
@router.post("/extract", dependencies=[rate_limit(10, 60)])  # 10 per minute
async def extract_colors(...):
    ...
```

### 3.3 Security Middleware Architecture

```python
# src/copy_that/interfaces/api/middleware/security_headers.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )

        # HSTS (only in production)
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response
```

### 3.4 Error Handling Middleware

```python
# src/copy_that/interfaces/api/middleware/error_handling.py

import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class SecureErrorMiddleware(BaseHTTPMiddleware):
    """Sanitize error responses to prevent information leakage"""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except HTTPException:
            # Re-raise HTTP exceptions (already sanitized)
            raise

        except Exception as e:
            # Log full error internally
            request_id = request.headers.get("X-Request-ID", "unknown")
            logger.error(
                f"Unhandled exception [request_id={request_id}]: {str(e)}",
                exc_info=True
            )

            # Return sanitized error to client
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal error occurred",
                    "request_id": request_id,
                    "support": "Please contact support with this request ID"
                }
            )


# Custom exception handlers
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Sanitize validation errors"""
    # Log full details
    logger.warning(f"Validation error: {exc.errors()}")

    # Return simplified error
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request data",
            "errors": [
                {
                    "field": err["loc"][-1] if err["loc"] else "unknown",
                    "message": err["msg"]
                }
                for err in exc.errors()
            ]
        }
    )
```

### 3.5 CORS Policy Design

```python
# src/copy_that/interfaces/api/main.py

def configure_cors(app: FastAPI):
    """Configure CORS with secure defaults"""

    environment = os.getenv("ENVIRONMENT", "local")

    if environment == "local":
        # Permissive for local development
        origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ]
    elif environment == "staging":
        origins = [
            "https://staging.copythat.dev",
            "https://staging-admin.copythat.dev",
        ]
    else:  # production
        origins = [
            "https://copythat.dev",
            "https://www.copythat.dev",
            "https://admin.copythat.dev",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-API-Key",
        ],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
        max_age=600,  # Cache preflight for 10 minutes
    )
```

### 3.6 Secret Management with GCP

```python
# src/copy_that/infrastructure/security/secrets_manager.py

from google.cloud import secretmanager
from functools import lru_cache
import os

class SecretsManager:
    """GCP Secret Manager integration"""

    def __init__(self, project_id: str = None):
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")

    def get_secret(self, secret_id: str, version: str = "latest") -> str:
        """Get secret value from Secret Manager"""
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"

        try:
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            raise RuntimeError(f"Failed to access secret {secret_id}: {e}")

    @lru_cache(maxsize=100)
    def get_secret_cached(self, secret_id: str) -> str:
        """Get secret with caching (use for non-rotating secrets)"""
        return self.get_secret(secret_id)


# Global instance
_secrets_manager = None

def get_secrets_manager() -> SecretsManager:
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def get_secret(secret_id: str) -> str:
    """Convenience function to get a secret"""
    return get_secrets_manager().get_secret(secret_id)


# Usage in config:
def get_database_url() -> str:
    """Get database URL from Secret Manager or environment"""
    if os.getenv("ENVIRONMENT") in ("staging", "production"):
        return get_secret("database-url")
    return os.getenv("DATABASE_URL")


def get_redis_url() -> str:
    """Get Redis URL from Secret Manager or environment"""
    if os.getenv("ENVIRONMENT") in ("staging", "production"):
        return get_secret("redis-url")
    return os.getenv("REDIS_URL")
```

---

## 4. Dependency Security

### 4.1 Current Dependencies Audit

**Security-Related Packages** (from pyproject.toml):

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| python-jose[cryptography] | >=3.3.0 | JWT | OK |
| passlib[bcrypt] | >=1.7.4 | Password hashing | OK |
| google-cloud-secret-manager | >=2.18.0 | Secrets | OK |
| pydantic | >=2.5.0 | Validation | OK |
| cryptography | (via jose) | Crypto | OK |

### 4.2 Recommended Security Additions

```toml
# pyproject.toml additions

dependencies = [
    # ... existing ...

    # Security scanning
    "safety>=2.3.0",        # Vulnerability scanning
    "bandit>=1.7.0",        # Security linting

    # Additional security
    "python-multipart>=0.0.6",  # Already present
    "limits>=3.0.0",            # Rate limiting library
    "secure>=0.3.0",            # Security headers
]
```

### 4.3 Automated Scanning Integration

```yaml
# .github/workflows/security.yml

name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  security-scan:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install safety bandit pip-audit

      - name: Run Safety check
        run: |
          pip install -e .
          safety check --full-report

      - name: Run Bandit
        run: |
          bandit -r src/copy_that -f json -o bandit-report.json || true
          bandit -r src/copy_that

      - name: Run pip-audit
        run: |
          pip-audit

      - name: Upload reports
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: security-reports
          path: |
            bandit-report.json
```

### 4.4 Pre-commit Security Hooks

```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ['-c', 'bandit.yaml']
        exclude: tests/

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

---

## 5. Implementation Examples

### 5.1 Complete Secure Endpoint Example

```python
# src/copy_that/interfaces/api/colors.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..security.authentication import get_current_user
from ..security.authorization import get_owned_project
from ..security.rate_limiter import rate_limit
from ...domain.models import User, Project, ColorToken
from ...infrastructure.database import get_db

router = APIRouter(prefix="/colors", tags=["colors"])


@router.post(
    "/extract",
    response_model=ColorExtractionResponse,
    dependencies=[rate_limit(10, 60)],  # 10 requests per minute
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        429: {"description": "Rate limit exceeded"},
    }
)
async def extract_colors(
    request: ExtractColorsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Extract colors from an image.

    Requires authentication and project ownership.
    Rate limited to 10 requests per minute.
    """
    # Verify project ownership
    project = await get_owned_project(request.project_id, db, current_user)

    # Validate image source
    if not request.image_url and not request.image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either image_url or image_base64 is required"
        )

    # Log the request (audit trail)
    logger.info(
        f"Color extraction requested",
        extra={
            "user_id": current_user.id,
            "project_id": project.id,
            "has_url": bool(request.image_url),
            "max_colors": request.max_colors
        }
    )

    try:
        # Perform extraction
        extractor = get_extractor()
        result = await extractor.extract(
            image_url=request.image_url,
            image_base64=request.image_base64,
            max_colors=request.max_colors
        )

        # Store results
        for color_data in result.colors:
            token = ColorToken(
                project_id=project.id,
                **color_data.dict()
            )
            db.add(token)

        await db.commit()

        # Log success
        logger.info(
            f"Color extraction completed",
            extra={
                "user_id": current_user.id,
                "project_id": project.id,
                "colors_extracted": len(result.colors)
            }
        )

        return result

    except ExternalAPIError as e:
        # Log but don't expose details
        logger.error(f"AI API error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Color extraction service temporarily unavailable"
        )

    except Exception as e:
        # Log but don't expose details
        logger.error(f"Extraction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Color extraction failed"
        )
```

### 5.2 Application Startup with Security

```python
# src/copy_that/interfaces/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .middleware.security_headers import SecurityHeadersMiddleware
from .middleware.error_handling import SecureErrorMiddleware
from ..security.rate_limiter import RateLimitMiddleware
from ...infrastructure.database import engine
from ...infrastructure.cache.redis_cache import get_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Copy That API")

    # Verify secrets are accessible
    if os.getenv("ENVIRONMENT") in ("staging", "production"):
        try:
            get_secret("database-url")
            logger.info("Secrets Manager connection verified")
        except Exception as e:
            logger.error(f"Failed to access secrets: {e}")
            raise

    yield

    # Shutdown
    logger.info("Shutting down Copy That API")
    await engine.dispose()


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="Copy That API",
        description="Design token extraction platform",
        version="1.0.0",
        lifespan=lifespan,
        # Disable docs in production
        docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
        redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
    )

    # Add middleware (order matters - last added = first executed)

    # 1. Security headers (outermost)
    app.add_middleware(SecurityHeadersMiddleware)

    # 2. Error handling
    app.add_middleware(SecureErrorMiddleware)

    # 3. Rate limiting
    redis = get_redis()
    app.add_middleware(
        RateLimitMiddleware,
        redis=redis,
        requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", 60)),
        requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", 1000))
    )

    # 4. CORS (innermost)
    configure_cors(app)

    # Add routers
    from .auth import router as auth_router
    from .projects import router as projects_router
    from .colors import router as colors_router
    from .sessions import router as sessions_router

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(projects_router, prefix="/api/v1")
    app.include_router(colors_router, prefix="/api/v1")
    app.include_router(sessions_router, prefix="/api/v1")

    # Health check (no auth required)
    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


app = create_application()
```

---

## Summary

### Critical Actions Required

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Implement JWT authentication | 8 hours | Critical |
| 2 | Remove hardcoded secrets | 2 hours | Critical |
| 3 | Add rate limiting | 4 hours | High |
| 4 | Add input validation | 4 hours | High |
| 5 | Add security headers | 1 hour | Medium |

### Security Score Improvement

| Area | Current | After Implementation |
|------|---------|---------------------|
| Authentication | 0/10 | 9/10 |
| Authorization | 0/10 | 8/10 |
| Input Validation | 6/10 | 9/10 |
| Rate Limiting | 0/10 | 8/10 |
| Secrets Management | 2/10 | 9/10 |
| **Overall Security** | **4/10** | **8.5/10** |

---

*Next: [04-implementation-roadmap.md](./04-implementation-roadmap.md)*
