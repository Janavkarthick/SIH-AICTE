"""Pydantic schemas for external issuer verification results and review workflows."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class VerificationTriggerRequest(BaseModel):
    """Payload to trigger verification check for a document."""
    verification_type: str = Field("reference_lookup", description="qr, reference_lookup, or digital_signature")
    force_refresh: bool = False


class VerificationResponse(BaseModel):
    """Authoritative outcome returned by verification engine."""
    id: int
    document_id: int
    verification_type: str
    status: str = Field(
        ...,
        description="verified, mismatch_detected, expired, verification_pending, source_unavailable, manual_review_required"
    )
    source_name: str
    source_response_json: Optional[str] = None
    submitted_data_json: Optional[str] = None
    discrepancies_json: Optional[str] = None
    verified_at: datetime
    verified_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ManualReviewQueueItem(BaseModel):
    """Queue entry for documents requiring manual officer examination."""
    document_id: int
    application_id: int
    institution_name: str
    document_type: str
    verification_status: str
    reason: str
    uploaded_at: datetime
