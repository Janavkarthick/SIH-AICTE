"""Application models for AICTE approval workflows and versioned change history."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Application(Base):
    """Core regulatory approval application submitted by an educational institution."""
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    institution_id: Mapped[int] = mapped_column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # extension_of_approval, increase_of_intake, new_course, closure
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, default="2025-2026")
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        index=True
    )  # draft, submitted, under_review, verified, deficient, approved, rejected
    submitted_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_officer: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Risk scoring (illustrative: replace with Approval Process Handbook values)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), default="Low", nullable=False)  # Low, Medium, High
    risk_breakdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON breakdown
    
    intake_applied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_intake: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    institution = relationship("Institution", back_populates="applications")
    submitter = relationship("User", foreign_keys=[submitted_by], back_populates="submitted_applications")
    officer = relationship("User", foreign_keys=[assigned_officer], back_populates="assigned_applications")
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    flags = relationship("Flag", back_populates="application", cascade="all, delete-orphan")
    compliance_results = relationship("ComplianceResult", back_populates="application", cascade="all, delete-orphan")
    history = relationship("ApplicationHistory", back_populates="application", cascade="all, delete-orphan")


class ApplicationHistory(Base):
    """Tracks versioned changes, field revisions, and resubmissions of applications."""
    __tablename__ = "application_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    changes_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON diff or snapshot
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    application = relationship("Application", back_populates="history")
