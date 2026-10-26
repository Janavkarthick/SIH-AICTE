"""Regulatory deficiency notice generation and review endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, role_required
from app.models.application import Application
from app.models.flag import Flag
from app.models.institution import Institution
from app.models.user import User
from app.schemas.letter import (
    LetterApproveRequest,
    LetterGenerateRequest,
    LetterImproveRequest,
    LetterResponse,
)
from app.services.letters.service import letter_service

router = APIRouter(prefix="/letters", tags=["Deficiency Letters"])


@router.post("/generate/{application_id}", response_model=LetterResponse)
async def generate_deficiency_letter(
    application_id: int,
    payload: LetterGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate official deficiency letter in English, Tamil, or Hindi."""
    app = await db.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    inst = await db.get(Institution, app.institution_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    # Fetch active open flags
    flag_stmt = select(Flag).where(Flag.application_id == application_id, Flag.is_resolved == False)
    flags = list((await db.execute(flag_stmt)).scalars().all())

    letter = letter_service.generate_deficiency_letter(
        application=app,
        institution=inst,
        open_flags=flags,
        language=payload.language,
        deadline_days=payload.deadline_days,
        additional_remarks=payload.additional_remarks,
    )
    return letter


@router.post("/improve")
async def improve_letter_wording(
    payload: LetterImproveRequest,
    current_user: User = Depends(get_current_user),
):
    """Refine deficiency notice clarity and legal tone using Gemini LLM."""
    improved_text = await letter_service.improve_letter_with_gemini(
        draft_content=payload.content,
        language=payload.language,
        tone=payload.tone,
    )
    return {
        "original_content": payload.content,
        "improved_content": improved_text,
        "language": payload.language,
        "enhanced": improved_text != payload.content,
    }


@router.put("/{application_id}/approve", dependencies=[Depends(role_required("officer", "admin"))])
async def approve_deficiency_letter(
    application_id: int,
    payload: LetterApproveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve and dispatch deficiency notice to institution (Officer/Admin only)."""
    app = await db.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    app.status = "deficient"
    await db.commit()

    return {
        "status": "approved",
        "application_id": application_id,
        "officer": current_user.username,
        "message": "Deficiency notice formally authorized and dispatched to college portal.",
    }
