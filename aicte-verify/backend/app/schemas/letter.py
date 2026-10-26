"""Pydantic schemas for deficiency letters and natural language generation."""

from typing import List, Optional
from pydantic import BaseModel, Field


class LetterGenerateRequest(BaseModel):
    """Parameters for generating a deficiency notice."""
    language: str = Field("eng", description="eng, tam, or hin")
    deadline_days: int = Field(15, ge=1, le=60)
    additional_remarks: Optional[str] = None


class LetterResponse(BaseModel):
    """Generated regulatory deficiency letter content."""
    application_id: int
    institution_name: str
    language: str
    subject: str
    content: str
    deficiencies_count: int
    open_flags: List[str] = []
    status: str = "draft"  # draft, approved, dispatched
    gemini_enhanced: bool = False


class LetterImproveRequest(BaseModel):
    """Request to enhance deficiency letter tone and clarity via LLM."""
    content: str
    language: str = "eng"
    tone: str = "formal_regulatory"


class LetterApproveRequest(BaseModel):
    """Officer formal approval of deficiency letter."""
    approved_content: str
    officer_notes: Optional[str] = None
