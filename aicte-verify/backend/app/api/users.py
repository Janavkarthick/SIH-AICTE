"""User management and role administration endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, role_required
from app.models.user import User
from app.schemas.user import UserResponse, UserRoleUpdate

router = APIRouter(prefix="/users", tags=["Users Management"], dependencies=[Depends(role_required("admin"))])


@router.get("", response_model=List[UserResponse], include_in_schema=False)
@router.get("/", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all user accounts across roles (Admin only)."""
    stmt = select(User).order_by(User.id.asc())
    users = list((await db.execute(stmt)).scalars().all())
    return [UserResponse.model_validate(u) for u in users]


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change authorization role of a user (Admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.role not in ["admin", "officer", "college_user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be one of: admin, officer, college_user",
        )

    user.role = payload.role
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a user account (Admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators cannot deactivate their own account.",
        )

    user.is_active = False
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)
