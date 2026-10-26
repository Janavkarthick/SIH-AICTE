"""Pydantic schemas for statutory compliance evaluations and intake calculations."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ComplianceResultResponse(BaseModel):
    """Single compliance rule evaluation result."""
    id: int
    application_id: int
    rule_id: str
    rule_description: str
    category: str
    declared_value: Optional[str] = None
    required_value: Optional[str] = None
    status: str  # pass, gap, needs_evidence, needs_physical_inspection
    details: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplianceSummaryResponse(BaseModel):
    """Aggregated compliance scorecard for an application."""
    application_id: int
    total_rules_checked: int
    passed_count: int
    gap_count: int
    needs_evidence_count: int
    needs_physical_inspection_count: int
    results: List[ComplianceResultResponse] = []


class CapacityCalculationResponse(BaseModel):
    """Calculated maximum intake capacity based on physical infrastructure [Reference - verify against Approval Process Handbook] (illustrative).
    
    All formulas and thresholds marked: illustrative: replace with Approval Process Handbook values.
    """
    application_id: int
    declared_intake: int
    max_calculated_capacity: int
    is_capacity_sufficient: bool
    classroom_capacity: int
    lab_capacity: int
    faculty_capacity: int
    limiting_factor: str
    breakdown: Dict[str, Any]
    formula_note: str = "illustrative: replace with Approval Process Handbook values"
