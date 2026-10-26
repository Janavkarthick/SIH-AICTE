"""Pydantic schemas for discrepancy and risk flags."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class FlagBase(BaseModel):
    """Core attributes for a regulatory or forensic discrepancy."""
    application_id: int
    document_id: Optional[int] = None
    flag_type: str = Field(..., description="validation, forensics, verification, compliance, anomaly")
    severity: str = Field(..., description="info, low, medium, high, critical")
    code: str = Field(..., description="Machine-readable code e.g. VAL-001")
    title: str
    reason: str
    evidence_json: Optional[str] = None
    confidence: float = 1.0
    rule_id: Optional[str] = None
    check_name: Optional[str] = None


class FlagCreate(FlagBase):
    """Schema to create a new flag."""
    pass


class FlagResolve(BaseModel):
    """Schema for an approving officer resolving a flag."""
    resolution_note: str = Field(..., min_length=5, description="Auditable justification for flag resolution")
    confirmed: bool = Field(..., description="Officer explicit confirmation checkbox")


class FlagResponse(FlagBase):
    """Full flag representation."""
    id: int
    is_resolved: bool
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertItem(BaseModel):
    """Summary of high priority operational alert."""
    id: int
    application_id: int
    document_id: Optional[int] = None
    category: str
    severity: str
    message: str
    created_at: datetime
