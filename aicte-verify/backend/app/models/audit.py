"""Tamper-evident append-only audit database model with cryptographic chaining."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class AuditEntry(Base):
    """Immutable audit record tied to preceding ledger entries via SHA-256."""
    __tablename__ = "audit_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_username: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    rule_check: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    records_checked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    entry_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Relationships
    actor = relationship("User", foreign_keys=[actor_id])
