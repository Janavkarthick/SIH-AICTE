"""Document Classification Service.

Categorizes uploaded regulatory documents into recognized AICTE artifact categories
using keyword frequency, layout features, title matching, and heuristics.
"""

import re
from typing import Dict, List, Optional, Tuple


class ClassifierService:
    """Rule, keyword, and layout-based document classifier for statutory AICTE filings."""

    def __init__(self):
        # Keyword patterns for each document type with relative weights
        self.type_keywords = {
            "affidavit": [
                (r"\baffidavit\b", 4.0),
                (r"\bnon[\s-]judicial\s+stamp\b", 3.0),
                (r"\bsolemnly\s+affirm\b", 3.0),
                (r"\bdeponent\b", 3.0),
                (r"\bnotary\s+public\b", 2.5),
                (r"\bsworn\s+before\s+me\b", 2.5),
            ],
            "fire_safety_certificate": [
                (r"\bfire\s+safety\b", 4.0),
                (r"\bfire\s+service\b", 3.5),
                (r"\bno\s+objection\s+certificate.*fire\b", 4.0),
                (r"\bfire\s+prevention\b", 3.0),
                (r"\bextinguisher\b", 2.0),
                (r"\bhose\s+reel\b", 2.0),
                (r"\bfire\s+officer\b", 2.5),
            ],
            "noc": [
                (r"\bno\s+objection\s+certificate\b", 4.0),
                (r"\bnoc\b", 2.5),
                (r"\bdepartment\s+of\s+higher\s+education\b", 3.0),
                (r"\bstate\s+government\b", 2.5),
                (r"\bgrant\s+of\s+noc\b", 3.5),
                (r"\bpermission\s+to\s+establish\b", 3.0),
            ],
            "accreditation_certificate": [
                (r"\baccreditation\b", 4.0),
                (r"\bnba\b", 3.0),
                (r"\bnaac\b", 3.0),
                (r"\bnational\s+board\s+of\s+accreditation\b", 4.5),
                (r"\bnational\s+assessment\s+and\s+accreditation\b", 4.5),
                (r"\bgrade\s+[A-C]\+*\b", 2.5),
                (r"\bvalid\s+up\s+to\b", 2.0),
            ],
            "land_document": [
                (r"\bsale\s+deed\b", 4.0),
                (r"\bland\s+document\b", 4.0),
                (r"\btitle\s+deed\b", 3.5),
                (r"\bsurvey\s+no\b", 3.0),
                (r"\bkhasra\b", 3.0),
                (r"\bpatta\b", 3.0),
                (r"\bregistration\s+department\b", 2.5),
                (r"\bacres\b", 2.0),
            ],
            "university_affiliation_letter": [
                (r"\baffiliation\b", 4.0),
                (r"\bprovisional\s+affiliation\b", 4.5),
                (r"\bcontinuation\s+of\s+affiliation\b", 4.5),
                (r"\bregistrar\b", 3.0),
                (r"\buniversity\b", 2.5),
                (r"\bacademic\s+council\b", 2.5),
                (r"\bsyndicate\b", 2.5),
            ],
            "faculty_list": [
                (r"\bfaculty\s+list\b", 4.5),
                (r"\bteaching\s+staff\b", 4.0),
                (r"\bassistant\s+professor\b", 3.5),
                (r"\bassociate\s+professor\b", 3.5),
                (r"\bprofessor\b", 2.5),
                (r"\bqualification\b", 2.0),
                (r"\bdate\s+of\s+joining\b", 2.5),
                (r"\bpan\s+number\b", 2.0),
            ],
            "electricity_bill": [
                (r"\belectricity\s+bill\b", 4.5),
                (r"\bpower\s+distribution\b", 3.5),
                (r"\bconsumer\s+number\b", 3.5),
                (r"\bkwh\b", 3.0),
                (r"\bmeter\s+reading\b", 3.0),
                (r"\btariff\b", 2.5),
                (r"\bbill\s+amount\b", 2.0),
            ],
            "infrastructure_photo": [
                (r"\bphotograph\b", 3.0),
                (r"\bcampus\s+view\b", 3.0),
                (r"\bfront\s+elevation\b", 3.0),
                (r"\blaboratory\s+photo\b", 3.0),
                (r"\bgeo[\s-]tagged\b", 3.5),
            ],
            "application_form": [
                (r"\bapplication\s+for\s+approval\b", 4.5),
                (r"\bapproval\s+process\b", 4.0),
                (r"\baicte\s+application\b", 4.5),
                (r"\bextension\s+of\s+approval\b", 3.5),
                (r"\bpermanent\s+id\b", 3.0),
                (r"\bcurrent\s+application\s+id\b", 3.5),
            ],
            "financial_statement": [
                (r"\baudited\s+financial\b", 4.5),
                (r"\bbalance\s+sheet\b", 4.5),
                (r"\bchartered\s+accountant\b", 4.0),
                (r"\bprofit\s+and\s+loss\b", 4.0),
                (r"\bincome\s+and\s+expenditure\b", 4.0),
                (r"\budin\b", 3.5),
                (r"\bassets\s+and\s+liabilities\b", 3.0),
            ],
        }

    def classify(
        self,
        text: str,
        filename: Optional[str] = None,
        declared_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Classify a document using text analysis and filename heuristics."""
        scores: Dict[str, float] = {doc_type: 0.0 for doc_type in self.type_keywords}
        lower_text = text.lower() if text else ""
        lower_filename = filename.lower() if filename else ""

        # 1. Filename heuristic boost
        for doc_type in self.type_keywords:
            clean_type = doc_type.replace("_", " ")
            if doc_type in lower_filename or clean_type in lower_filename:
                scores[doc_type] += 3.0

        # 2. Text keyword matching
        for doc_type, patterns in self.type_keywords.items():
            for pattern, weight in patterns:
                matches = len(re.findall(pattern, lower_text))
                if matches > 0:
                    scores[doc_type] += min(matches, 4) * weight

        # 3. Photo heuristic: if text is empty/minimal and filename indicates photo or image
        if len(lower_text.strip()) < 40 and lower_filename.endswith(
            (".jpg", ".jpeg", ".png", ".webp")
        ):
            scores["infrastructure_photo"] += 6.0

        # Find maximum scoring class
        best_type, max_score = max(scores.items(), key=lambda item: item[1])

        # If declared_type was specified and score is very low, give bias or verify consistency
        if max_score < 2.0:
            if declared_type and declared_type in self.type_keywords:
                predicted_type = declared_type
                confidence = 0.50
            else:
                predicted_type = best_type if max_score > 0 else (declared_type or "application_form")
                confidence = 0.40
        else:
            predicted_type = best_type
            # Normalize confidence between 0.60 and 0.99
            confidence = min(0.99, 0.60 + (max_score / 30.0) * 0.39)

        return {
            "predicted_type": predicted_type,
            "confidence": round(confidence, 2),
            "method": "rule_keyword_layout",
            "scores": {k: round(v, 2) for k, v in scores.items() if v > 0},
        }


# Singleton instance
classifier_service = ClassifierService()
