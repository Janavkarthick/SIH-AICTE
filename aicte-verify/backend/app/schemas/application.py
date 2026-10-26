"""Pydantic schemas for applications, validation reports, and risk breakdown."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.document import DocumentResponse
from app.schemas.flag import FlagResponse
from app.schemas.compliance import ComplianceResultResponse


class ApplicationBase(BaseModel):
    """Base application fields."""
    category: str = Field(
        ...,
        description="extension_of_approval, increase_of_intake, new_course, or closure"
    )
    academic_year: str = Field("2025-2026", max_length=20)
    intake_applied: int = Field(0, ge=0)
    current_intake: int = Field(0, ge=0)
    submission_date: Optional[date] = Field(None, description="Official statutory application submission date (not DB insert time)")


class ApplicationCreate(ApplicationBase):
    """Schema for submitting an application."""
    institution_id: Optional[int] = None  # Inferred for college_user


class ApplicationUpdate(BaseModel):
    """Schema for updating draft application fields."""
    category: Optional[str] = None
    academic_year: Optional[str] = None
    intake_applied: Optional[int] = None
    current_intake: Optional[int] = None


class ApplicationStatusUpdate(BaseModel):
    """Schema for officer/admin changing status."""
    status: str = Field(
        ...,
        description="draft, submitted, under_review, verified, deficient, approved, rejected"
    )
    reason: Optional[str] = None


class ApplicationResubmit(BaseModel):
    """Schema for submitting a revised application version."""
    revision_note: str = Field(..., min_length=5)
    updated_fields: Dict[str, Any] = {}


class ApplicationHistoryResponse(BaseModel):
    """Versioned historical revision."""
    id: int
    application_id: int
    version: int
    changes_json: str
    created_by: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationResponse(ApplicationBase):
    """Full application response with relations."""
    id: int
    institution_id: int
    status: str
    submitted_by: Optional[int] = None
    assigned_officer: Optional[int] = None
    risk_score: float
    risk_level: str
    risk_breakdown: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Computed convenience properties for frontend
    application_number: Optional[str] = None
    institution_name: Optional[str] = None
    institution_type: Optional[str] = "Technical Campus"
    region: Optional[str] = "Southern"
    state: Optional[str] = "Tamil Nadu"
    applied_intake: Optional[int] = None
    approved_intake: Optional[int] = None
    total_flags_count: Optional[int] = 0
    critical_flags_count: Optional[int] = 0
    submission_version: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)



class ApplicationDetailResponse(ApplicationResponse):
    """Detailed application view including documents, flags, and compliance results."""
    documents: List[DocumentResponse] = []
    flags: List[FlagResponse] = []
    compliance_results: List[ComplianceResultResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ApplicationListResponse(BaseModel):
    """Paginated list of applications."""
    total: int
    items: List[ApplicationResponse]


class FlagItem(BaseModel):
    """Flag item within validation report."""
    code: str
    title: str
    severity: str
    reason: str
    rule_id: Optional[str] = None
    document_id: Optional[int] = None


class RiskContribution(BaseModel):
    """Weight and contribution of an individual flag to the risk score."""
    flag_code: str
    title: str
    severity: str
    weight: float
    contribution_score: float


class RiskBreakdown(BaseModel):
    """Risk score composition and level."""
    risk_score: float
    risk_level: str  # Low, Medium, High
    total_flags: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    contributions: List[RiskContribution] = []
    threshold_note: str = "illustrative: replace with Approval Process Handbook values"


class ValidationReport(BaseModel):
    """Comprehensive automated validation report."""
    application_id: int
    application_category: str
    is_valid: bool
    summary: str
    missing_documents: List[str] = []
    expired_documents: List[str] = []
    cross_check_mismatches: List[str] = []
    flags: List[FlagItem] = []
    risk: RiskBreakdown
