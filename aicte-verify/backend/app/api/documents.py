"""Document lifecycle, artifact upload, pipeline processing, and evidence endpoints."""

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.application import Application
from app.models.document import Document, DocumentClassification, ExtractedData
from app.models.user import User
from app.schemas.document import (
    DocumentDetailResponse,
    DocumentForensicsResponse,
    DocumentResponse,
)
from app.services.audit.service import audit_service
from app.services.classify.service import classifier_service
from app.services.evidence.service import evidence_service
from app.services.extract.service import extraction_service
from app.services.forensics.service import forensics_service
from app.services.ocr.service import ocr_service

router = APIRouter(prefix="/documents", tags=["Documents"])


def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filenames against directory traversal vulnerabilities."""
    clean = os.path.basename(filename)
    clean = "".join(c for c in clean if c.isalnum() or c in "._- ")
    return clean or "document.bin"


async def process_document_pipeline(
    doc: Document, db: AsyncSession
) -> None:
    """Execute OCR, classification, and field extraction pipeline on an uploaded file."""
    # 1. OCR text extraction
    ocr_res = ocr_service.process_document(doc.file_path)
    text = ocr_res.get("text", "")
    blocks = ocr_res.get("blocks", [])

    # 2. Document classification
    class_res = classifier_service.classify(
        text=text, filename=doc.original_filename, declared_type=doc.document_type
    )

    # Persist or update classification
    cls_stmt = select(DocumentClassification).where(DocumentClassification.document_id == doc.id)
    cls_rec = (await db.execute(cls_stmt)).scalar_one_or_none()
    if cls_rec:
        cls_rec.predicted_type = class_res["predicted_type"]
        cls_rec.confidence = class_res["confidence"]
        cls_rec.method = class_res["method"]
    else:
        cls_rec = DocumentClassification(
            document_id=doc.id,
            predicted_type=class_res["predicted_type"],
            confidence=class_res["confidence"],
            method=class_res["method"],
        )
        db.add(cls_rec)

    # 3. Field Extraction
    # Generate page image for QR detection if PDF
    rendered_page = None
    try:
        rendered_page = ocr_service.render_page_image(doc.file_path, page_num=1)
    except Exception:
        pass

    extracted_items = extraction_service.extract_fields(
        text=text, blocks=blocks, image_path=rendered_page or doc.file_path
    )

    # Clear previous extractions if any
    del_stmt = select(ExtractedData).where(ExtractedData.document_id == doc.id)
    old_ext = (await db.execute(del_stmt)).scalars().all()
    for o in old_ext:
        await db.delete(o)

    for item in extracted_items:
        ext_entry = ExtractedData(
            document_id=doc.id,
            field_name=item["field_name"],
            field_value=item["field_value"],
            confidence=item["confidence"],
            page_number=item.get("page_number", 1),
            bbox_json=item.get("bbox_json"),
            method=item.get("method", "ocr"),
            language=item.get("language", "eng"),
        )
        db.add(ext_entry)

    doc.status = "processed"
    await db.commit()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    application_id: int = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a regulatory document, compute SHA-256, and trigger processing pipeline."""
    app = await db.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if current_user.role == "college_user" and app.institution_id != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Read and validate size
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit.",
        )

    # Compute SHA-256
    file_hash = hashlib.sha256(content).hexdigest()
    clean_orig_name = sanitize_filename(file.filename or "upload.pdf")

    # Save to disk
    upload_root = Path(settings.UPLOAD_DIR) / f"app_{application_id}"
    upload_root.mkdir(parents=True, exist_ok=True)
    saved_filename = f"{document_type}_{file_hash[:12]}_{clean_orig_name}"
    saved_path = upload_root / saved_filename

    with open(saved_path, "wb") as f:
        f.write(content)

    new_doc = Document(
        application_id=application_id,
        institution_id=app.institution_id,
        document_type=document_type,
        filename=saved_filename,
        original_filename=clean_orig_name,
        file_path=str(saved_path.resolve()),
        file_hash_sha256=file_hash,
        version=1,
        status="pending",
        is_current=True,
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)

    # Log to audit trail
    await audit_service.log_upload(
        db,
        user=current_user,
        document_id=new_doc.id,
        filename=clean_orig_name,
        file_hash=file_hash,
        application_id=application_id,
    )

    # Run processing pipeline synchronously for prototype immediacy
    await process_document_pipeline(new_doc, db)
    await db.refresh(new_doc)

    return DocumentResponse.model_validate(new_doc)


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve document metadata, classifications, and extracted bounding box fields."""
    stmt = (
        select(Document)
        .options(
            selectinload(Document.extracted_data),
            selectinload(Document.classification),
        )
        .where(Document.id == document_id)
    )
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return DocumentDetailResponse.model_validate(doc)


@router.get("/{document_id}/content")
async def get_document_content(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Serve the raw document binary (PDF/Image)."""
    doc = await db.get(Document, document_id)
    if not doc or not Path(doc.file_path).exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File content not found")

    return FileResponse(doc.file_path, filename=doc.original_filename)


@router.get("/{document_id}/evidence")
async def get_document_evidence(
    document_id: int,
    page: int = Query(1, ge=1),
    highlight: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve visual evidence package with bounding box annotations and blended ELA heatmap."""
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    ext_stmt = select(ExtractedData).where(ExtractedData.document_id == document_id)
    ext_data = list((await db.execute(ext_stmt)).scalars().all())

    evidence = evidence_service.build_evidence_view(
        document=doc,
        extracted_data=ext_data,
        page_num=page,
        highlight_field=highlight,
    )
    return evidence


@router.post("/{document_id}/reupload", response_model=DocumentResponse)
async def reupload_rectified_document(
    document_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a replacement version of a previously flagged document (Rectification flow)."""
    old_doc = await db.get(Document, document_id)
    if not old_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Original document not found")

    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    clean_orig_name = sanitize_filename(file.filename or "rectification.pdf")

    upload_root = Path(settings.UPLOAD_DIR) / f"app_{old_doc.application_id}"
    upload_root.mkdir(parents=True, exist_ok=True)
    saved_filename = f"{old_doc.document_type}_v{old_doc.version + 1}_{file_hash[:12]}_{clean_orig_name}"
    saved_path = upload_root / saved_filename

    with open(saved_path, "wb") as f:
        f.write(content)

    new_doc = Document(
        application_id=old_doc.application_id,
        institution_id=old_doc.institution_id,
        document_type=old_doc.document_type,
        filename=saved_filename,
        original_filename=clean_orig_name,
        file_path=str(saved_path.resolve()),
        file_hash_sha256=file_hash,
        version=old_doc.version + 1,
        status="pending",
        is_current=True,
    )
    db.add(new_doc)
    await db.flush()

    # Demote old document from being current
    old_doc.is_current = False
    old_doc.replaced_by = new_doc.id

    await db.commit()
    await db.refresh(new_doc)

    await process_document_pipeline(new_doc, db)
    await db.refresh(new_doc)

    return DocumentResponse.model_validate(new_doc)


@router.post("/{document_id}/process", response_model=DocumentResponse)
async def trigger_document_process(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Re-trigger OCR, classification, and field extraction pipeline."""
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    await process_document_pipeline(doc, db)
    await db.refresh(doc)
    return DocumentResponse.model_validate(doc)


@router.get("/{document_id}/forensics", response_model=DocumentForensicsResponse)
async def get_document_forensics(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run forensic examination: metadata, typography, ELA, copy-move, and duplicate hash checks."""
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Load extracted fields
    ext_stmt = select(ExtractedData).where(ExtractedData.document_id == document_id)
    ext_data = {e.field_name: e.field_value for e in (await db.execute(ext_stmt)).scalars().all() if e.field_value}

    # Fetch other document hashes for duplicate cross-matching
    hash_stmt = select(Document.id, Document.file_hash_sha256).where(Document.id != document_id)
    other_docs = (await db.execute(hash_stmt)).all()
    existing_hashes = [(d[0], d[1], None) for d in other_docs]

    # Find QR text if present
    qr_payload = ext_data.get("qr_code_payload")

    rendered_page = None
    try:
        rendered_page = ocr_service.render_page_image(doc.file_path, page_num=1)
    except Exception:
        pass

    forensics_report = forensics_service.analyze_document(
        document_id=doc.id,
        file_path=doc.file_path,
        page_image_path=rendered_page,
        qr_payload=qr_payload,
        extracted_fields=ext_data,
        existing_hashes=existing_hashes,
    )
    return forensics_report
