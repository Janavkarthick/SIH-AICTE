"""Database Seeding Script for AICTE-Verify.

Generates initial synthetic users, 6 institutions across regions, 18 sample applications
(6 institutions x 3 academic years: 2024-2025, 2025-2026, 2026-2027), sample PDF regulatory
artifacts, graph nodes for collusion detection, and mock issuer certificates.
ALL DATA IS STRICTLY SYNTHETIC AND ANONYMIZED. Marked SIMULATED.
"""

import hashlib
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import delete, select
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


async def seed_database(db: AsyncSession, wipe: bool = True) -> None:
    """Populate database with synthetic development records idempotently (wipe and reseed)."""
    if wipe:
        # Wipe in foreign key safe order
        for model in [
            Flag, ExtractedData, DocumentClassification, Document,
            ComplianceResult, VerificationResult, ApplicationHistory,
            Application, GraphRelation, GraphEntity, Institution,
            User
        ]:
            try:
                await db.execute(delete(model))
            except Exception:
                pass
        await db.commit()

    # 1. Create Default Users
    # Passwords: admin123, officer123, college123
    users_data = [
        {"username": "admin", "email": "admin@aicte.gov.in.simulated", "password": "admin123", "full_name": "AICTE Central Administrator", "role": "admin", "region": "Central", "institution_id": None},
        {"username": "officer1", "email": "officer.south@aicte.gov.in.simulated", "password": "officer123", "full_name": "Dr. V. Srinivasan (RO South)", "role": "officer", "region": "Southern", "institution_id": None},
        {"username": "officer2", "email": "officer.north@aicte.gov.in.simulated", "password": "officer123", "full_name": "Prof. R. K. Sharma (RO North)", "role": "officer", "region": "Northern", "institution_id": None},
        {"username": "college1", "email": "registrar@apextech.edu.simulated", "password": "college123", "full_name": "Registrar, Apex Tech", "role": "college_user", "region": "Southern", "institution_id": 1},
        {"username": "college2", "email": "dean@zenitheng.edu.simulated", "password": "college123", "full_name": "Dean Admin, Zenith Eng", "role": "college_user", "region": "Western", "institution_id": 2},
    ]

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
            "address": "88 Industrial Valley Road, Hinjawadi",
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
            "address": "12 Gomti Nagar Extension",
            "trust_name": "Awadh Welfare Educational Trust",
            "trust_registration_number": "TR-UP-2012-701",
            "campus_latitude": 26.8467,
            "campus_longitude": 80.9462,
            "established_year": 2012,
        },
        {
            "id": 4,
            "name": "Bengal Institute of Technology & Science",
            "code": "1-100456",
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

    # 3. Create Exactly 18 Applications (6 institutions x 3 academic years: 2024-2025, 2025-2026, 2026-2027)
    app_configs = [
        # Inst 1: Apex Tech (Chennai)
        {"id": 1, "inst_id": 1, "year": "2024-2025", "cat": "extension_of_approval", "status": "approved", "sub_date": date(2024, 4, 15), "risk": 14.0, "risk_lvl": "Low", "intake": 480, "curr": 480},
        {"id": 2, "inst_id": 1, "year": "2025-2026", "cat": "extension_of_approval", "status": "under_review", "sub_date": date(2025, 4, 10), "risk": 32.0, "risk_lvl": "Medium", "intake": 480, "curr": 480},
        {"id": 3, "inst_id": 1, "year": "2026-2027", "cat": "extension_of_approval", "status": "submitted", "sub_date": date(2026, 3, 1), "risk": 18.0, "risk_lvl": "Low", "intake": 480, "curr": 480},
        
        # Inst 2: Zenith Engg (Pune)
        {"id": 4, "inst_id": 2, "year": "2024-2025", "cat": "extension_of_approval", "status": "approved", "sub_date": date(2024, 4, 12), "risk": 22.0, "risk_lvl": "Low", "intake": 420, "curr": 420},
        {"id": 5, "inst_id": 2, "year": "2025-2026", "cat": "increase_of_intake", "status": "deficient", "sub_date": date(2025, 4, 10), "risk": 88.0, "risk_lvl": "High", "intake": 600, "curr": 420},
        {"id": 6, "inst_id": 2, "year": "2026-2027", "cat": "increase_of_intake", "status": "draft", "sub_date": date(2026, 2, 28), "risk": 35.0, "risk_lvl": "Medium", "intake": 540, "curr": 420},

        # Inst 3: Northern Poly (Lucknow)
        {"id": 7, "inst_id": 3, "year": "2024-2025", "cat": "extension_of_approval", "status": "approved", "sub_date": date(2024, 4, 20), "risk": 15.0, "risk_lvl": "Low", "intake": 360, "curr": 360},
        {"id": 8, "inst_id": 3, "year": "2025-2026", "cat": "extension_of_approval", "status": "under_review", "sub_date": date(2025, 4, 10), "risk": 72.0, "risk_lvl": "High", "intake": 360, "curr": 360},
        {"id": 9, "inst_id": 3, "year": "2026-2027", "cat": "extension_of_approval", "status": "submitted", "sub_date": date(2026, 3, 5), "risk": 20.0, "risk_lvl": "Low", "intake": 360, "curr": 360},

        # Inst 4: Bengal BITS (Kolkata)
        {"id": 10, "inst_id": 4, "year": "2024-2025", "cat": "introduction_of_new_course", "status": "approved", "sub_date": date(2024, 5, 2), "risk": 12.0, "risk_lvl": "Low", "intake": 300, "curr": 300},
        {"id": 11, "inst_id": 4, "year": "2025-2026", "cat": "introduction_of_new_course", "status": "under_review", "sub_date": date(2025, 4, 10), "risk": 28.0, "risk_lvl": "Low", "intake": 360, "curr": 300},
        {"id": 12, "inst_id": 4, "year": "2026-2027", "cat": "extension_of_approval", "status": "submitted", "sub_date": date(2026, 2, 25), "risk": 16.0, "risk_lvl": "Low", "intake": 360, "curr": 360},

        # Inst 5: Deccan Engg (Hyderabad)
        {"id": 13, "inst_id": 5, "year": "2024-2025", "cat": "extension_of_approval", "status": "approved", "sub_date": date(2024, 4, 18), "risk": 16.0, "risk_lvl": "Low", "intake": 480, "curr": 480},
        {"id": 14, "inst_id": 5, "year": "2025-2026", "cat": "extension_of_approval", "status": "under_review", "sub_date": date(2025, 4, 10), "risk": 38.0, "risk_lvl": "Medium", "intake": 480, "curr": 480},
        {"id": 15, "inst_id": 5, "year": "2026-2027", "cat": "extension_of_approval", "status": "submitted", "sub_date": date(2026, 3, 10), "risk": 22.0, "risk_lvl": "Low", "intake": 480, "curr": 480},

        # Inst 6: Central Valley (Bhopal)
        {"id": 16, "inst_id": 6, "year": "2024-2025", "cat": "extension_of_approval", "status": "approved", "sub_date": date(2024, 4, 25), "risk": 18.0, "risk_lvl": "Low", "intake": 300, "curr": 300},
        {"id": 17, "inst_id": 6, "year": "2025-2026", "cat": "extension_of_approval", "status": "deficient", "sub_date": date(2025, 4, 10), "risk": 84.0, "risk_lvl": "High", "intake": 420, "curr": 300},
        {"id": 18, "inst_id": 6, "year": "2026-2027", "cat": "extension_of_approval", "status": "submitted", "sub_date": date(2026, 2, 20), "risk": 25.0, "risk_lvl": "Low", "intake": 300, "curr": 300},
    ]

    for cfg in app_configs:
        app_obj = Application(
            id=cfg["id"],
            institution_id=cfg["inst_id"],
            category=cfg["cat"],
            academic_year=cfg["year"],
            status=cfg["status"],
            submission_date=cfg["sub_date"],
            submitted_by=4 if cfg["inst_id"] == 1 else 5,
            assigned_officer=2 if cfg["inst_id"] in [1, 5] else 3,
            risk_score=cfg["risk"],
            risk_level=cfg["risk_lvl"],
            intake_applied=cfg["intake"],
            current_intake=cfg["curr"],
        )
        db.add(app_obj)
    await db.commit()

    # 4. Generate Core Regulatory Documents for Key Operational Applications
    sample_docs_info = [
        {
            "application_id": 2,
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
            "application_id": 2,
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
            "application_id": 5,
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
        {
            "application_id": 5,
            "institution_id": 2,
            "document_type": "affidavit",
            "filename": "affidavit_zenith_mismatch.pdf",
            "title": "AFFIDAVIT ON STAMP PAPER",
            "lines": [
                "AFFIDAVIT ON STAMP PAPER",
                "I, Secretary of Zenith College of Engineering, solemnly affirm:",
                "Declared Student Intake for 2025-2026: 420 seats.",
                "Application form requested: 600 seats.",
                "Discrepancy noted between affidavit claim and intake expansion request.",
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

    # 5. Populate Extracted Data
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
        else:
            db.add(ExtractedData(document_id=doc_entry.id, field_name="institution_name", field_value="Zenith College of Engineering", confidence=0.98))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="certificate_number", field_value="CFD/2023/FS-1042-EXPIRED", confidence=0.95))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="issue_date", field_value="2023-01-10", confidence=0.94))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="expiry_date", field_value="2024-01-09", confidence=0.94))
            db.add(ExtractedData(document_id=doc_entry.id, field_name="intake", field_value="420", confidence=0.91))
    await db.commit()

    # 6. Seed Fresh Active Discrepancy Flags (Zero Resolved Flags)
    flags_to_seed = [
        # Zenith College (App 5) - High Risk
        Flag(
            application_id=5,
            document_id=created_docs[2][0].id,
            flag_type="validation",
            severity="high",
            code="VAL-DOC-EXPIRED",
            title="Fire Safety Certificate Expired",
            reason="Fire safety clearance certificate expired on 2024-01-09. Current valid certificate mandatory.",
            confidence=0.98,
            rule_id="DOC-EXPIRY-FIRE",
            check_name="Validity Window Check",
            is_resolved=False,
        ),
        Flag(
            application_id=5,
            document_id=created_docs[3][0].id,
            flag_type="validation",
            severity="high",
            code="VAL-INTAKE-MISMATCH",
            title="Intake Numerical Discrepancy",
            reason="Affidavit declares intake capacity of 420 seats, conflicting with expansion application request of 600 seats.",
            confidence=0.95,
            rule_id="INTAKE-AFFIDAVIT-CHECK",
            check_name="Intake Consistency Reconciliation",
            is_resolved=False,
        ),
        Flag(
            application_id=5,
            document_id=None,
            flag_type="compliance",
            severity="critical",
            code="COM-INTAKE-HIKE",
            title="Excessive Intake Increase Request",
            reason="Requested intake increase from 420 to 600 exceeds 50% annual regulatory ceiling.",
            confidence=1.0,
            rule_id="INTAKE-GROWTH-CAP",
            check_name="Intake Expansion Bounds Check",
            is_resolved=False,
        ),
        # Northern Poly (App 8) - Land and Faculty Collusion
        Flag(
            application_id=8,
            document_id=None,
            flag_type="anomaly",
            severity="critical",
            code="ANO-GHOST-FACULTY",
            title="Cross-Campus Ghost Faculty Collusion",
            reason="Professor Dr. Vikram Singh claimed as full-time regular faculty concurrently in Pune and Chennai.",
            confidence=0.97,
            rule_id="FACULTY-COLLUSION-GRAPH",
            check_name="Multi-Campus Ghost Faculty Graph Analyzer",
            is_resolved=False,
        ),
        Flag(
            application_id=8,
            document_id=None,
            flag_type="anomaly",
            severity="high",
            code="ANO-SHARED-LAND",
            title="Cross-Trust Land Survey Duplication",
            reason="Survey parcel #441/2 simultaneously registered to unrelated educational trusts in land title deeds.",
            confidence=0.94,
            rule_id="LAND-COLLUSION-GRAPH",
            check_name="Cross-Trust Land Survey Collusion Resolver",
            is_resolved=False,
        ),
    ]

    for fl in flags_to_seed:
        db.add(fl)
    await db.commit()

    # 7. Seed Knowledge Graph Entities & Collusion Relations
    nodes = [
        GraphEntity(id=1, entity_type="institution", entity_id="1-100234", name="Apex Institute of Technology", metadata_json=json.dumps({"city": "Chennai"})),
        GraphEntity(id=2, entity_type="institution", entity_id="1-100567", name="Zenith College of Engineering", metadata_json=json.dumps({"city": "Pune"})),
        GraphEntity(id=3, entity_type="institution", entity_id="1-100891", name="Northern Polytechnic Institute", metadata_json=json.dumps({"city": "Lucknow"})),
        GraphEntity(id=4, entity_type="faculty", entity_id="FAC011", name="Dr. Vikram Singh (Professor, CSE)", metadata_json=json.dumps({"pan": "ABCDE7741R", "specialization": "VLSI"})),
        GraphEntity(id=5, entity_type="land", entity_id="SURV-441-2", name="Survey Parcel #441/2 (12 Acres)", metadata_json=json.dumps({"survey_no": "441/2", "district": "Kanchipuram"})),
        GraphEntity(id=6, entity_type="trust", entity_id="TR-TN-2004-981", name="Sri Krishna Educational & Charitable Trust", metadata_json=json.dumps({"reg": "TR-TN-2004-981"})),
    ]
    for n in nodes:
        db.add(n)
    await db.commit()

    edges = [
        # Faculty duplication (flagged collusion across cities)
        GraphRelation(source_entity_id=4, target_entity_id=1, relation_type="employed_at", is_flagged=True, flag_reason="COLLUSION ANOMALY: Dual full-time faculty listing across institutions in Pune and Chennai simultaneously."),
        GraphRelation(source_entity_id=4, target_entity_id=2, relation_type="employed_at", is_flagged=True, flag_reason="COLLUSION ANOMALY: Dual full-time faculty listing across institutions in Pune and Chennai simultaneously."),
        # Land parcel duplication (flagged collusion across unrelated trusts)
        GraphRelation(source_entity_id=1, target_entity_id=5, relation_type="owns_land", is_flagged=True, flag_reason="COLLUSION ANOMALY: Land parcel Survey #441/2 concurrently claimed by unrelated educational trusts."),
        GraphRelation(source_entity_id=3, target_entity_id=5, relation_type="owns_land", is_flagged=True, flag_reason="COLLUSION ANOMALY: Land parcel Survey #441/2 concurrently claimed by unrelated educational trusts."),
        # Sponsoring trust governance links
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
        details={"status": "INITIALIZED", "system": "AICTE-Verify Backend Engine", "mode": "SIMULATED_PROTOTYPE", "seeded_applications": 18, "seeded_institutions": 6},
        rule_check="INTEGRITY_GENESIS_CHAIN_START",
    )
