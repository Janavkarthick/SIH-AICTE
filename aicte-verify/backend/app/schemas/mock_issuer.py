"""Pydantic schemas for SIMULATED issuer registration and verification checks."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class MockCertRegister(BaseModel):
    """Payload to register a certificate in the SIMULATED issuer repository."""
    doc_type: str = Field(..., description="fire_safety_certificate, noc, accreditation_certificate, university_affiliation_letter")
    ref_number: str = Field(..., description="Unique certificate registration reference number")
    institution_name: str
    issue_date: str
    expiry_date: Optional[str] = None
    issuing_authority: str
    is_valid: bool = True
    payload: Dict[str, Any] = {}
    is_simulated: bool = Field(True, description="Always marked SIMULATED")


class MockCertResponse(BaseModel):
    """Outcome returned from SIMULATED issuer query."""
    status: str  # verified, mismatch_detected, expired, verification_pending, source_unavailable, manual_review_required
    doc_type: str
    ref_number: str
    issuer_name: str
    certificate_data: Optional[Dict[str, Any]] = None
    message: str
    is_simulated: bool = True
