"""Audit Service Wrapper.

Provides structured convenience methods for creating cryptographic audit trail entries
across all security, authentication, and regulatory workflows.
"""

from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.audit import AuditLogger
from app.models.user import User


class AuditService:
    """Service wrapper for logging actions to the tamper-evident hash chain."""

    async def log_login(
        self, db: AsyncSession, user: User, client_ip: Optional[str] = None
    ):
        """Log user authentication event."""
        await AuditLogger.log(
            db=db,
            action="USER_LOGIN",
            actor_id=user.id,
            actor_username=user.username,
            details={"role": user.role, "client_ip": client_ip or "unknown"},
        )

    async def log_upload(
        self,
        db: AsyncSession,
        user: Optional[User],
        document_id: int,
        filename: str,
        file_hash: str,
        application_id: int,
    ):
        """Log document upload and checksum registration."""
        await AuditLogger.log(
            db=db,
            action="DOCUMENT_UPLOAD",
            actor_id=user.id if user else None,
            actor_username=user.username if user else "system",
            details={
                "document_id": document_id,
                "application_id": application_id,
                "filename": filename,
                "file_hash_sha256": file_hash,
            },
        )

    async def log_review(
        self,
        db: AsyncSession,
        user: User,
        application_id: int,
        decision: str,
        note: Optional[str] = None,
    ):
        """Log officer application adjudication decision."""
        await AuditLogger.log(
            db=db,
            action="APPLICATION_REVIEW",
            actor_id=user.id,
            actor_username=user.username,
            details={
                "application_id": application_id,
                "decision": decision,
                "note": note,
            },
        )

    async def log_flag_resolve(
        self,
        db: AsyncSession,
        user: User,
        flag_id: int,
        flag_code: str,
        resolution_note: str,
    ):
        """Log formal resolution and clearance of a risk discrepancy flag."""
        await AuditLogger.log(
            db=db,
            action="FLAG_RESOLVE",
            actor_id=user.id,
            actor_username=user.username,
            details={
                "flag_id": flag_id,
                "flag_code": flag_code,
                "resolution_note": resolution_note,
            },
        )

    async def log_verification(
        self,
        db: AsyncSession,
        user: Optional[User],
        document_id: int,
        verification_type: str,
        status: str,
        source_name: str,
    ):
        """Log automated or manual document verification check."""
        await AuditLogger.log(
            db=db,
            action="DOCUMENT_VERIFY",
            actor_id=user.id if user else None,
            actor_username=user.username if user else "system",
            details={
                "document_id": document_id,
                "verification_type": verification_type,
                "status": status,
                "source": source_name,
            },
            rule_check=f"VERIFY_{verification_type.upper()}",
            records_checked=1,
            source_response=status,
        )

    async def log_compliance_run(
        self,
        db: AsyncSession,
        user: Optional[User],
        application_id: int,
        total_rules_checked: int,
        gap_count: int,
    ):
        """Log automated statutory compliance evaluation run."""
        await AuditLogger.log(
            db=db,
            action="COMPLIANCE_EVALUATION",
            actor_id=user.id if user else None,
            actor_username=user.username if user else "system",
            details={
                "application_id": application_id,
                "total_checked": total_rules_checked,
                "gaps_found": gap_count,
            },
            rule_check="STATUTORY_NORMS_EVALUATION",
            records_checked=total_rules_checked,
        )


# Singleton instance
audit_service = AuditService()
