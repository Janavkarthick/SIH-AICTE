"""Statutory compliance and intake capacity endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.application import Application
from app.models.compliance import ComplianceResult
from app.models.document import Document, ExtractedData
from app.models.user import User
from app.schemas.compliance import (
    CapacityCalculationResponse,
    ComplianceResultResponse,
    ComplianceSummaryResponse,
)
from app.services.compliance.service import compliance_service

router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.post("/check/{application_id}", response_model=ComplianceSummaryResponse)
async def run_compliance(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute statutory compliance checks against Approval Process Handbook norms."""
    app = await db.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    summary = await compliance_service.run_compliance_check(db, application_id)
    return summary


@router.get("/results/{application_id}", response_model=List[ComplianceResultResponse])
async def get_compliance_results(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve compliance results evaluated for an application."""
    stmt = select(ComplianceResult).where(ComplianceResult.application_id == application_id)
    results = list((await db.execute(stmt)).scalars().all())
    return [ComplianceResultResponse.model_validate(r) for r in results]


@router.get("/capacity/{application_id}", response_model=CapacityCalculationResponse)
async def get_intake_capacity(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate maximum intake capacity using statutory A1 infrastructure formulas.
    
    All thresholds marked: illustrative: replace with Approval Process Handbook values.
    """
    app = await db.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    # Load extracted fields
    doc_stmt = select(Document).where(Document.application_id == application_id, Document.is_current == True)
    docs = (await db.execute(doc_stmt)).scalars().all()
    doc_ids = [d.id for d in docs]

    ext_data = {}
    if doc_ids:
        ext_stmt = select(ExtractedData).where(ExtractedData.document_id.in_(doc_ids))
        for item in (await db.execute(ext_stmt)).scalars().all():
            if item.field_name and item.field_value:
                ext_data[item.field_name] = item.field_value

    declared_intake = app.intake_applied or app.current_intake or 300
    try:
        area_sqft = float(ext_data.get("area_sqft", "60000").replace(",", ""))
    except ValueError:
        area_sqft = 60000.0

    faculty_ids_str = ext_data.get("faculty_ids", "")
    faculty_count = max(80, len(faculty_ids_str.split(",")) if faculty_ids_str else 80)
    classrooms_count = 16

    res = compliance_service.calculate_capacity(
        declared_intake=declared_intake,
        area_sqft=area_sqft,
        faculty_count=faculty_count,
        classrooms_count=classrooms_count,
    )
    res.application_id = application_id
    return res
