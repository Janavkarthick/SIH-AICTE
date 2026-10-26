"""Regulatory discrepancy flag resolution and operational alert endpoints."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, role_required
from app.models.application import Application
from app.models.flag import Flag
from app.models.user import User
from app.schemas.flag import AlertItem, FlagResolve, FlagResponse
from app.services.audit.service import audit_service

router = APIRouter(tags=["Flags & Alerts"])


@router.get("/flags", response_model=List[FlagResponse], include_in_schema=False)
@router.get("/flags/", response_model=List[FlagResponse])
async def list_flags(
    application_id: Optional[int] = None,
    flag_type: Optional[str] = None,
    severity: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List regulatory and forensic discrepancy flags across applications."""
    stmt = select(Flag)
    if application_id:
        stmt = stmt.where(Flag.application_id == application_id)
    if flag_type:
        stmt = stmt.where(Flag.flag_type == flag_type)
    if severity:
        stmt = stmt.where(Flag.severity == severity)
    if is_resolved is not None:
        stmt = stmt.where(Flag.is_resolved == is_resolved)

    stmt = stmt.order_by(desc(Flag.created_at))
    results = list((await db.execute(stmt)).scalars().all())
    return [FlagResponse.model_validate(f) for f in results]


@router.get("/flags/{application_id}", response_model=List[FlagResponse])
@router.get("/applications/{application_id}/flags", response_model=List[FlagResponse], include_in_schema=False)
async def get_application_flags(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all discrepancy flags attached to an application."""
    stmt = select(Flag).where(Flag.application_id == application_id).order_by(desc(Flag.created_at))
    results = list((await db.execute(stmt)).scalars().all())
    return [FlagResponse.model_validate(f) for f in results]


@router.put("/flags/{flag_id}/resolve", response_model=FlagResponse, dependencies=[Depends(role_required("officer", "admin"))])
@router.patch("/flags/{flag_id}/resolve", response_model=FlagResponse, dependencies=[Depends(role_required("officer", "admin"))], include_in_schema=False)
async def resolve_flag(
    flag_id: int,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Formally resolve and clear a discrepancy flag with officer audit justification."""
    note = payload.get("resolution_note") or payload.get("notes") or payload.get("resolution_notes") or "Resolved by officer"

    flag = await db.get(Flag, flag_id)
    if not flag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flag not found")

    flag.is_resolved = True
    flag.resolved_by = current_user.id
    flag.resolved_at = datetime.now(timezone.utc)
    flag.resolution_note = note

    await db.commit()
    await db.refresh(flag)

    # Log to cryptographic audit ledger
    await audit_service.log_flag_resolve(
        db,
        user=current_user,
        flag_id=flag.id,
        flag_code=flag.code,
        resolution_note=note,
    )

    return FlagResponse.model_validate(flag)



@router.get("/alerts/", response_model=List[AlertItem])
async def get_system_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve urgent operational alerts (missing docs, expired certificates, pending tasks)."""
    stmt = (
        select(Flag)
        .where(Flag.is_resolved == False, Flag.severity.in_(["high", "critical"]))
        .order_by(desc(Flag.created_at))
        .limit(20)
    )
    flags = (await db.execute(stmt)).scalars().all()

    alerts = [
        AlertItem(
            id=f.id,
            application_id=f.application_id,
            document_id=f.document_id,
            category=f.flag_type,
            severity=f.severity,
            message=f"{f.title}: {f.reason[:120]}...",
            created_at=f.created_at,
        )
        for f in flags
    ]
    return alerts
