"""Pydantic schemas for document metadata, extracted entities, and forensics."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExtractedDataResponse(BaseModel):
    """Schema for individual OCR/native/QR extracted field."""
    id: int
    document_id: int
    field_name: str
    field_value: Optional[str] = None
    confidence: float
    page_number: int
    bbox_json: Optional[str] = None
    method: str
    language: str

    model_config = ConfigDict(from_attributes=True)


class DocumentClassificationResponse(BaseModel):
    """Schema for document classification output."""
    id: int
    document_id: int
    predicted_type: str
    confidence: float
    method: str

    model_config = ConfigDict(from_attributes=True)


class DocumentBase(BaseModel):
    """Shared document properties."""
    document_type: str
    filename: str
    original_filename: str
    file_hash_sha256: str
    version: int = 1
    status: str = "pending"
    is_current: bool = True


class DocumentUpload(BaseModel):
    """Metadata required alongside document upload."""
    application_id: int
    document_type: str


class DocumentResponse(DocumentBase):
    """Standard document response."""
    id: int
    application_id: int
    institution_id: int
    file_path: str
    upload_time: datetime
    replaced_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(DocumentResponse):
    """Comprehensive document view including extracted data and classification."""
    extracted_data: List[ExtractedDataResponse] = []
    classification: Optional[DocumentClassificationResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ForensicsFinding(BaseModel):
    """Single forensic anomaly or verification check."""
    check: str
    passed: bool
    details: str
    severity: str = "info"  # info, low, medium, high, critical
    indicator: str = "preliminary indicator - human verification required"


class DocumentForensicsResponse(BaseModel):
    """Full forensic analysis payload for a document."""
    document_id: int
    file_hash: str
    metadata_checks: List[ForensicsFinding] = []
    font_consistency: List[ForensicsFinding] = []
    image_forensics: List[ForensicsFinding] = []
    digital_signature: List[ForensicsFinding] = []
    duplicate_checks: List[ForensicsFinding] = []
    qr_match_check: Optional[ForensicsFinding] = None
    ela_heatmap_url: Optional[str] = None
    all_findings_tagged: str = "preliminary indicator - human verification required"
