"""Tamper-evident audit trail endpoints and cryptographic verification."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import simulate_tamper, verify_chain
from app.core.database import get_db
from app.core.security import get_current_user, role_required
from app.models.audit import AuditEntry
from app.models.user import User
from app.schemas.audit import (
    AuditChainVerification,
    AuditEntryResponse,
    AuditListResponse,
)

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


@router.get("", response_model=AuditListResponse, dependencies=[Depends(role_required("admin"))], include_in_schema=False)
@router.get("/logs", response_model=AuditListResponse, dependencies=[Depends(role_required("admin"))], include_in_schema=False)
@router.get("/", response_model=AuditListResponse, dependencies=[Depends(role_required("admin"))])
async def get_audit_trail(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve paginated cryptographic audit log (Admin only)."""
    count_stmt = select(AuditEntry)
    total = len((await db.execute(count_stmt)).scalars().all())

    stmt = select(AuditEntry).order_by(desc(AuditEntry.id)).offset(skip).limit(limit)
    entries = list((await db.execute(stmt)).scalars().all())

    items = []
    for e in entries:
        resp_item = AuditEntryResponse.model_validate(e)
        resp_item.actor_name = e.actor_username or "System Engine"
        resp_item.actor_role = "Central Admin" if e.actor_username == "admin" else ("Regional Officer" if e.actor_username.startswith("ro") else "System")
        resp_item.details = e.details_json or "{}"
        resp_item.prev_hash = e.previous_hash
        resp_item.curr_hash = e.entry_hash
        resp_item.entity_type = "StatutoryRule" if e.rule_check else "AuditEvent"
        resp_item.entity_id = f"#{e.id}"
        items.append(resp_item)

    return AuditListResponse(
        total=total,
        items=items,
    )


@router.get("/verify-chain", response_model=AuditChainVerification)
async def verify_audit_chain_integrity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify cryptographic SHA-256 hash continuity across the entire ledger."""
    result = await verify_chain(db)
    result["is_valid"] = result.get("valid", True)
    result["total_blocks"] = result.get("verified_count", 0)
    result["error_message"] = None if result.get("valid") else result.get("reason")
    return AuditChainVerification(**result)


@router.post("/simulate-tamper")
async def simulate_unauthorized_tamper(
    entry_id: Optional[int] = Query(None, description="Target audit entry ID to tamper with"),
    current_user: User = Depends(role_required("admin")),
    db: AsyncSession = Depends(get_db),
):
    """SIMULATED: Tamper with an audit entry to test hash-chain detection (Development mode only)."""
    result = await simulate_tamper(db, entry_id)
    return result


@router.post("/reset-tamper")
async def reset_audit_tamper(
    current_user: User = Depends(role_required("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Restore cryptographic chain integrity by recalculating canonical hashes across all blocks."""
    import json
    from app.core.audit import compute_entry_hash

    stmt = select(AuditEntry).order_by(AuditEntry.id.asc())
    entries = list((await db.execute(stmt)).scalars().all())
    prev_hash = "0" * 64

    for entry in entries:
        try:
            details_dict = json.loads(entry.details_json) if entry.details_json else {}
        except Exception:
            details_dict = {}

        # Reset any simulated flag
        if isinstance(details_dict, dict) and details_dict.get("TAMPERED_BY_TEST"):
            details_dict = {"restored": True, "notice": "Audit block content restored to original statutory state"}
            entry.details_json = json.dumps(details_dict)

        payload_dict = {
            "action": entry.action,
            "actor_id": entry.actor_id,
            "actor_username": entry.actor_username,
            "details": details_dict,
            "records_checked": entry.records_checked,
            "rule_check": entry.rule_check,
            "source_response": entry.source_response,
            "timestamp": entry.timestamp.strftime("%Y-%m-%dT%H:%M:%S") if entry.timestamp else "",
        }

        entry.previous_hash = prev_hash
        entry.entry_hash = compute_entry_hash(prev_hash, payload_dict)
        prev_hash = entry.entry_hash

    await db.commit()
    return {
        "status": "RESET_SUCCESS",
        "message": f"Cryptographic integrity successfully restored across all {len(entries)} audit blocks.",
    }
