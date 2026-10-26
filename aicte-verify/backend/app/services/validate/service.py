"""Regulatory Checklist and Cross-Document Validation Service.

Validates application packages against checklists.json, doc_validity.json,
and cross-document consistency rules.
All thresholds are marked: illustrative: replace with Approval Process Handbook values.
"""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.application import Application
from app.models.document import Document, ExtractedData
from app.models.flag import Flag
from app.schemas.application import FlagItem, RiskBreakdown, RiskContribution, ValidationReport
from app.services.risk.service import risk_service


class ValidationService:
    """Validates document completeness, cross-document field consistency, and statutory expiration."""

    def __init__(self):
        self._checklists: Optional[Dict[str, Any]] = None
        self._doc_validity: Optional[Dict[str, Any]] = None

    def _load_config_rules(self):
        """Load rules and checklists lazily."""
        if self._checklists is None:
            c_path = settings.resolve_rules_path("checklists.json")
            if c_path.exists():
                with open(c_path, "r", encoding="utf-8") as f:
                    self._checklists = json.load(f)
            else:
                self._checklists = {}

        if self._doc_validity is None:
            v_path = settings.resolve_rules_path("doc_validity.json")
            if v_path.exists():
                with open(v_path, "r", encoding="utf-8") as f:
                    self._doc_validity = json.load(f)
            else:
                self._doc_validity = {}

    def _parse_date(self, d_str: Optional[str]) -> Optional[date]:
        """Attempt parsing common date strings."""
        if not d_str:
            return None
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(d_str.strip(), fmt).date()
            except ValueError:
                continue
        return None

    async def validate_application(
        self,
        db: AsyncSession,
        application_id: int,
        persist_flags: bool = True,
    ) -> ValidationReport:
        """Run complete automated checklist and cross-document validation for an application."""
        self._load_config_rules()

        # 1. Fetch application with institution and current documents
        stmt = (
            select(Application)
            .where(Application.id == application_id)
        )
        res = await db.execute(stmt)
        application = res.scalar_one_or_none()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # Fetch current documents
        doc_stmt = (
            select(Document)
            .where(Document.application_id == application_id, Document.is_current == True)
        )
        doc_res = await db.execute(doc_stmt)
        documents: List[Document] = list(doc_res.scalars().all())

        # Fetch extracted data for all documents
        doc_ids = [d.id for d in documents]
        extracted_map: Dict[int, Dict[str, str]] = {d.id: {} for d in documents}
        if doc_ids:
            ext_stmt = select(ExtractedData).where(ExtractedData.document_id.in_(doc_ids))
            ext_res = await db.execute(ext_stmt)
            for item in ext_res.scalars().all():
                if item.field_value:
                    extracted_map[item.document_id][item.field_name] = item.field_value

        category = application.category
        checklist_cfg = self._checklists.get(category, {})
        required_docs = checklist_cfg.get("required_documents", [])
        validity_rules = self._doc_validity.get("validity_periods", {})

        uploaded_types = {d.document_type: d for d in documents}
        missing_docs: List[str] = []
        expired_docs: List[str] = []
        cross_check_mismatches: List[str] = []
        new_flags: List[Flag] = []
        today = date.today()

        # A. Check missing mandatory documents
        for req in required_docs:
            dtype = req.get("type")
            is_mand = req.get("mandatory", False)
            label = req.get("label", dtype)
            if is_mand and dtype not in uploaded_types:
                missing_docs.append(f"{label} ({dtype})")
                new_flags.append(
                    Flag(
                        application_id=application.id,
                        document_id=None,
                        flag_type="validation",
                        severity="high",
                        code="VAL-MISSING-DOC",
                        title=f"Mandatory Document Missing: {label}",
                        reason=f"The required mandatory document '{label}' was not uploaded for category '{category}'.",
                        evidence_json=json.dumps({"document_type": dtype, "category": category}),
                        rule_id=f"CHK-{dtype.upper()}",
                        check_name="Mandatory Document Checklist",
                    )
                )

        # B. Check validity and date logic on uploaded documents
        for doc in documents:
            dtype = doc.document_type
            extracted = extracted_map.get(doc.id, {})
            issue_date = self._parse_date(extracted.get("issue_date"))
            expiry_date = self._parse_date(extracted.get("expiry_date"))

            # 1. Check if future dated
            if issue_date and issue_date > today:
                new_flags.append(
                    Flag(
                        application_id=application.id,
                        document_id=doc.id,
                        flag_type="validation",
                        severity="high",
                        code="VAL-DATE-FUTURE",
                        title="Document Issue Date in Future",
                        reason=f"Document issue date {issue_date} is set in the future.",
                        evidence_json=json.dumps({"issue_date": str(issue_date), "today": str(today)}),
                        rule_id="DATE-FUTURE-CHECK",
                        check_name="Chronological Sanity Check",
                    )
                )

            # 2. Check if inverted dates (issue >= expiry)
            if issue_date and expiry_date and issue_date >= expiry_date:
                new_flags.append(
                    Flag(
                        application_id=application.id,
                        document_id=doc.id,
                        flag_type="validation",
                        severity="critical",
                        code="VAL-DATE-INVERTED",
                        title="Inverted Validity Dates",
                        reason=f"Issue date ({issue_date}) is after or equal to expiry date ({expiry_date}).",
                        evidence_json=json.dumps({"issue_date": str(issue_date), "expiry_date": str(expiry_date)}),
                        rule_id="DATE-INVERSION-CHECK",
                        check_name="Chronological Sanity Check",
                    )
                )

            # 3. Check expiration
            if expiry_date and expiry_date < today:
                expired_docs.append(f"{doc.document_type} (Expired on {expiry_date})")
                new_flags.append(
                    Flag(
                        application_id=application.id,
                        document_id=doc.id,
                        flag_type="validation",
                        severity="high",
                        code="VAL-DOC-EXPIRED",
                        title="Statutory Document Expired",
                        reason=f"The document expired on {expiry_date} prior to current academic verification.",
                        evidence_json=json.dumps({"expiry_date": str(expiry_date), "today": str(today)}),
                        rule_id="DOC-EXPIRY-CHECK",
                        check_name="Validity Window Check",
                    )
                )

        # C. Cross-document consistency checks
        cross_checks = checklist_cfg.get("cross_checks", [])
        for check in cross_checks:
            field_name = check.get("field")
            across_types = check.get("across", [])
            rule = check.get("rule")

            if rule == "must_match" and field_name and len(across_types) >= 2:
                # Gather values from available documents
                values_found: Dict[str, str] = {}
                for doc_type in across_types:
                    doc = uploaded_types.get(doc_type)
                    if doc and doc.id in extracted_map:
                        val = extracted_map[doc.id].get(field_name)
                        if val:
                            values_found[doc_type] = val.strip().lower()

                # If 2 or more values exist, check matching
                if len(values_found) >= 2:
                    unique_vals = set(values_found.values())
                    if len(unique_vals) > 1:
                        mismatch_desc = f"{field_name} differs across: {values_found}"
                        cross_check_mismatches.append(mismatch_desc)
                        new_flags.append(
                            Flag(
                                application_id=application.id,
                                document_id=None,
                                flag_type="validation",
                                severity="high" if field_name != "intake" else "medium",
                                code=f"VAL-CROSS-{field_name.upper()}",
                                title=f"Cross-Document Mismatch: {field_name}",
                                reason=f"Inconsistent field values detected across regulatory filings: {values_found}",
                                evidence_json=json.dumps(values_found),
                                rule_id=f"CROSS-{field_name.upper()}",
                                check_name="Cross-Document Consistency Engine",
                            )
                        )

        # Persist flags to database if requested
        if persist_flags:
            for flag in new_flags:
                db.add(flag)
            await db.commit()

        # Compute risk score using RiskService
        risk_breakdown = risk_service.compute_risk(new_flags)

        # Update application risk score and level
        application.risk_score = risk_breakdown.risk_score
        application.risk_level = risk_breakdown.risk_level
        application.risk_breakdown = json.dumps(risk_breakdown.model_dump())
        await db.commit()
        await db.refresh(application)

        flag_items = [
            FlagItem(
                code=f.code,
                title=f.title,
                severity=f.severity,
                reason=f.reason,
                rule_id=f.rule_id,
                document_id=f.document_id,
            )
            for f in new_flags
        ]

        is_valid = len(new_flags) == 0

        summary = (
            f"Validation complete for application {application_id} ({category}). "
            f"{len(new_flags)} discrepancies flagged. "
            f"Risk Level: {risk_breakdown.risk_level} ({risk_breakdown.risk_score}/100)."
        )

        return ValidationReport(
            application_id=application_id,
            application_category=category,
            is_valid=is_valid,
            summary=summary,
            missing_documents=missing_docs,
            expired_documents=expired_docs,
            cross_check_mismatches=cross_check_mismatches,
            flags=flag_items,
            risk=risk_breakdown,
        )


# Singleton instance
validation_service = ValidationService()
