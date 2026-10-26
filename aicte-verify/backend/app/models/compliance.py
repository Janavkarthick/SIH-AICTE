"""Compliance engine assessment models mapped against statutory AICTE norms."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ComplianceResult(Base):
    """Evaluation record of an application against AICTE Handbook norms."""
    __tablename__ = "compliance_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    rule_description: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # infrastructure, faculty, intake, area, labs
    declared_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    required_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # pass, gap, needs_evidence, needs_physical_inspection
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    application = relationship("Application", back_populates="compliance_results")
