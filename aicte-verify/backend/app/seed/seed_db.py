"""Database Seeding Script for AICTE-Verify.

Generates initial synthetic users, 6 institutions across regions, sample applications,
sample PDF regulatory artifacts, graph nodes for collusion detection, and mock issuer certificates.
ALL DATA IS STRICTLY SYNTHETIC AND ANONYMIZED. Marked SIMULATED.
"""

import hashlib
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditLogger
from app.core.config import settings
from app.core.security import hash_password
from app.mock_issuer.service import mock_issuer_service
from app.models.application import Application, ApplicationHistory
from app.models.compliance import ComplianceResult
from app.models.document import Document, DocumentClassification, ExtractedData
from app.models.flag import Flag
from app.models.graph import GraphEntity, GraphRelation
from app.models.institution import Institution
from app.models.user import User
from app.models.verification import VerificationResult


def create_sample_pdf(file_path: str, title: str, lines: list):
    """Generate a clean synthetic PDF for OCR and document processing."""
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(p), pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, title)
    c.setFont("Helvetica", 11)
    y = 710
    for line in lines:
        c.drawString(72, y, line)
        y -= 22
    c.save()


async def seed_database(db: AsyncSession) -> None:
    """Populate database with synthetic development records if empty."""
    # Check if already seeded
    user_check = await db.execute(select(User))
    if user_check.scalars().first():
        return

    # 1. Create Default Users
    # Passwords: admin123, officer123, college123
    users_data = [
        {"username": "admin", "email": "admin@aicte.gov.in.simulated", "password": "admin123", "full_name": "AICTE Central Administrator", "role": "admin", "region": "Central", "institution_id": None},
        {"username": "officer1", "email": "officer.south@aicte.gov.in.simulated", "password": "officer123", "full_name": "Dr. V. Srinivasan (RO South)", "role": "officer", "region": "Southern", "institution_id": None},
        {"username": "officer2", "email": "officer.north@aicte.gov.in.simulated", "password": "officer123", "full_name": "Prof. R. K. Sharma (RO North)", "role": "officer", "region": "Northern", "institution_id": None},
        {"username": "college1", "email": "registrar@apextech.edu.simulated", "password": "college123", "full_name": "Registrar, Apex Tech", "role": "college_user", "region": "Southern", "institution_id": 1},
        {"username": "college2", "email": "dean@zenitheng.edu.simulated", "password": "college123", "full_name": "Dean Admin, Zenith Eng", "role": "college_user", "region": "Western", "institution_id": 2},
    ]

    user_objects = []
    for u in users_data:
        usr = User(
            username=u["username"],
            email=u["email"],
            hashed_password=hash_password(u["password"]),
            full_name=u["full_name"],
            role=u["role"],
            region=u["region"],
            institution_id=u["institution_id"],
            is_active=True,
        )
        db.add(usr)
        user_objects.append(usr)
    await db.commit()

    # 2. Create 6 Synthetic Institutions
    institutions_data = [
        {
            "id": 1,
            "name": "Apex Institute of Technology",
            "code": "1-100234",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "region": "Southern",
            "address": "45 Knowledge Park, OMR Highway",
            "trust_name": "Sri Krishna Educational & Charitable Trust",
            "trust_registration_number": "TR-TN-2004-981",
            "campus_latitude": 12.9234,
            "campus_longitude": 80.1982,
            "established_year": 2004,
        },
        {
            "id": 2,
            "name": "Zenith College of Engineering",
            "code": "1-100567",
            "city": "Pune",
            "state": "Maharashtra",
            "region": "Western",
            "address": "12 Hinjawadi Phase 2, IT Hub",
            "trust_name": "Sahyadri Higher Education Foundation",
            "trust_registration_number": "TR-MH-2009-412",
            "campus_latitude": 18.5912,
            "campus_longitude": 73.7389,
            "established_year": 2009,
        },
        {
            "id": 3,
            "name": "Northern Polytechnic Institute",
            "code": "1-100891",
            "city": "Lucknow",
            "state": "Uttar Pradesh",
            "region": "Northern",
            "address": "88 Gomti Nagar Industrial Area",
            "trust_name": "Sri Krishna Educational & Charitable Trust",  # Shared trust to test graph
            "trust_registration_number": "TR-TN-2004-981",
            "campus_latitude": 26.8467,
            "campus_longitude": 80.9462,
            "established_year": 2012,
        },
        {
            "id": 4,
            "name": "Eastern Academy of Science & Technology",
            "code": "1-100345",
            "city": "Kolkata",
            "state": "West Bengal",
            "region": "Eastern",
            "address": "21 Salt Lake Sector V",
            "trust_name": "Bengal Science Development Society",
            "trust_registration_number": "TR-WB-1998-129",
            "campus_latitude": 22.5801,
            "campus_longitude": 88.4312,
            "established_year": 1998,
        },
        {
            "id": 5,
            "name": "Deccan Institute of Engineering",
            "code": "1-100678",
            "city": "Hyderabad",
            "state": "Telangana",
            "region": "South-Central",
            "address": "104 Gachibowli Tech Corridor",
            "trust_name": "Telangana Technical Heritage Society",
            "trust_registration_number": "TR-TS-2015-883",
            "campus_latitude": 17.4401,
            "campus_longitude": 78.3489,
            "established_year": 2015,
        },
        {
            "id": 6,
            "name": "Central Valley Engineering College",
            "code": "1-100912",
            "city": "Bhopal",
            "state": "Madhya Pradesh",
            "region": "Central",
            "address": "15 Raisen Bypass Highway",
            "trust_name": "Narmada Educational Foundation",
            "trust_registration_number": "TR-MP-2011-552",
            "campus_latitude": 23.2599,
            "campus_longitude": 77.4126,
            "established_year": 2011,
        },
    ]

    for inst in institutions_data:
        db.add(Institution(**inst))
    await db.commit()

    # 3. Create Applications
    app1 = Application(
        id=1,
        institution_id=1,
        category="extension_of_approval",
        academic_year="2025-2026",
        status="under_review",
        submitted_by=4,  # college1
        assigned_officer=2,  # officer1
        risk_score=28.5,
        risk_level="Low",
        intake_applied=480,
        current_intake=480,
    )
    app2 = Application(
        id=2,
        institution_id=2,
        category="increase_of_intake",
        academic_year="2025-2026",
        status="deficient",
        submitted_by=5,  # college2
        assigned_officer=2,
        risk_score=68.0,
        risk_level="High",
        intake_applied=600,
        current_intake=420,
    )
    db.add(app1)
    db.add(app2)
    await db.commit()

    # 4. Generate Synthetic Document Files on Disk
    sample_docs_info = [
        {
            "application_id": 1,
            "institution_id": 1,
            "document_type": "fire_safety_certificate",
            "filename": "fire_safety_apex.pdf",
            "title": "DEPARTMENT OF FIRE AND EMERGENCY SERVICES",
            "lines": [
                "STATE FIRE DISASTER MANAGEMENT COMMAND",
                "FIRE SAFETY CERTIFICATE / RENEWAL COMPLIANCE",
                "Certificate No: CFD/2024/FS-8891",
                "Date of Issue: 2024-06-15",
                "Valid Up to: 2025-06-14",
                "Name of the Institution: Apex Institute of Technology",
                "Address: 45 Knowledge Park, OMR Highway, Chennai",
                "Permanent AICTE ID: 1-100234",
                "Total Built-up Area: 65,000 sq ft across 4 Instructional Blocks",
                "Status: Certified Fully Compliant with Fire Hydrant & Hose Reels",
                "Issuing Authority: Divisional Fire Officer, Metro Command",
            ],
        },
        {
            "application_id": 1,
            "institution_id": 1,
            "document_type": "affidavit",
            "filename": "affidavit_apex.pdf",
            "title": "NON-JUDICIAL STAMP PAPER - GOVERNMENT OF TAMIL NADU",
            "lines": [
                "AFFIDAVIT ON STAMP PAPER",
                "Before the Executive Magistrate / Notary Public",
                "I, Dr. K. Soundararajan, Secretary of Sri Krishna Trust, solemnly affirm:",
                "1. That our institution, Apex Institute of Technology (PID: 1-100234),",
                "   is applying for Extension of Approval for Academic Year 2025-2026.",
                "2. Total Approved Intake: 480 seats in Engineering and Technology.",
                "3. Survey No: 204/1A, Total Land Area: 10.5 Acres.",
                "4. All teaching staff qualifications conform to AICTE norms.",
                "Deponent Signature & Notary Public Seal",
            ],
        },
        {
            "application_id": 2,
            "institution_id": 2,
            "document_type": "fire_safety_certificate",
            "filename": "fire_safety_zenith_expired.pdf",
            "title": "MUNICIPAL CORPORATION FIRE SAFETY DIVISION",
            "lines": [
                "ANNUAL FIRE SAFETY CERTIFICATE",
                "Reference Number: CFD/2023/FS-1042-EXPIRED",
                "Date of Issue: 2023-01-10",
                "Expiry Date: 2024-01-09",
                "Name of the Institution: Zenith College of Engineering",
                "Permanent ID: 1-100567",
                "Intake Approved: 420",
                "Status: EXPIRED - Renewal Pending Inspection",
            ],
        },
    ]

    created_docs = []
    for s_doc in sample_docs_info:
        file_path = f"./uploads/app_{s_doc['application_id']}/{s_doc['filename']}"
        create_sample_pdf(file_path, s_doc["title"], s_doc["lines"])

        with open(file_path, "rb") as f:
            f_hash = hashlib.sha256(f.read()).hexdigest()

        doc_entry = Document(
            application_id=s_doc["application_id"],
            institution_id=s_doc["institution_id"],
            document_type=s_doc["document_type"],
            filename=s_doc["filename"],
            original_filename=s_doc["filename"],
            file_path=str(Path(file_path).resolve()),
            file_hash_sha256=f_hash,
            version=1,
            status="processed",
            is_current=True,
        )
        db.add(doc_entry)
        created_docs.append((doc_entry, s_doc))
    await db.commit()

    # 5. Populate Extracted Data for Application 1 & 2 Documents
    for doc_entry, meta in created_docs:
        await db.refresh(doc_entry)
        if "apex" in meta["filename"]:
            db.add(ExtractedData(document_id=doc_entry.id, field_name="institution_name", field_value="Apex Institute of Technology", confidence=0.98))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="institution_id", field_value="1-100234", confidence=0.99))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="certificate_number", field_value="CFD/2024/FS-8891", confidence=0.95))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="issue_date", field_value="2024-06-15", confidence=0.94))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="expiry_date", field_value="2025-06-14", confidence=0.94))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="area_sqft", field_value="65000", confidence=0.92))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="intake", field_value="480", confidence=0.93))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="faculty_ids", field_value="ABCDE1234F, BCDEF2345G, CDEFG3456H, DEFGH4567I", confidence=0.96))
        else:
            db.add(ExtractedData(document_id=doc_entry.id, field_name="institution_name", field_value="Zenith College of Engineering", confidence=0.98))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="certificate_number", field_value="CFD/2023/FS-1042-EXPIRED", confidence=0.95))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="issue_date", field_value="2023-01-10", confidence=0.94))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="expiry_date", field_value="2024-01-09", confidence=0.94))
    await db.commit()

    # 6. Seed Flags for Application 2 (to demonstrate high risk)
    db.add(
        Flag(
            application_id=2,
            document_id=created_docs[-1][0].id,
            flag_type="validation",
            severity="high",
            code="VAL-DOC-EXPIRED",
            title="Fire Safety Certificate Expired",
            reason="Fire safety clearance certificate expired on 2024-01-09. Current valid certificate mandatory.",
            confidence=0.98,
            rule_id="DOC-EXPIRY-FIRE",
            check_name="Validity Window Check",
        )
    )
    db.add(
        Flag(
            application_id=2,
            document_id=None,
            flag_type="compliance",
            severity="critical",
            code="COM-INTAKE-HIKE",
            title="Excessive Intake Increase Request",
            reason="Requested intake increase from 420 to 600 exceeds 50% annual regulatory ceiling.",
            confidence=1.0,
            rule_id="INTAKE-GROWTH-CAP",
            check_name="Intake Expansion Bounds Check",
        )
    )
    await db.commit()

    # 7. Seed Knowledge Graph Entities & Collusion Relations
    # Example 1: Dr. R. Ramanathan working at both Inst 1 (Apex) and Inst 2 (Zenith)
    # Example 2: Same land parcel Survey #441/2 claimed by both Inst 1 and Inst 3
    nodes = [
        GraphEntity(id=1, entity_type="institution", entity_id="1-100234", name="Apex Institute of Technology", metadata_json=json.dumps({"city": "Chennai"})),
        GraphEntity(id=2, entity_type="institution", entity_id="1-100567", name="Zenith College of Engineering", metadata_json=json.dumps({"city": "Pune"})),
        GraphEntity(id=3, entity_type="institution", entity_id="1-100891", name="Northern Polytechnic Institute", metadata_json=json.dumps({"city": "Lucknow"})),
        GraphEntity(id=4, entity_type="faculty", entity_id="PAN-RMN-7741", name="Dr. R. Ramanathan (Professor, CSE)", metadata_json=json.dumps({"pan": "ABCDE7741R", "specialization": "VLSI"})),
        GraphEntity(id=5, entity_type="land", entity_id="SURV-441-2", name="Survey Parcel #441/2 (12 Acres)", metadata_json=json.dumps({"survey_no": "441/2", "district": "Kanchipuram"})),
        GraphEntity(id=6, entity_type="trust", entity_id="TR-TN-2004-981", name="Sri Krishna Educational & Charitable Trust", metadata_json=json.dumps({"reg": "TR-TN-2004-981"})),
    ]
    for n in nodes:
        db.add(n)
    await db.commit()

    edges = [
        # Faculty duplication
        GraphRelation(source_entity_id=4, target_entity_id=1, relation_type="employed_at", is_flagged=True, flag_reason="COLLUSION ANOMALY: Dual full-time faculty listing across multiple institutions simultaneously."),
        GraphRelation(source_entity_id=4, target_entity_id=2, relation_type="employed_at", is_flagged=True, flag_reason="COLLUSION ANOMALY: Dual full-time faculty listing across multiple institutions simultaneously."),
        # Land parcel duplication
        GraphRelation(source_entity_id=1, target_entity_id=5, relation_type="owns_land", is_flagged=True, flag_reason="COLLUSION ANOMALY: Same land parcel Survey #441/2 concurrently claimed by 2 separate institutions."),
        GraphRelation(source_entity_id=3, target_entity_id=5, relation_type="owns_land", is_flagged=True, flag_reason="COLLUSION ANOMALY: Same land parcel Survey #441/2 concurrently claimed by 2 separate institutions."),
        # Trust links
        GraphRelation(source_entity_id=1, target_entity_id=6, relation_type="governed_by", is_flagged=False),
        GraphRelation(source_entity_id=3, target_entity_id=6, relation_type="governed_by", is_flagged=False),
    ]
    for edge in edges:
        db.add(edge)
    await db.commit()

    # 8. Seed Genesis Block in Cryptographic Audit Ledger
    await AuditLogger.log(
        db=db,
        action="GENESIS_SYSTEM_INITIALIZATION",
        actor_id=1,
        actor_username="system_init",
        details={"status": "INITIALIZED", "system": "AICTE-Verify Backend Engine", "mode": "SIMULATED_PROTOTYPE"},
        rule_check="INTEGRITY_GENESIS_CHAIN_START",
    )
