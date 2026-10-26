"""Pydantic schemas for tamper-evident audit ledger entries and cryptographic verification."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class AuditEntryResponse(BaseModel):
    """Immutable audit entry."""
    id: int
    actor_id: Optional[int] = None
    actor_username: str
    action: str
    details_json: str
    rule_check: Optional[str] = None
    records_checked: int = 0
    source_response: Optional[str] = None
    timestamp: datetime
    entry_hash: str
    previous_hash: str

    # Compatibility fields for frontend
    actor_name: Optional[str] = None
    actor_role: Optional[str] = None
    details: Optional[str] = None
    prev_hash: Optional[str] = None
    curr_hash: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AuditListResponse(BaseModel):
    """Paginated list of audit records."""
    total: int
    items: List[AuditEntryResponse]


class AuditChainVerification(BaseModel):
    """Verification outcome of cryptographic hash chain."""
    valid: bool
    verified_count: int
    tampered_entry_id: Optional[int] = None
    reason: str

    # Compatibility aliases
    is_valid: Optional[bool] = None
    total_blocks: Optional[int] = None
    error_message: Optional[str] = None
