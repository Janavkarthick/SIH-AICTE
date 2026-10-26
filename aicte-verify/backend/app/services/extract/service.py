"""Entity and Field Extraction Service.

Extracts structured regulatory fields from unstructured document text and images
using regex, keyword-anchored window extraction, and OpenCV QR code detection.
"""

import json
import re
from typing import Any, Dict, List, Optional
import cv2
import numpy as np


class ExtractionService:
    """Extracts key statutory fields (institution name, ID, certificate numbers, dates, intake, area)."""

    def __init__(self):
        # Regular expressions for common statutory fields
        self.date_regexes = [
            r"\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b",  # 2024-05-15 or 2024/05/15
            r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b",  # 15-05-2024 or 15/05/2024
            r"\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+\d{4})\b",
        ]
        self.aicte_id_regex = r"\b(?:AICTE\s*ID|PID|Permanent\s*ID|Institution\s*ID)[\s:.-]*([1-9]-\d{6,11}|\d{6,12})\b"
        self.ref_num_regex = r"\b(?:Ref(?:\.|erence)?\s*(?:No|Num)?|Certificate\s*(?:No|Num)|Registration\s*(?:No|Num)|NOC\s*No)[\s:.-]*([A-Z0-9/\-_]{4,35})\b"
        self.intake_regex = r"\b(?:Intake|Approved\s*Intake|Capacity|Total\s*Intake|Sanctioned\s*Intake)[\s:.-]*(\d{2,4})\b"
        self.area_regex = r"\b(?:Built[- ]up\s*Area|Total\s*Area|Carpet\s*Area|Land\s*Area)[\s:.-]*([\d,]+(?:\.\d+)?)\s*(?:sq\.?\s*(?:ft|m(?:tr)?|feet)|acres|hectares)?\b"
        self.survey_regex = r"\b(?:Survey\s*No|Khasra\s*No|Gat\s*No|Patta\s*No)[\s:.-]*([A-Z0-9/\-_]+)\b"
        self.pan_regex = r"\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b"

    def detect_qr_code(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Detect and decode QR code from an image or rendered PDF page using OpenCV."""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None

            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)
            if data and bbox is not None:
                # bbox is float coordinates of 4 corners
                x_coords = [p[0] for p in bbox[0]]
                y_coords = [p[1] for p in bbox[0]]
                min_x, max_x = min(x_coords), max(x_coords)
                min_y, max_y = min(y_coords), max(y_coords)
                return {
                    "data": data,
                    "bbox": [float(min_x), float(min_y), float(max_x - min_x), float(max_y - min_y)],
                    "method": "qr",
                }
        except Exception:
            pass
        return None

    def _normalize_date(self, date_str: str) -> str:
        """Clean and convert extracted date strings into standard YYYY-MM-DD if possible."""
        clean = re.sub(r"[^\w\s\-/]", "", date_str).strip()
        # If DD/MM/YYYY or DD-MM-YYYY
        match_dmy = re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$", clean)
        if match_dmy:
            day, month, year = match_dmy.groups()
            return f"{year}-{int(month):02d}-{int(day):02d}"
        return clean

    def extract_fields(
        self,
        text: str,
        blocks: Optional[List[Dict[str, Any]]] = None,
        image_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Extract all known fields from document text, bounding blocks, and optional QR code."""
        results: List[Dict[str, Any]] = []
        found_fields: Dict[str, bool] = {}

        # 1. QR Code extraction if image provided
        if image_path:
            qr_info = self.detect_qr_code(image_path)
            if qr_info:
                qr_content = qr_info["data"]
                results.append({
                    "field_name": "qr_code_payload",
                    "field_value": qr_content,
                    "confidence": 0.99,
                    "page_number": 1,
                    "bbox_json": json.dumps(qr_info["bbox"]),
                    "method": "qr",
                    "language": "eng",
                })
                # Check if QR contains JSON with structured certificate info
                try:
                    parsed = json.loads(qr_content)
                    if isinstance(parsed, dict):
                        for k, v in parsed.items():
                            results.append({
                                "field_name": f"qr_{k}",
                                "field_value": str(v),
                                "confidence": 0.99,
                                "page_number": 1,
                                "bbox_json": json.dumps(qr_info["bbox"]),
                                "method": "qr",
                                "language": "eng",
                            })
                except Exception:
                    pass

        # 2. Institution Name extraction (Anchored search)
        name_patterns = [
            r"(?:Name\s*of\s*(?:the)?\s*Institution|Institution\s*Name|College\s*Name)[\s:.-]*([A-Z0-9\s.,&'\-]{6,80})",
            r"(?:This\s*is\s*to\s*certify\s*that)\s+([A-Z\s.,&'\-]{6,80})",
            r"\b([A-Z][A-Za-z\s&]{4,60}\s+(?:Institute|College|University|Academy|Polytechnic))",
        ]
        for pattern in name_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m and "institution_name" not in found_fields:
                val = m.group(1).strip().split("\n")[0].strip()
                if len(val) > 4 and not val.lower().startswith("ai"):
                    results.append({
                        "field_name": "institution_name",
                        "field_value": val,
                        "confidence": 0.90,
                        "page_number": 1,
                        "bbox_json": None,
                        "method": "keyword_anchor",
                        "language": "eng",
                    })
                    found_fields["institution_name"] = True
                    break

        # 3. AICTE Permanent ID / Institution ID
        m_id = re.search(self.aicte_id_regex, text, re.IGNORECASE)
        if m_id:
            results.append({
                "field_name": "institution_id",
                "field_value": m_id.group(1).strip(),
                "confidence": 0.95,
                "page_number": 1,
                "bbox_json": None,
                "method": "regex",
                "language": "eng",
            })
            found_fields["institution_id"] = True

        # 4. Certificate / Reference Number
        m_ref = re.search(self.ref_num_regex, text, re.IGNORECASE)
        if m_ref:
            val = m_ref.group(1).strip()
            if len(val) >= 4 and not val.lower().startswith("aicte"):
                results.append({
                    "field_name": "certificate_number",
                    "field_value": val,
                    "confidence": 0.92,
                    "page_number": 1,
                    "bbox_json": None,
                    "method": "regex",
                    "language": "eng",
                })
                found_fields["certificate_number"] = True

        # 5. Dates: Issue Date and Expiry Date
        # Look for "Issue Date" or "Dated"
        issue_anchor = r"(?:Issue\s*Date|Date\s*of\s*Issue|Dated|Date)[\s:.-]*"
        for d_pat in self.date_regexes:
            m_issue = re.search(issue_anchor + d_pat, text, re.IGNORECASE)
            if m_issue and "issue_date" not in found_fields:
                raw_date = m_issue.group(1).strip()
                results.append({
                    "field_name": "issue_date",
                    "field_value": self._normalize_date(raw_date),
                    "confidence": 0.90,
                    "page_number": 1,
                    "bbox_json": None,
                    "method": "keyword_anchor",
                    "language": "eng",
                })
                found_fields["issue_date"] = True
                break

        # Look for "Valid Up to", "Expiry Date", "Validity"
        expiry_anchor = r"(?:Valid\s*(?:Up\s*to|until|thru)|Expiry\s*Date|Validity)[\s:.-]*"
        for d_pat in self.date_regexes:
            m_exp = re.search(expiry_anchor + d_pat, text, re.IGNORECASE)
            if m_exp and "expiry_date" not in found_fields:
                raw_date = m_exp.group(1).strip()
                results.append({
                    "field_name": "expiry_date",
                    "field_value": self._normalize_date(raw_date),
                    "confidence": 0.88,
                    "page_number": 1,
                    "bbox_json": None,
                    "method": "keyword_anchor",
                    "language": "eng",
                })
                found_fields["expiry_date"] = True
                break

        # 6. Approved Intake
        m_intake = re.search(self.intake_regex, text, re.IGNORECASE)
        if m_intake:
            results.append({
                "field_name": "intake",
                "field_value": m_intake.group(1).strip(),
                "confidence": 0.89,
                "page_number": 1,
                "bbox_json": None,
                "method": "regex",
                "language": "eng",
            })
            found_fields["intake"] = True

        # 7. Built-up Area
        m_area = re.search(self.area_regex, text, re.IGNORECASE)
        if m_area:
            val = m_area.group(1).replace(",", "").strip()
            results.append({
                "field_name": "area_sqft",
                "field_value": val,
                "confidence": 0.87,
                "page_number": 1,
                "bbox_json": None,
                "method": "regex",
                "language": "eng",
            })
            found_fields["area_sqft"] = True

        # 8. Survey Number
        m_surv = re.search(self.survey_regex, text, re.IGNORECASE)
        if m_surv:
            results.append({
                "field_name": "survey_number",
                "field_value": m_surv.group(1).strip(),
                "confidence": 0.86,
                "page_number": 1,
                "bbox_json": None,
                "method": "regex",
                "language": "eng",
            })
            found_fields["survey_number"] = True

        # 9. Faculty PANs / IDs
        pans = re.findall(self.pan_regex, text)
        if pans:
            unique_pans = sorted(list(set(pans)))[:10]  # top 10 unique
            results.append({
                "field_name": "faculty_ids",
                "field_value": ", ".join(unique_pans),
                "confidence": 0.94,
                "page_number": 1,
                "bbox_json": None,
                "method": "regex_pan",
                "language": "eng",
            })

        # 10. Issuing Authority
        auth_patterns = [
            r"(?:Issued\s*by|Issuing\s*Authority|Signature\s*of)[\s:.-]*([A-Za-z0-9\s.,\-]{5,60})",
            r"\b((?:Fire\s*and\s*Rescue\s*Services|Department\s*of\s*Higher\s*Education|State\s*Pollution\s*Control\s*Board|National\s*Board\s*of\s*Accreditation|Registrar))",
        ]
        for pat in auth_patterns:
            m_auth = re.search(pat, text, re.IGNORECASE)
            if m_auth and "issuing_authority" not in found_fields:
                results.append({
                    "field_name": "issuing_authority",
                    "field_value": m_auth.group(1).strip().split("\n")[0].strip(),
                    "confidence": 0.85,
                    "page_number": 1,
                    "bbox_json": None,
                    "method": "keyword_anchor",
                    "language": "eng",
                })
                found_fields["issuing_authority"] = True
                break

        # Attach bounding box if matching text is located in blocks
        if blocks:
            for item in results:
                target_val = str(item.get("field_value", "")).lower()
                for b in blocks:
                    block_txt = b.get("text", "").lower()
                    if target_val and (target_val in block_txt or block_txt in target_val):
                        item["bbox_json"] = json.dumps(b.get("bbox"))
                        item["page_number"] = b.get("page", 1)
                        break

        return results


# Singleton instance
extraction_service = ExtractionService()
