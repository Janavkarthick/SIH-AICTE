"""SIMULATED External Issuer Authority Registry Service.

This module simulates external issuing authorities including:
1. Fictional State University (Affiliation Letters)
2. City Fire Department (Fire Safety Certificates)
3. State Pollution Control Board (NOCs)
4. National Accreditation Body (Accreditation Certificates)

SIMULATED: All certificate checks, status outcomes, and endpoints are simulated for regulatory demonstration.
Must produce ALL 6 verification statuses:
- verified
- mismatch_detected
- expired
- verification_pending
- source_unavailable (e.g. simulated connection timeout)
- manual_review_required
"""

import asyncio
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from app.core.config import settings


class MockIssuerService:
    """SIMULATED repository of certificates issued by external state/national bodies."""

    def __init__(self):
        # In-memory registry: key = (doc_type, ref_number.upper().strip())
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._seed_default_simulated_certificates()

    def _seed_default_simulated_certificates(self):
        """Seed registry with realistic synthetic certificates across fictional issuing bodies."""
        default_certs = [
            # 1. Fire Safety Certificates (City Fire Department)
            {
                "doc_type": "fire_safety_certificate",
                "ref_number": "CFD/2024/FS-8891",
                "institution_name": "Apex Institute of Technology",
                "issue_date": "2024-06-15",
                "expiry_date": "2028-06-14",
                "issuing_authority": "City Fire & Emergency Services Department",
                "is_valid": True,
                "payload": {"floors_inspected": 4, "hydrants_operational": True, "noc_status": "APPROVED"},
            },
            {
                "doc_type": "fire_safety_certificate",
                "ref_number": "CFD/2023/FS-1042-EXPIRED",
                "institution_name": "Zenith Engineering College",
                "issue_date": "2023-01-10",
                "expiry_date": "2024-01-09",
                "issuing_authority": "City Fire & Emergency Services Department",
                "is_valid": False,
                "payload": {"floors_inspected": 3, "noc_status": "EXPIRED"},
            },
            # 2. State Pollution Control Board (NOC)
            {
                "doc_type": "noc",
                "ref_number": "SPCB/NOC/2024/774",
                "institution_name": "Apex Institute of Technology",
                "issue_date": "2024-03-20",
                "expiry_date": "2025-03-19",
                "issuing_authority": "State Pollution Control Board",
                "is_valid": True,
                "payload": {"effluent_treatment_plant": "Compliant", "dg_set_emissions": "Permitted"},
            },
            # 3. Fictional State University (Affiliation Letters)
            {
                "doc_type": "university_affiliation_letter",
                "ref_number": "FSU/AFFIL/2024-25/1109",
                "institution_name": "Apex Institute of Technology",
                "issue_date": "2024-05-10",
                "expiry_date": "2025-05-09",
                "issuing_authority": "Fictional State University Examination & Affiliation Board",
                "is_valid": True,
                "payload": {"affiliated_courses": ["CSE", "ECE", "MECH"], "approved_intake": 480},
            },
            # 4. National Accreditation Body
            {
                "doc_type": "accreditation_certificate",
                "ref_number": "NAB/NBA/2022/8821",
                "institution_name": "Apex Institute of Technology",
                "issue_date": "2022-07-01",
                "expiry_date": "2027-06-30",
                "issuing_authority": "National Accreditation Body",
                "is_valid": True,
                "payload": {"grade": "A+", "score": 3.42, "accredited_programs": ["CSE", "ECE"]},
            },
            # Special test certificates to deterministically trigger specific statuses
            {
                "doc_type": "fire_safety_certificate",
                "ref_number": "TEST-PENDING-001",
                "institution_name": "Test College",
                "issue_date": "2024-01-01",
                "expiry_date": "2025-01-01",
                "issuing_authority": "City Fire Department",
                "is_valid": True,
                "payload": {"force_status": "verification_pending"},
            },
            {
                "doc_type": "noc",
                "ref_number": "TEST-TIMEOUT-001",
                "institution_name": "Test College",
                "issue_date": "2024-01-01",
                "expiry_date": "2025-01-01",
                "issuing_authority": "State Pollution Control Board",
                "is_valid": True,
                "payload": {"force_status": "source_unavailable"},
            },
            {
                "doc_type": "university_affiliation_letter",
                "ref_number": "TEST-MANUAL-001",
                "institution_name": "Test College",
                "issue_date": "2024-01-01",
                "expiry_date": "2025-01-01",
                "issuing_authority": "Fictional State University",
                "is_valid": True,
                "payload": {"force_status": "manual_review_required"},
            },
        ]

        for cert in default_certs:
            self.register_certificate(cert)

    def _make_key(self, doc_type: str, ref_number: str) -> str:
        return f"{doc_type.lower().strip()}::{ref_number.upper().strip()}"

    def register_certificate(self, cert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a synthetic certificate in the simulated authority registry."""
        doc_type = cert_data["doc_type"]
        ref_number = cert_data["ref_number"]
        key = self._make_key(doc_type, ref_number)
        record = {
            "doc_type": doc_type,
            "ref_number": ref_number,
            "institution_name": cert_data.get("institution_name", "Unknown Institution"),
            "issue_date": cert_data.get("issue_date", str(date.today())),
            "expiry_date": cert_data.get("expiry_date"),
            "issuing_authority": cert_data.get("issuing_authority", "SIMULATED Regulatory Authority"),
            "is_valid": cert_data.get("is_valid", True),
            "payload": cert_data.get("payload", {}),
            "is_simulated": True,
        }
        self._registry[key] = record
        return record

    def list_all(self) -> List[Dict[str, Any]]:
        """Return all certificates currently in the SIMULATED registry."""
        return list(self._registry.values())

    async def verify(
        self,
        doc_type: str,
        ref_number: str,
        submitted_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """SIMULATED verification engine against simulated issuing authority databases.
        
        Returns one of the 6 canonical statuses:
        - verified
        - mismatch_detected
        - expired
        - verification_pending
        - source_unavailable
        - manual_review_required
        """
        ref_clean = ref_number.upper().strip()
        doc_clean = doc_type.lower().strip()
        key = self._make_key(doc_clean, ref_clean)

        # 1. Deterministic status triggers via keywords in ref_number or forced payload
        if "TIMEOUT" in ref_clean or "UNAVAILABLE" in ref_clean:
            # Simulate network latency then failure
            await asyncio.sleep(0.05)
            return {
                "status": "source_unavailable",
                "doc_type": doc_type,
                "ref_number": ref_number,
                "issuer_name": "SIMULATED Authority Gateway",
                "certificate_data": None,
                "message": "SIMULATED: Issuing authority portal timed out or connection refused (503 Service Unavailable)",
                "is_simulated": True,
            }

        if "PENDING" in ref_clean:
            return {
                "status": "verification_pending",
                "doc_type": doc_type,
                "ref_number": ref_number,
                "issuer_name": "SIMULATED Authority Gateway",
                "certificate_data": None,
                "message": "SIMULATED: Verification request is queued at issuing body; batch reconciliation in progress",
                "is_simulated": True,
            }

        if "MANUAL" in ref_clean:
            return {
                "status": "manual_review_required",
                "doc_type": doc_type,
                "ref_number": ref_number,
                "issuer_name": "SIMULATED Authority Gateway",
                "certificate_data": None,
                "message": "SIMULATED: Authority flagged document for biometric/wet-ink physical cross-examination",
                "is_simulated": True,
            }

        record = self._registry.get(key)

        # If not found in registry -> manual_review_required or mismatch
        if not record:
            return {
                "status": "manual_review_required",
                "doc_type": doc_type,
                "ref_number": ref_number,
                "issuer_name": "SIMULATED Central Repository",
                "certificate_data": None,
                "message": f"SIMULATED: Reference number '{ref_number}' not found in registry of {doc_type}. Officer manual review recommended.",
                "is_simulated": True,
            }

        # Check for explicit forced status in stored payload
        forced_status = record.get("payload", {}).get("force_status")
        if forced_status in [
            "verified",
            "mismatch_detected",
            "expired",
            "verification_pending",
            "source_unavailable",
            "manual_review_required",
        ]:
            return {
                "status": forced_status,
                "doc_type": doc_type,
                "ref_number": ref_number,
                "issuer_name": record["issuing_authority"],
                "certificate_data": record,
                "message": f"SIMULATED: Pre-configured test status '{forced_status}' triggered",
                "is_simulated": True,
            }

        # 2. Check expiration
        expiry_str = record.get("expiry_date")
        if expiry_str:
            try:
                exp_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                if exp_date < date.today() or not record.get("is_valid", True):
                    return {
                        "status": "expired",
                        "doc_type": doc_type,
                        "ref_number": ref_number,
                        "issuer_name": record["issuing_authority"],
                        "certificate_data": record,
                        "message": f"SIMULATED: Certificate expired on {expiry_str}",
                        "is_simulated": True,
                    }
            except ValueError:
                pass

        # 3. Check for mismatches if submitted data is provided
        if submitted_payload:
            mismatches = []
            sub_inst = submitted_payload.get("institution_name")
            if sub_inst and record.get("institution_name"):
                if sub_inst.strip().lower() != record["institution_name"].strip().lower():
                    mismatches.append(
                        f"Institution name mismatch: Submitted '{sub_inst}' vs Registry '{record['institution_name']}'"
                    )

            sub_intake = submitted_payload.get("intake")
            reg_intake = record.get("payload", {}).get("approved_intake")
            if sub_intake and reg_intake and int(sub_intake) != int(reg_intake):
                mismatches.append(
                    f"Approved intake mismatch: Submitted {sub_intake} vs Registry {reg_intake}"
                )

            if mismatches:
                return {
                    "status": "mismatch_detected",
                    "doc_type": doc_type,
                    "ref_number": ref_number,
                    "issuer_name": record["issuing_authority"],
                    "certificate_data": record,
                    "discrepancies": mismatches,
                    "message": "SIMULATED: Discrepancy detected between submitted document and issuer ledger",
                    "is_simulated": True,
                }

        # 4. Verified successfully
        return {
            "status": "verified",
            "doc_type": doc_type,
            "ref_number": ref_number,
            "issuer_name": record["issuing_authority"],
            "certificate_data": record,
            "message": "SIMULATED: Certificate matched and confirmed authentic by issuing authority repository",
            "is_simulated": True,
        }


# Singleton instance
mock_issuer_service = MockIssuerService()
