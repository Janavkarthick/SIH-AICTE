"""Security, authentication, and privacy module for AICTE-Verify.

Provides Argon2 password hashing, PyJWT token handling, role-based authorization
dependencies, and PII masking for sensitive data protection.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plain text password using Argon2id."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against an Argon2 hash."""
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, Exception):
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token with an expiration timestamp."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Dependency to retrieve the authenticated user from the database."""
    # Delayed import to avoid circular dependency
    from app.models.user import User

    payload = decode_access_token(token)
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


def role_required(*allowed_roles: str) -> Callable:
    """Dependency factory restricting route access to specified roles."""
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


def mask_pii(text: Optional[str]) -> Optional[str]:
    """Mask Aadhaar-like 12-digit IDs, phone numbers, and sensitive identifiers.
    
    Replaces 12-digit Aadhaar pattern with 'XXXX-XXXX-<last4>'.
    Replaces 10-digit Indian phone numbers with 'XXXXXX<last4>'.
    """
    if not text:
        return text

    # Mask Aadhaar numbers (with optional spaces or hyphens)
    # e.g., 1234 5678 9012 or 1234-5678-9012 or 123456789012
    def replace_aadhaar(match):
        digits = re.sub(r"\D", "", match.group(0))
        if len(digits) == 12:
            return f"XXXX-XXXX-{digits[-4:]}"
        return match.group(0)

    aadhaar_pattern = r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
    masked_text = re.sub(aadhaar_pattern, replace_aadhaar, text)

    # Mask Indian mobile phone numbers (10 digits starting with 6, 7, 8, or 9)
    # Supports optional +91 or 0 prefix
    def replace_phone(match):
        raw = match.group(0)
        digits = re.sub(r"\D", "", raw)
        last4 = digits[-4:]
        prefix = "+91-" if "+91" in raw else ""
        return f"{prefix}XXXXXX{last4}"

    phone_pattern = r"(?:\+91[\s-]?)?[6-9]\d{9}\b"
    masked_text = re.sub(phone_pattern, replace_phone, masked_text)

    return masked_text
