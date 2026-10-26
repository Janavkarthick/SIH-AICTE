"""Discrepancy and risk flag model across all verification engines."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Flag(Base):
    """Auditable regulatory issue, forensic irregularity, or compliance gap."""
    __tablename__ = "flags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    flag_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # validation, forensics, verification, compliance, anomaly
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )  # info, low, medium, high, critical
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # e.g., VAL-001, FOR-002
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)  # Plain-language explanation
    evidence_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON {document_id, page, bbox, heatmap_path}
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    rule_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    check_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # Resolution tracking
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    resolved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    application = relationship("Application", back_populates="flags")
    document = relationship("Document", back_populates="flags")
    resolver = relationship("User", foreign_keys=[resolved_by])
