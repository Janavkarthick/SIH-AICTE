"""Verification result models connecting submitted data to authoritative issuer registries."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class VerificationResult(Base):
    """Authoritative cross-check outcome from issuing bodies (SIMULATED or live)."""
    __tablename__ = "verification_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    verification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # qr, reference_lookup, digital_signature
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # verified, mismatch_detected, expired, verification_pending, source_unavailable, manual_review_required
    source_name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_response_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_data_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    discrepancies_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    verified_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="verification_results")
    verifier = relationship("User", foreign_keys=[verified_by])
