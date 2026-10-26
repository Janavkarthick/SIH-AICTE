"""User database model for authentication and role-based access control."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class User(Base):
    """Represents a system user (admin, officer, or college user)."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # admin, officer, college_user
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Regional jurisdiction
    institution_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    institution = relationship("Institution", back_populates="users", foreign_keys=[institution_id])
    submitted_applications = relationship("Application", back_populates="submitter", foreign_keys="Application.submitted_by")
    assigned_applications = relationship("Application", back_populates="officer", foreign_keys="Application.assigned_officer")
