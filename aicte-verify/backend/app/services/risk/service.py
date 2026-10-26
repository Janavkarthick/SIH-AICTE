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
        "high": 7.0,
        "medium": 4.0,
        "low": 2.0,
        "info": 1.0,
    }

    # Threshold intervals (illustrative: replace with Approval Process Handbook values)
    THRESHOLD_LOW_MAX = 30.0
    THRESHOLD_MEDIUM_MAX = 60.0

    def compute_risk(self, flags: List[Union[Flag, FlagItem]]) -> RiskBreakdown:
        """Calculate weighted score, categorical risk level, and itemized contributions."""
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        info_count = 0
        contributions: List[RiskContribution] = []

        total_weighted_points = 0.0

        for f in flags:
            # Check if flag is resolved (if Flag model instance)
            if hasattr(f, "is_resolved") and f.is_resolved:
                continue

            sev = f.severity.lower()
            weight = self.WEIGHTS.get(sev, 1.0)
            total_weighted_points += weight

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

            code = getattr(f, "code", "FLAG")
            title = getattr(f, "title", "Discrepancy")
            contributions.append(
                RiskContribution(
                    flag_code=code,
                    title=title,
                    severity=sev,
                    weight=weight,
                    contribution_score=weight,
                )
            )

        # Scale raw points into a 0 - 100 risk score
        # e.g., 2 critical flags (20 pts) + 1 high (7 pts) = 27 pts
        # A normal regulatory scale maps ~35 weighted points to max risk 100
        # (illustrative: replace with Approval Process Handbook values)
        normalized_score = min(100.0, round((total_weighted_points / 35.0) * 100.0, 1))

        # Categorize risk level
        if normalized_score <= self.THRESHOLD_LOW_MAX:
            risk_level = "Low"
        elif normalized_score <= self.THRESHOLD_MEDIUM_MAX:
            risk_level = "Medium"
        else:
            risk_level = "High"

        # Auto-escalate to High if critical flags exist
        if critical_count > 0 and risk_level != "High":
            risk_level = "High"
            normalized_score = max(normalized_score, 65.0)

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
