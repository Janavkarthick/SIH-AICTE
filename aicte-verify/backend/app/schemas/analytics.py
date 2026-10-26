from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FlagsBySeverity(BaseModel):
    info: int = 0
    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class VerificationOutcomeItem(BaseModel):
    name: str
    value: int
    color: str


class FlagTypeItem(BaseModel):
    type: str
    count: int


class AppStatusItem(BaseModel):
    status: str
    count: int


class ProcessingTimeTrendItem(BaseModel):
    week: str
    avg_days: float


class AnalyticsSummary(BaseModel):
    """Overall dashboard KPI metrics."""
    total_applications: int
    pending_review: int = 0
    approved_applications: int = 0
    rejected_applications: int = 0
    flags_by_severity: FlagsBySeverity = Field(default_factory=FlagsBySeverity)
    flags_by_type: List[FlagTypeItem] = Field(default_factory=list)
    verification_outcomes: List[VerificationOutcomeItem] = Field(default_factory=list)
    applications_by_status: List[AppStatusItem] = Field(default_factory=list)
    processing_times_trend: List[ProcessingTimeTrendItem] = Field(default_factory=list)
    average_risk_score: float = 0.0
    chain_integrity_status: str = "verified"
    total_documents: int = 0
    total_flags: int = 0
    open_flags: int = 0
    resolved_flags: int = 0
    high_risk_applications_count: int = 0


class FlagsByType(BaseModel):
    """Flag distribution breakdown for charts."""
    validation: int
    forensics: int
    verification: int
    compliance: int
    anomaly: int


class VerificationOutcomes(BaseModel):
    """Aggregate outcomes across all verification runs."""
    verified: int
    mismatch_detected: int
    expired: int
    verification_pending: int
    source_unavailable: int
    manual_review_required: int


class ProcessingTimeMetric(BaseModel):
    """Average pipeline processing times in seconds."""
    ocr_seconds: float
    forensics_seconds: float
    verification_seconds: float
    compliance_seconds: float
    total_pipeline_seconds: float

