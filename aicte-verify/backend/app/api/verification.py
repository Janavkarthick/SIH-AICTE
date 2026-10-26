"""External verification endpoints and officer manual adjudication queue."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, role_required
from app.models.application import Application
from app.models.document import Document
from app.models.institution import Institution
from app.models.user import User
from app.models.verification import VerificationResult
from app.schemas.verification import (
    ManualReviewQueueItem,
    VerificationResponse,
    VerificationTriggerRequest,
)
from app.services.verify.service import verification_service

router = APIRouter(prefix="/verify", tags=["Verification"])


@router.post("/{document_id}", response_model=VerificationResponse)
async def trigger_verification(
    document_id: int,
    payload: Optional[VerificationTriggerRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger external issuer verification for a document (SIMULATED or live)."""
    strategy = payload.verification_type if payload else "reference_lookup"

    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    result = await verification_service.verify_document(
        db=db,
        document_id=document_id,
        strategy_type=strategy,
        verified_by_user_id=current_user.id,
    )
    return VerificationResponse.model_validate(result)


@router.get("/results/{document_id}", response_model=List[VerificationResponse])
async def get_verification_results(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all verification attempts and outcomes for a document."""
    stmt = select(VerificationResult).where(VerificationResult.document_id == document_id)
    results = list((await db.execute(stmt)).scalars().all())
    return [VerificationResponse.model_validate(r) for r in results]


@router.get("/queue", response_model=List[ManualReviewQueueItem], dependencies=[Depends(role_required("officer", "admin"))])
async def get_manual_review_queue(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve queue of documents needing officer manual examination."""
    stmt = (
        select(VerificationResult, Document, Institution)
        .join(Document, VerificationResult.document_id == Document.id)
        .join(Institution, Document.institution_id == Institution.id)
        .where(
            VerificationResult.status.in_([
                "manual_review_required",
                "mismatch_detected",
                "source_unavailable",
                "expired",
            ])
        )
    )
    res = await db.execute(stmt)
    queue_items = []

    for v_res, doc, inst in res.all():
        queue_items.append(
            ManualReviewQueueItem(
                document_id=doc.id,
                application_id=doc.application_id,
                institution_name=inst.name,
                document_type=doc.document_type,
                verification_status=v_res.status,
                reason=f"Status: {v_res.status} via {v_res.source_name}",
                uploaded_at=doc.upload_time,
            )
        )

    return queue_items
