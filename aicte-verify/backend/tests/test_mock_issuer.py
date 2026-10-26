"""Unit tests for SIMULATED issuing authority service."""

import pytest
from app.mock_issuer.service import MockIssuerService


@pytest.mark.asyncio
async def test_mock_issuer_all_six_statuses():
    """Verify that the SIMULATED issuer repository can produce all 6 canonical outcomes."""
    issuer = MockIssuerService()

    # 1. verified
    res_verified = await issuer.verify(
        doc_type="fire_safety_certificate",
        ref_number="CFD/2024/FS-8891",
        submitted_payload={"institution_name": "Apex Institute of Technology"},
    )
    assert res_verified["status"] == "verified"
    assert res_verified["is_simulated"] is True

    # 2. mismatch_detected
    res_mismatch = await issuer.verify(
        doc_type="fire_safety_certificate",
        ref_number="CFD/2024/FS-8891",
        submitted_payload={"institution_name": "Different College Name"},
    )
    assert res_mismatch["status"] == "mismatch_detected"

    # 3. expired
    res_expired = await issuer.verify(
        doc_type="fire_safety_certificate",
        ref_number="CFD/2023/FS-1042-EXPIRED",
    )
    assert res_expired["status"] == "expired"

    # 4. verification_pending
    res_pending = await issuer.verify(
        doc_type="fire_safety_certificate",
        ref_number="TEST-PENDING-001",
    )
    assert res_pending["status"] == "verification_pending"

    # 5. source_unavailable
    res_unavailable = await issuer.verify(
        doc_type="noc",
        ref_number="TEST-TIMEOUT-001",
    )
    assert res_unavailable["status"] == "source_unavailable"

    # 6. manual_review_required
    res_manual = await issuer.verify(
        doc_type="university_affiliation_letter",
        ref_number="UNKNOWN-REF-9999",
    )
    assert res_manual["status"] == "manual_review_required"
