"""SIMULATED issuing authority test endpoints and mock registry administration."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from app.core.security import get_current_user
from app.mock_issuer.service import mock_issuer_service
from app.models.user import User
from app.schemas.mock_issuer import MockCertRegister, MockCertResponse

router = APIRouter(prefix="/mock-issuer", tags=["SIMULATED Issuing Authorities"])


@router.get("/verify/{doc_type}/{ref_number}", response_model=MockCertResponse)
async def verify_certificate_with_issuer(
    doc_type: str,
    ref_number: str,
    institution_name: Optional[str] = Query(None, description="Optional institution name cross-check"),
    intake: Optional[int] = Query(None, description="Optional approved intake cross-check"),
):
    """SIMULATED: Query external issuer database to verify certificate authenticity.
    
    Produces ALL 6 canonical verification statuses:
    - verified
    - mismatch_detected
    - expired
    - verification_pending
    - source_unavailable (connection timeout)
    - manual_review_required
    """
    payload: Dict[str, Any] = {}
    if institution_name:
        payload["institution_name"] = institution_name
    if intake:
        payload["intake"] = intake

    result = await mock_issuer_service.verify(
        doc_type=doc_type,
        ref_number=ref_number,
        submitted_payload=payload if payload else None,
    )
    return MockCertResponse(
        status=result["status"],
        doc_type=doc_type,
        ref_number=ref_number,
        issuer_name=result.get("issuer_name", "SIMULATED Authority"),
        certificate_data=result.get("certificate_data"),
        message=result.get("message", "SIMULATED Verification Query"),
        is_simulated=True,
    )


@router.get("/registry", response_model=List[Dict[str, Any]])
async def get_mock_issuer_registry():
    """SIMULATED: List all pre-registered certificates in the mock authority repository."""
    return mock_issuer_service.list_all()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_mock_certificate(payload: MockCertRegister):
    """SIMULATED: Add a certificate record into the simulated issuer registry."""
    record = mock_issuer_service.register_certificate(payload.model_dump())
    return {
        "status": "registered",
        "certificate": record,
        "is_simulated": True,
    }
