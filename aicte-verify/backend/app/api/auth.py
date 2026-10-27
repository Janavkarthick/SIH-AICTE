"""Authentication and user session management endpoints."""

import time
from collections import defaultdict
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    role_required,
    verify_password,
)
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.audit.service import audit_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory sliding window rate limiter: client_ip -> list of epoch timestamps
LOGIN_ATTEMPTS: dict[str, list[float]] = defaultdict(list)
MAX_LOGIN_ATTEMPTS_PER_MINUTE = 10
LOGIN_WINDOW_SECONDS = 60.0


def check_login_rate_limit(client_ip: str) -> None:
    """Enforce maximum login attempts per minute per IP address."""
    now = time.time()
    attempts = LOGIN_ATTEMPTS[client_ip]
    # Retain only timestamps inside window
    valid_attempts = [ts for ts in attempts if now - ts < LOGIN_WINDOW_SECONDS]
    LOGIN_ATTEMPTS[client_ip] = valid_attempts
    if len(valid_attempts) >= MAX_LOGIN_ATTEMPTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Rate limit exceeded (maximum 10 attempts per minute).",
        )
    LOGIN_ATTEMPTS[client_ip].append(now)


def reset_rate_limiter() -> None:
    """Clear in-memory login attempts (used in test fixtures)."""
    LOGIN_ATTEMPTS.clear()


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user credentials and issue signed JWT access token."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    check_login_rate_limit(client_ip)

    username = None
    password = None

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            username = body.get("username")
            password = body.get("password")
        except Exception:
            pass
    elif "form" in content_type:
        try:
            form = await request.form()
            username = form.get("username")
            password = form.get("password")
        except Exception:
            pass
    else:
        try:
            body = await request.json()
            username = body.get("username")
            password = body.get("password")
        except Exception:
            try:
                form = await request.form()
                username = form.get("username")
                password = form.get("password")
            except Exception:
                pass

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )

    # Normalize username: trim whitespace and support shorthand aliases (e.g., clg3, clg 3 -> college3)
    clean_user = username.strip()
    compact = clean_user.lower().replace(" ", "").replace("_", "").replace("-", "")
    if compact in ["clg1", "clg2", "clg3", "clg4", "clg5", "clg6"]:
        normalized_username = compact.replace("clg", "college")
    else:
        normalized_username = clean_user

    stmt = select(User).where((User.username == normalized_username) | (User.email == normalized_username))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact system administrator.",
        )

    client_ip = request.client.host if request.client else "unknown"
    await audit_service.log_login(db, user, client_ip)

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "id": user.id},
        expires_delta=expires_delta,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/register", response_model=UserResponse, dependencies=[Depends(role_required("admin"))])
async def register_user(
    payload: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account (Admin only)."""
    # Check for existing username or email
    stmt = select(User).where((User.username == payload.username) | (User.email == payload.email))
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        region=payload.region,
        institution_id=payload.institution_id,
        is_active=payload.is_active,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse.model_validate(new_user)


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Retrieve details for the currently authenticated user."""
    return UserResponse.model_validate(current_user)
