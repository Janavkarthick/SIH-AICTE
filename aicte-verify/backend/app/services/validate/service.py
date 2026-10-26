"""Regulatory Checklist and Cross-Document Validation Service.

Validates application packages against checklists.json, doc_validity.json,
and cross-document consistency rules.
All thresholds are marked: illustrative: replace with Approval Process Handbook values.
"""

import difflib
import json
import re
from datetime import date, datetime, timedelta
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


def collapse_initials(text: str) -> str:
    """Collapse spaced single letters representing initials (e.g., 'b r' -> 'br', 'p s g' -> 'psg')."""
    prev = ""
    while prev != text:
        prev = text
        text = re.sub(r"\b([a-z])\s+([a-z])\b", r"\1\2", text)
    return text


def normalize_institution_name(name: str) -> str:
    """Normalize institutional names for resilient fuzzy equivalence comparison."""
    if not name:
        return ""
    text = name.lower().strip()
    text = text.replace("&", " and ")
    text = text.replace("'s", "")
    text = text.replace("’s", "")
    text = re.sub(r"[,\.\-\/\\_\(\)]", " ", text)
    abbreviations = {
        r"\bst\b": "saint",
        r"\bengg\b": "engineering",
        r"\btech\b": "technology",
        r"\binst\b": "institute",
        r"\bcoll\b": "college",
        r"\bpoly\b": "polytechnic",
        r"\bgovt\b": "government",
        r"\buniv\b": "university",
        r"\bacad\b": "academy",
        r"\bmgmt\b": "management",
    }
    for pattern, repl in abbreviations.items():
        text = re.sub(pattern, repl, text)
    text = collapse_initials(text)
    return re.sub(r"\s+", " ", text).strip()


GENERIC_INSTITUTIONAL_AFFIXES = {
    "campus", "deemed", "univ", "university", "college", "institute",
    "technology", "engineering", "academy", "polytechnic", "science",
    "sciences", "center", "centre", "main", "branch", "school", "department",
    "of", "the", "and", "in", "at", "for"
}


def has_trailing_specifier_conflict(t1: List[str], t2: List[str]) -> bool:
    """Detect conflicting branch or location suffixes when shared institutional stems exist."""
    tail1 = None
    for x in reversed(t1):
        if x not in GENERIC_INSTITUTIONAL_AFFIXES:
            tail1 = x
            break
    tail2 = None
    for x in reversed(t2):
        if x not in GENERIC_INSTITUTIONAL_AFFIXES:
            tail2 = x
            break
    if tail1 and tail2 and tail1 != tail2:
        common_words = (set(t1) & set(t2)) - GENERIC_INSTITUTIONAL_AFFIXES
        if len(common_words) >= 1 or len(set(t1) & set(t2)) >= 2:
            return True
    return False


def match_acronym_subsequence(t1: List[str], t2: List[str]) -> bool:
    """Match acronym tokens against consecutive subphrases (e.g. 'nit' -> 'national institute technology')."""
    def check_sub(acro_tokens: List[str], full_tokens: List[str]) -> bool:
        for i, tok in enumerate(acro_tokens):
            if 2 <= len(tok) <= 6:
                for start in range(len(full_tokens)):
                    for end in range(start + len(tok), min(start + len(tok) + 1, len(full_tokens) + 1)):
                        sub_initials = "".join(x[0] for x in full_tokens[start:end])
                        if tok == sub_initials:
                            rem_full = [x for x in (full_tokens[:start] + full_tokens[end:]) if x not in GENERIC_INSTITUTIONAL_AFFIXES]
                            rem_acro = [x for x in (acro_tokens[:i] + acro_tokens[i + 1:]) if x not in GENERIC_INSTITUTIONAL_AFFIXES]
                            if rem_full and rem_acro and rem_full != rem_acro:
                                return False
                            if not rem_acro or not rem_full or rem_acro == rem_full or set(rem_acro).issubset(set(rem_full)) or set(rem_full).issubset(set(rem_acro)):
                                return True
        return False
    return check_sub(t1, t2) or check_sub(t2, t1)


def normalize_survey_number(survey: str) -> str:
    """Normalize land survey / khasra numbers (e.g., 'Survey No. 12/3-A' -> '12/3a')."""
    if not survey:
        return ""
    text = survey.lower().strip()
    text = re.sub(r"\b(survey|sy|s|khasra|plot|rs)\s*(no|number)?[\.:\s]*", "", text)
    text = re.sub(r"-\s*([a-zA-Z])", r"\1", text)
    text = re.sub(r"\s*[\/]\s*", "/", text)
    return re.sub(r"[\s\-_]+", "", text).strip()


def are_field_values_equivalent(field_name: str, val1: str, val2: str) -> bool:
    """Determine if two regulatory field extractions are semantically equivalent."""
    if not val1 or not val2:
        return False
    v1_raw = val1.strip().lower()
    v2_raw = val2.strip().lower()
    if v1_raw == v2_raw:
        return True

    if any(k in field_name.lower() for k in ["institution", "trust", "college", "applicant"]):
        n1 = normalize_institution_name(val1)
        n2 = normalize_institution_name(val2)
        if n1 == n2:
            return True

        # Mutually exclusive institutional types cannot match
        incompatible_pairs = [
            ("polytechnic", "engineering"),
            ("global academy", "institute"),
            ("polytechnic", "institute"),
            ("university", "polytechnic"),
        ]
        for type_a, type_b in incompatible_pairs:
            if (type_a in n1 and type_b in n2) or (type_b in n1 and type_a in n2):
                return False

        # Filter stopwords for token matching
        stopwords = {"of", "the", "and", "in", "at", "for", "deemed", "campus"}
        t1 = [w for w in n1.split() if w not in stopwords]
        t2 = [w for w in n2.split() if w not in stopwords]
        s1, s2 = set(t1), set(t2)
        if s1 == s2:
            return True

        # Structural conflict check for distinctive trailing branch/location specifiers
        if has_trailing_specifier_conflict(t1, t2):
            return False

        # Acronym subphrase matching (e.g. 'nit' <-> 'national institute technology')
        if match_acronym_subsequence(t1, t2):
            return True

        # Jaccard similarity on core tokens
        if s1 and s2:
            jaccard = len(s1.intersection(s2)) / len(s1.union(s2))
            if jaccard >= 0.75:
                return True

        ratio = difflib.SequenceMatcher(None, n1, n2).ratio()
        if ratio >= 0.90:
            return True

        return False

    if any(k in field_name.lower() for k in ["survey", "khasra", "plot", "land"]):
        s1 = normalize_survey_number(val1)
        s2 = normalize_survey_number(val2)
        if s1 == s2:
            return True
        # Handle subdivision e.g. 12/3 vs 12/3a
        if s1.startswith(s2) or s2.startswith(s1):
            return True

    if any(k in field_name.lower() for k in ["area", "acres", "intake"]):
        try:
            num1 = float(re.findall(r"[\d\.]+", val1)[0])
            num2 = float(re.findall(r"[\d\.]+", val2)[0])
            if abs(num1 - num2) < 0.1:
                return True
        except (IndexError, ValueError):
            pass

    return False


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
        # Rule #2: Use explicit application.submission_date field, NEVER created_at or DB insert time
        submission_date = getattr(application, "submission_date", None)
        if not submission_date:
            submission_date = date.today()

        validity_cfg = self._doc_validity or {}
        grace_period_days = validity_cfg.get("grace_period_days", 30)

        for doc in documents:
            dtype = doc.document_type
            extracted = extracted_map.get(doc.id, {})
            issue_date = self._parse_date(extracted.get("issue_date"))
            expiry_date = self._parse_date(extracted.get("expiry_date"))

            # 1. Check if future dated relative to submission
            if issue_date and issue_date > submission_date:
                new_flags.append(
                    Flag(
                        application_id=application.id,
                        document_id=doc.id,
                        flag_type="validation",
                        severity="high",
                        code="VAL-DATE-FUTURE",
                        title="Document Issue Date in Future",
                        reason=f"Document issue date {issue_date} is set in the future relative to submission date {submission_date}.",
                        evidence_json=json.dumps({"issue_date": str(issue_date), "submission_date": str(submission_date)}),
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

            # 3. Check expiration against submission date with grace period
            if expiry_date:
                if expiry_date < submission_date:
                    days_past = (submission_date - expiry_date).days
                    if days_past <= grace_period_days:
                        new_flags.append(
                            Flag(
                                application_id=application.id,
                                document_id=doc.id,
                                flag_type="validation",
                                severity="medium",
                                code="VAL-DOC-GRACE-PERIOD",
                                title=f"Statutory Document Renewal in Progress ({grace_period_days}-Day Grace Period)",
                                reason=f"Document expired on {expiry_date} ({days_past} days prior to application submission date {submission_date}). Falls within illustrative {grace_period_days}-day grace window (configurable); requires proof of renewal application.",
                                evidence_json=json.dumps({"expiry_date": str(expiry_date), "submission_date": str(submission_date), "days_past": days_past, "grace_period_days": grace_period_days}),
                                rule_id="DOC-GRACE-CHECK",
                                check_name="Validity Window Grace Check",
                            )
                        )
                    else:
                        expired_docs.append(f"{doc.document_type} (Expired on {expiry_date})")
                        new_flags.append(
                            Flag(
                                application_id=application.id,
                                document_id=doc.id,
                                flag_type="validation",
                                severity="high",
                                code="VAL-DOC-EXPIRED",
                                title="Statutory Document Expired Prior to Submission",
                                reason=f"The document expired on {expiry_date} prior to application submission date {submission_date} (exceeds illustrative {grace_period_days}-day grace window; configurable).",
                                evidence_json=json.dumps({"expiry_date": str(expiry_date), "submission_date": str(submission_date), "grace_period_days": grace_period_days}),
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
                            values_found[doc_type] = val.strip()

                # If 2 or more values exist, check matching using fuzzy and semantic normalizers
                if len(values_found) >= 2:
                    val_items = list(values_found.items())
                    has_genuine_mismatch = False
                    for i in range(len(val_items)):
                        for j in range(i + 1, len(val_items)):
                            d1, v1 = val_items[i]
                            d2, v2 = val_items[j]
                            if not are_field_values_equivalent(field_name, v1, v2):
                                has_genuine_mismatch = True
                                break
                        if has_genuine_mismatch:
                            break

                    if has_genuine_mismatch:
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
