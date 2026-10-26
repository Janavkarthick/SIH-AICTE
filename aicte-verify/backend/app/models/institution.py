"""Institution database model representing affiliated colleges and polytechnics."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Institution(Base):
    """Educational institution profile with physical campus and trust metadata."""
    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)  # AICTE permanent ID
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    region: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    trust_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trust_registration_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    campus_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    campus_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    established_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    users = relationship("User", back_populates="institution")
    applications = relationship("Application", back_populates="institution", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="institution", cascade="all, delete-orphan")
