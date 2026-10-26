"""Pydantic schemas for educational institution profiles and physical assets."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class InstitutionBase(BaseModel):
    """Core attributes for an AICTE-affiliated institution."""
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=100, description="Permanent AICTE Institution Code")
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    region: str = Field(..., max_length=100)
    address: str
    trust_name: str = Field(..., max_length=255)
    trust_registration_number: str = Field(..., max_length=100)
    campus_latitude: Optional[float] = None
    campus_longitude: Optional[float] = None
    established_year: Optional[int] = None


class InstitutionCreate(InstitutionBase):
    """Schema for onboarding an institution."""
    pass


class InstitutionUpdate(BaseModel):
    """Schema for editing an institution's profile."""
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    trust_name: Optional[str] = None
    trust_registration_number: Optional[str] = None
    campus_latitude: Optional[float] = None
    campus_longitude: Optional[float] = None
    established_year: Optional[int] = None


class InstitutionResponse(InstitutionBase):
    """Public representation of an institution."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
