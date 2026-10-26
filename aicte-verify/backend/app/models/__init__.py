"""Database models registration package for AICTE-Verify."""

from app.models.user import User
from app.models.institution import Institution
from app.models.application import Application, ApplicationHistory
from app.models.document import Document, ExtractedData, DocumentClassification
from app.models.flag import Flag
from app.models.verification import VerificationResult
from app.models.compliance import ComplianceResult
from app.models.audit import AuditEntry
from app.models.graph import GraphEntity, GraphRelation

__all__ = [
    "User",
    "Institution",
    "Application",
    "ApplicationHistory",
    "Document",
    "ExtractedData",
    "DocumentClassification",
    "Flag",
    "VerificationResult",
    "ComplianceResult",
    "AuditEntry",
    "GraphEntity",
    "GraphRelation",
]
