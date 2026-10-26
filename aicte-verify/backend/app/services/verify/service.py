"""External Verification Service and Pluggable Verification Adapters.

Implements strategy pattern for QR code cross-referencing, certificate reference lookups,
and digital signature validations.
Connects with mock_issuer service for SIMULATED state verification.
"""

from abc import ABC, abstractmethod
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mock_issuer.service import mock_issuer_service
from app.models.document import Document, ExtractedData
from app.models.flag import Flag
from app.models.verification import VerificationResult


class VerificationStrategy(ABC):
    """Abstract strategy interface for document verification."""

    @abstractmethod
    async def verify(
        self,
        document: Document,
        extracted_fields: Dict[str, str],
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """Perform verification and return normalized result payload."""
        pass


class QRVerification(VerificationStrategy):
    """Verification strategy decoding QR code payloads and validating signatures against issuers."""

    async def verify(
        self,
        document: Document,
        extracted_fields: Dict[str, str],
        db: AsyncSession,
    ) -> Dict[str, Any]:
        qr_payload = extracted_fields.get("qr_code_payload")
        ref_number = extracted_fields.get("certificate_number") or extracted_fields.get("qr_ref_number")

        if not qr_payload and not ref_number:
            return {
                "status": "manual_review_required",
                "source_name": "QR Verification Subsystem (SIMULATED)",
                "source_response": {"message": "No readable QR code or certificate reference found in document"},
                "discrepancies": ["Document lacks machine-readable QR identifier"],
            }

        # Query SIMULATED issuer repository
        ref_to_query = ref_number or "QR-EXTRACTED-REF"
        mock_result = await mock_issuer_service.verify(
            doc_type=document.document_type,
            ref_number=ref_to_query,
            submitted_payload=extracted_fields,
        )

        return {
            "status": mock_result["status"],
            "source_name": f"{mock_result.get('issuer_name', 'SIMULATED Issuer')} [QR Verification]",
            "source_response": mock_result,
            "discrepancies": mock_result.get("discrepancies", []),
        }


class ReferenceLookup(VerificationStrategy):
    """Verification strategy querying external registry via certificate registration number."""

    async def verify(
        self,
        document: Document,
        extracted_fields: Dict[str, str],
        db: AsyncSession,
    ) -> Dict[str, Any]:
        ref_number = extracted_fields.get("certificate_number")

        if not ref_number:
            return {
                "status": "manual_review_required",
                "source_name": "Direct Authority Lookup (SIMULATED)",
                "source_response": {"message": "Certificate reference number missing from extracted fields"},
                "discrepancies": ["No certificate reference number identified for registry lookup"],
            }

        mock_result = await mock_issuer_service.verify(
            doc_type=document.document_type,
            ref_number=ref_number,
            submitted_payload=extracted_fields,
        )

        return {
            "status": mock_result["status"],
            "source_name": mock_result.get("issuer_name", "SIMULATED State Authority Gateway"),
            "source_response": mock_result,
            "discrepancies": mock_result.get("discrepancies", []),
        }


class DigitalSignatureCheck(VerificationStrategy):
    """Verification strategy validating PDF cryptographic PKI certificates."""

    async def verify(
        self,
        document: Document,
        extracted_fields: Dict[str, str],
        db: AsyncSession,
    ) -> Dict[str, Any]:
        # SIMULATED / pyHanko cryptographic check
        from app.services.forensics.service import forensics_service

        findings = forensics_service.verify_digital_signature(document.file_path)
        sig_found = any(f.passed for f in findings)

        if sig_found:
            return {
                "status": "verified",
                "source_name": "Government PKI Root CA (SIMULATED)",
                "source_response": {"signature_valid": True, "chain_verified": True},
                "discrepancies": [],
            }
        else:
            return {
                "status": "manual_review_required",
                "source_name": "Government PKI Root CA (SIMULATED)",
                "source_response": {"signature_valid": False, "note": "Unsigned physical scan"},
                "discrepancies": ["Document lacks cryptographic digital signature seal"],
            }


class VerificationService:
    """Orchestrates document authenticity verification across pluggable strategies."""

    def __init__(self):
        self._strategies: Dict[str, VerificationStrategy] = {
            "qr": QRVerification(),
            "reference_lookup": ReferenceLookup(),
            "digital_signature": DigitalSignatureCheck(),
        }

    async def verify_document(
        self,
        db: AsyncSession,
        document_id: int,
        strategy_type: str = "reference_lookup",
        verified_by_user_id: Optional[int] = None,
    ) -> VerificationResult:
        """Run verification using requested strategy and persist audit record and flags."""
        stmt = select(Document).where(Document.id == document_id)
        res = await db.execute(stmt)
        document = res.scalar_one_or_none()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Fetch extracted data
        ext_stmt = select(ExtractedData).where(ExtractedData.document_id == document_id)
        ext_res = await db.execute(ext_stmt)
        extracted_fields = {e.field_name: e.field_value for e in ext_res.scalars().all() if e.field_value}

        strategy = self._strategies.get(strategy_type, self._strategies["reference_lookup"])
        outcome = await strategy.verify(document, extracted_fields, db)

        status_result = outcome["status"]
        discrepancies = outcome.get("discrepancies", [])
        source_resp_json = json.dumps(outcome.get("source_response", {}))
        submitted_data_json = json.dumps(extracted_fields)
        discrepancies_json = json.dumps(discrepancies) if discrepancies else None

        # Check existing result or create new
        existing_stmt = select(VerificationResult).where(
            VerificationResult.document_id == document_id,
            VerificationResult.verification_type == strategy_type,
        )
        existing_res = await db.execute(existing_stmt)
        record = existing_res.scalar_one_or_none()

        if record:
            record.status = status_result
            record.source_name = outcome["source_name"]
            record.source_response_json = source_resp_json
            record.submitted_data_json = submitted_data_json
            record.discrepancies_json = discrepancies_json
            record.verified_at = datetime.now(timezone.utc)
            record.verified_by = verified_by_user_id
        else:
            record = VerificationResult(
                document_id=document_id,
                verification_type=strategy_type,
                status=status_result,
                source_name=outcome["source_name"],
                source_response_json=source_resp_json,
                submitted_data_json=submitted_data_json,
                discrepancies_json=discrepancies_json,
                verified_at=datetime.now(timezone.utc),
                verified_by=verified_by_user_id,
            )
            db.add(record)

        # Update document status
        if status_result == "verified":
            document.status = "verified"
        elif status_result in ["mismatch_detected", "expired"]:
            document.status = "flagged"
            # Create Flag
            db.add(
                Flag(
                    application_id=document.application_id,
                    document_id=document.id,
                    flag_type="verification",
                    severity="critical" if status_result == "mismatch_detected" else "high",
                    code=f"VER-{status_result.upper().replace('_', '-')}",
                    title=f"Issuer Verification: {status_result.replace('_', ' ').title()}",
                    reason=f"Issuing body reported status '{status_result}': {', '.join(discrepancies) if discrepancies else 'Check failed'}",
                    evidence_json=source_resp_json,
                    rule_id="VERIFICATION-STATUS-CHECK",
                    check_name="External Authority Verification",
                )
            )

        await db.commit()
        await db.refresh(record)
        return record


# Singleton instance
verification_service = VerificationService()
