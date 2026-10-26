"""Risk Scoring Engine.

Calculates normalized composite risk index (0-100) based on weighted flag severities.
All weights and risk thresholds are marked: illustrative: replace with Approval Process Handbook values.
"""

from typing import List, Union
from app.models.flag import Flag
from app.schemas.application import FlagItem, RiskBreakdown, RiskContribution


class RiskService:
    """Calculates risk levels and explainable score breakdowns for AICTE regulatory applications."""

    # Flag severity weights (illustrative: replace with Approval Process Handbook values)
    WEIGHTS = {
        "critical": 10.0,
        "high": 6.0,
        "medium": 3.0,
        "low": 1.5,
        "info": 0.5,
    }

    # Threshold intervals (illustrative: replace with Approval Process Handbook values)
    THRESHOLD_LOW_MAX = 28.0
    THRESHOLD_MEDIUM_MAX = 60.0

    # Per-category maximum contribution caps to prevent score saturation
    CATEGORY_CAPS = {
        "missing_docs": 18.0,
        "validation": 25.0,
        "compliance": 25.0,
        "forensics": 30.0,
        "anomaly": 30.0,
        "verification": 25.0,
        "other": 15.0,
    }

    def _determine_category(self, code: str, flag_type: str) -> str:
        c = (code or "").lower()
        ft = (flag_type or "").lower()
        if "missing" in c or "missing" in ft:
            return "missing_docs"
        if ft == "anomaly" or "ano-" in c or "collusion" in c or "ghost" in c:
            return "anomaly"
        if ft == "forensics" or "for-" in c or "ela" in c or "font" in c:
            return "forensics"
        if ft == "compliance" or "com-" in c or "quota" in c or "ratio" in c:
            return "compliance"
        if ft == "verification" or "ver-" in c:
            return "verification"
        if ft == "validation" or "val-" in c:
            return "validation"
        return "other"

    def compute_risk(self, flags: List[Union[Flag, FlagItem]]) -> RiskBreakdown:
        """Calculate weighted score, categorical risk level, and itemized contributions."""
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        info_count = 0
        contributions: List[RiskContribution] = []

        category_points: dict[str, float] = {k: 0.0 for k in self.CATEGORY_CAPS}

        for f in flags:
            # Check if flag is resolved (if Flag model instance)
            if hasattr(f, "is_resolved") and f.is_resolved:
                continue

            sev = (getattr(f, "severity", "") or "medium").lower()
            weight = self.WEIGHTS.get(sev, 1.5)

            if sev == "critical":
                critical_count += 1
            elif sev == "high":
                high_count += 1
            elif sev == "medium":
                medium_count += 1
            elif sev == "low":
                low_count += 1
            else:
                info_count += 1

            code = getattr(f, "code", "FLAG") or "FLAG"
            title = getattr(f, "title", "Discrepancy") or "Discrepancy"
            flag_type = getattr(f, "flag_type", "validation") or "validation"

            cat = self._determine_category(code, flag_type)
            category_points[cat] = category_points.get(cat, 0.0) + weight

            contributions.append(
                RiskContribution(
                    flag_code=code,
                    title=title,
                    severity=sev,
                    weight=weight,
                    contribution_score=weight,
                )
            )

        # Apply per-category caps
        capped_total = 0.0
        for cat, pts in category_points.items():
            cap = self.CATEGORY_CAPS.get(cat, 20.0)
            capped_total += min(pts, cap)

        # Scale capped points into a 0 - 100 risk score
        # Normal regulatory baseline maps 55 balanced weighted points to high risk (100)
        # (illustrative: replace with Approval Process Handbook values)
        raw_score = (capped_total / 55.0) * 100.0
        normalized_score = min(100.0, round(raw_score, 1))

        # Categorize risk level
        if normalized_score <= self.THRESHOLD_LOW_MAX:
            risk_level = "Low"
        elif normalized_score <= self.THRESHOLD_MEDIUM_MAX:
            risk_level = "Medium"
        else:
            risk_level = "High"

        # Auto-escalate to High if critical flags exist, with progressive scaling above 65
        if critical_count > 0:
            risk_level = "High"
            base_critical = 65.0 + min(25.0, (critical_count - 1) * 10.0 + (high_count * 2.5))
            normalized_score = min(100.0, round(max(normalized_score, base_critical), 1))

        return RiskBreakdown(
            risk_score=normalized_score,
            risk_level=risk_level,
            total_flags=len(contributions),
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            info_count=info_count,
            contributions=contributions,
            threshold_note="illustrative: replace with Approval Process Handbook values",
        )


# Singleton instance
risk_service = RiskService()
