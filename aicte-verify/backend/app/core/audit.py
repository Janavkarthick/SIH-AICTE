"""Cryptographically verifiable append-only audit trail module.

Maintains an immutable SHA-256 hash chain for all administrative actions,
automated validation runs, document uploads, and verification checks.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


def compute_canonical_json(data: Any) -> str:
    """Produce deterministic canonical JSON string for hashing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def compute_entry_hash(prev_hash: str, payload_dict: Dict[str, Any]) -> str:
    """Compute SHA-256 hash of previous hash plus canonical JSON of entry content."""
    canonical = compute_canonical_json(payload_dict)
    hasher = hashlib.sha256()
    hasher.update(prev_hash.encode("utf-8"))
    hasher.update(b":")
    hasher.update(canonical.encode("utf-8"))
    return hasher.hexdigest()


class AuditLogger:
    """Service to create cryptographically linked append-only audit entries."""

    @staticmethod
    async def log(
        db: AsyncSession,
        action: str,
        actor_id: Optional[int] = None,
        actor_username: str = "system",
        details: Optional[Dict[str, Any]] = None,
        rule_check: Optional[str] = None,
        records_checked: int = 0,
        source_response: Optional[str] = None,
    ):
        """Append a new verified audit record to the tamper-evident log chain."""
        # Delayed import to avoid circular dependencies
        from app.models.audit import AuditEntry

        # 1. Fetch previous head entry
        stmt = select(AuditEntry).order_by(AuditEntry.id.desc()).limit(1)
        res = await db.execute(stmt)
        last_entry = res.scalar_one_or_none()

        prev_hash = last_entry.entry_hash if last_entry else "0" * 64
        now_utc = datetime.now(timezone.utc)
        timestamp_str = now_utc.strftime("%Y-%m-%dT%H:%M:%S")

        payload_dict = {
            "action": action,
            "actor_id": actor_id,
            "actor_username": actor_username,
            "details": details or {},
            "records_checked": records_checked,
            "rule_check": rule_check,
            "source_response": source_response,
            "timestamp": timestamp_str,
        }

        entry_hash = compute_entry_hash(prev_hash, payload_dict)

        new_entry = AuditEntry(
            actor_id=actor_id,
            actor_username=actor_username,
            action=action,
            details_json=compute_canonical_json(details or {}),
            rule_check=rule_check,
            records_checked=records_checked,
            source_response=source_response,
            timestamp=now_utc,
            entry_hash=entry_hash,
            previous_hash=prev_hash,
        )

        db.add(new_entry)
        await db.commit()
        await db.refresh(new_entry)
        return new_entry


async def verify_chain(db: AsyncSession) -> Dict[str, Any]:
    """Validate cryptographic integrity of the entire audit chain."""
    from app.models.audit import AuditEntry

    stmt = select(AuditEntry).order_by(AuditEntry.id.asc())
    result = await db.execute(stmt)
    entries: List[AuditEntry] = list(result.scalars().all())

    if not entries:
        return {
            "valid": True,
            "verified_count": 0,
            "tampered_entry_id": None,
            "reason": "Chain is empty (genesis pending)",
        }

    expected_prev_hash = "0" * 64

    for entry in entries:
        # Check chain link
        if entry.previous_hash != expected_prev_hash:
            return {
                "valid": False,
                "verified_count": len(entries),
                "tampered_entry_id": entry.id,
                "reason": f"Previous hash mismatch at ID {entry.id}. Expected {expected_prev_hash}, got {entry.previous_hash}",
            }

        # Parse stored details
        try:
            details_dict = json.loads(entry.details_json) if entry.details_json else {}
        except Exception:
            details_dict = {}

        # Reconstruct canonical payload
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

        recalculated_hash = compute_entry_hash(entry.previous_hash, payload_dict)
        if recalculated_hash != entry.entry_hash:
            return {
                "valid": False,
                "verified_count": len(entries),
                "tampered_entry_id": entry.id,
                "reason": f"Content hash mismatch at ID {entry.id}. Data has been modified.",
            }

        expected_prev_hash = entry.entry_hash

    return {
        "valid": True,
        "verified_count": len(entries),
        "tampered_entry_id": None,
        "reason": f"Cryptographic integrity verified across all {len(entries)} audit records",
    }


async def simulate_tamper(db: AsyncSession, entry_id: Optional[int] = None) -> Dict[str, Any]:
    """Simulate unauthorized database record alteration for tamper-detection testing.
    
    SIMULATED: Only permitted when DEBUG=True. Modifies details_json without updating hash.
    """
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tamper simulation is strictly disabled outside development/test mode.",
        )

    from app.models.audit import AuditEntry

    if entry_id is not None:
        stmt = select(AuditEntry).where(AuditEntry.id == entry_id)
    else:
        stmt = select(AuditEntry).order_by(AuditEntry.id.desc()).limit(1)

    res = await db.execute(stmt)
    entry = res.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No audit entry available to tamper with",
        )

    original_details = entry.details_json
    tampered_data = {"TAMPERED_BY_TEST": True, "unauthorized_change": "Injected fraudulent approval flag"}
    entry.details_json = json.dumps(tampered_data)
    # Deliberately do not recompute entry.entry_hash!

    await db.commit()
    await db.refresh(entry)

    return {
        "status": "SIMULATED_TAMPER_SUCCESS",
        "entry_id": entry.id,
        "original_details": original_details,
        "tampered_details": entry.details_json,
        "hash_remained_unchanged": entry.entry_hash,
        "message": "Audit entry modified without hash recalculation. Running verify_chain() will now detect violation.",
    }
