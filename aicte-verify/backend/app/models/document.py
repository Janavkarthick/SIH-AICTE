"""Document models for uploaded regulatory artifacts, OCR data, and classification."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Document(Base):
    """Uploaded verification document supporting multi-version lifecycle tracking."""
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id: Mapped[int] = mapped_column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    upload_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    replaced_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        index=True
    )  # pending, processed, verified, flagged, rejected
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    application = relationship("Application", back_populates="documents")
    institution = relationship("Institution", back_populates="documents")
    extracted_data = relationship("ExtractedData", back_populates="document", cascade="all, delete-orphan")
    classification = relationship("DocumentClassification", back_populates="document", uselist=False, cascade="all, delete-orphan")
    verification_results = relationship("VerificationResult", back_populates="document", cascade="all, delete-orphan")
    flags = relationship("Flag", back_populates="document", cascade="all, delete-orphan")


class ExtractedData(Base):
    """Field-level metadata and OCR extractions anchored by page number and bounding box coordinates."""
    __tablename__ = "extracted_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    field_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    bbox_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON [x, y, width, height]
    method: Mapped[str] = mapped_column(String(50), default="native", nullable=False)  # native, ocr, qr
    language: Mapped[str] = mapped_column(String(20), default="eng", nullable=False)

    # Relationships
    document = relationship("Document", back_populates="extracted_data")


class DocumentClassification(Base):
    """Automatic categorization output for uploaded documents."""
    __tablename__ = "document_classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    predicted_type: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String(50), default="keyword_rule", nullable=False)

    # Relationships
    document = relationship("Document", back_populates="classification")
