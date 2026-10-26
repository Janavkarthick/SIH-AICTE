"""
Unit tests for Forensics Severities, Validation Fuzzy Matching,
Collusion Graph Sponsoring Trusts, and Deficiency Governance.
"""

import pytest
import pytest_asyncio
from datetime import date, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from app.core.database import Base
from app.services.forensics.service import ForensicsService
from app.services.validate.service import (
    normalize_institution_name,
    normalize_survey_number,
    are_field_values_equivalent,
)
from app.services.graph.service import GraphService
from app.services.letters.service import LetterService
from app.models.institution import Institution
from app.models.graph import GraphEntity, GraphRelation


@pytest_asyncio.fixture
async def in_memory_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        yield session

    await engine.dispose()


def create_test_pdf(filepath, producer, creator="AICTE Compliance"):
    c = canvas.Canvas(str(filepath), pagesize=A4)
    c.setTitle("Test Document")
    c.setProducer(producer)
    c.setCreator(creator)
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, "Statutory Compliance Test Document")
    c.save()


def test_forensics_compressor_vs_image_editor_severity(tmp_path):
    """Test that routine compressors are LOW severity/passed, while image editors trigger flagged."""
    forensics = ForensicsService()

    # 1. Test routine compressor
    compressor_pdf = tmp_path / "compressed.pdf"
    create_test_pdf(compressor_pdf, producer="iLovePDF Compression Service", creator="canva")

    findings = forensics.check_pdf_metadata(str(compressor_pdf))
    comp_finding = next((f for f in findings if f.check == "Editing Software Signature Detection"), None)
    assert comp_finding is not None
    assert comp_finding.passed is True
    assert comp_finding.severity == "low"
    assert "routine PDF compressor" in comp_finding.details

    # 2. Test Photoshop editor
    editor_pdf = tmp_path / "edited.pdf"
    create_test_pdf(editor_pdf, producer="Adobe Photoshop CC 2024 (Windows)", creator="Adobe Photoshop")

    findings = forensics.check_pdf_metadata(str(editor_pdf))
    edit_finding = next((f for f in findings if f.check == "Editing Software Signature Detection"), None)
    assert edit_finding is not None
    assert edit_finding.passed is False
    assert edit_finding.status == "flagged"
    assert "photoshop" in edit_finding.details.lower()


def test_unsigned_scan_severity(tmp_path):
    """Test that unsigned standard Indian scans are INFO and passed=True."""
    forensics = ForensicsService()
    unsigned_pdf = tmp_path / "unsigned_scan.pdf"
    create_test_pdf(unsigned_pdf, producer="ReportLab PDF Library")

    findings = forensics.verify_digital_signature(str(unsigned_pdf))
    sig_finding = findings[0]
    assert sig_finding.passed is True
    assert sig_finding.status == "passed"
    assert sig_finding.severity == "info"
    assert "unsigned scan" in sig_finding.details.lower()


def test_fuzzy_name_and_survey_normalization():
    """Test resilient matching on '&' vs 'and', abbreviations, and survey numbers."""
    name1 = "Apex College of Engg. & Technology"
    name2 = "Apex College of Engineering and Technology"
    assert are_field_values_equivalent("institution_name", name1, name2) is True

    # Survey number variations
    surv1 = "Plot No. 12/3-A"
    surv2 = "Sy No. 12 / 3A"
    assert normalize_survey_number(surv1) == normalize_survey_number(surv2)
    assert are_field_values_equivalent("survey_number", surv1, surv2) is True


@pytest.mark.asyncio
async def test_sister_campuses_not_flagged_as_collusion(in_memory_db):
    """Test that institutions under the same sponsoring trust are recognized as sister campuses, not collusion."""
    # 1. Seed Institutions
    inst1 = Institution(id=1, name="Rajiv Gandhi Inst of Tech", code="1-101", city="Pune", state="Maharashtra", region="Western", address="Pune Rd", trust_name="Rajiv Education Trust", trust_registration_number="TR-MH-01")
    inst6 = Institution(id=6, name="Savitribai Phule Poly", code="1-106", city="Pune", state="Maharashtra", region="Western", address="Nagpur Rd", trust_name="Rajiv Education Trust", trust_registration_number="TR-MH-01")
    inst2 = Institution(id=2, name="Apex Engineering", code="1-102", city="Chennai", state="Tamil Nadu", region="Southern", address="OMR", trust_name="Different Foundation", trust_registration_number="TR-TN-02")
    in_memory_db.add_all([inst1, inst6, inst2])

    # 2. Seed Graph Entities
    e1 = GraphEntity(id=1, entity_type="institution", entity_id="1-101", name="Rajiv Gandhi Inst of Tech", metadata_json="{}")
    e6 = GraphEntity(id=2, entity_type="institution", entity_id="1-106", name="Savitribai Phule Poly", metadata_json="{}")
    e2 = GraphEntity(id=3, entity_type="institution", entity_id="1-102", name="Apex Engineering", metadata_json="{}")
    e_land_same = GraphEntity(id=4, entity_type="land", entity_id="12/3A", name="Survey 12/3A", metadata_json="{}")
    e_land_diff = GraphEntity(id=5, entity_type="land", entity_id="99/1B", name="Survey 99/1B", metadata_json="{}")
    in_memory_db.add_all([e1, e6, e2, e_land_same, e_land_diff])

    # 3. Seed Relations
    # Sister campus land parcel under same trust (inst1 and inst6)
    r1 = GraphRelation(id=1, source_entity_id=1, target_entity_id=4, relation_type="owns_land", is_flagged=False)
    r2 = GraphRelation(id=2, source_entity_id=2, target_entity_id=4, relation_type="owns_land", is_flagged=False)
    # Collusion land parcel across unrelated trusts (inst1 and inst2)
    r3 = GraphRelation(id=3, source_entity_id=1, target_entity_id=5, relation_type="owns_land", is_flagged=False)
    r4 = GraphRelation(id=4, source_entity_id=3, target_entity_id=5, relation_type="owns_land", is_flagged=False)
    in_memory_db.add_all([r1, r2, r3, r4])
    await in_memory_db.commit()

    # 4. Run detection
    graph_service = GraphService()
    flagged_count = await graph_service.detect_anomalies_and_flag(in_memory_db)

    # 5. Verify results from DB
    res_rels = (await in_memory_db.execute(select(GraphRelation))).scalars().all()
    rel_map = {r.id: r for r in res_rels}

    # Sister campus land parcel (r1, r2) must NOT be flagged
    assert rel_map[1].is_flagged is False
    assert "SHARED SPONSOR" in (rel_map[1].flag_reason or "")

    # Unrelated trust land parcel (r3, r4) MUST be flagged
    assert rel_map[3].is_flagged is True
    assert "CRITICAL LAND COLLUSION" in (rel_map[3].flag_reason or "")


def test_deficiency_notice_draft_clauses():
    """Test that deficiency notices are marked as DRAFT with statutory clause placeholders."""
    letter_service = LetterService()

    app_mock = MagicMock()
    app_mock.id = 101
    app_mock.academic_year = "2025-2026"
    app_mock.category = "extension_of_approval"

    inst_mock = MagicMock()
    inst_mock.name = "Apex Institute of Technology"
    inst_mock.address = "45 Knowledge Park"
    inst_mock.city = "Chennai"
    inst_mock.state = "Tamil Nadu"
    inst_mock.code = "1-100234"

    flag_mock = MagicMock()
    flag_mock.code = "VAL-DOC-EXPIRED"
    flag_mock.severity = "high"
    flag_mock.flag_type = "document_expired"
    flag_mock.title = "Fire Safety Certificate Expired"
    flag_mock.reason = "Fire safety certificate expired prior to application submission date."

    res = letter_service.generate_deficiency_letter(
        application=app_mock,
        institution=inst_mock,
        open_flags=[flag_mock],
        language="eng",
    )
    assert "*** DRAFT DEFICIENCY NOTICE" in res.content
    assert "[Clause reference - verify against Approval Process Handbook]" in res.content
    assert "PENDING REGIONAL OFFICER SCRUTINY" in res.content
    assert "Final decision rests with the competent authority" in res.content
    assert res.status == "draft"


@pytest.mark.asyncio
async def test_same_trust_faculty_duplication_across_cities_flagged(in_memory_db):
    """Test (a): Faculty member claimed full-time at two institutions in different cities

    under the SAME trust is strictly flagged as CRITICAL GHOST FACULTY.
    Sister campuses may share land (SHARED SPONSOR), but NOT full-time faculty.
    """
    # 1. Two institutions under the SAME trust in DIFFERENT cities
    inst1 = Institution(
        id=10,
        name="Shree Ram College of Engineering",
        code="1-901",
        city="Pune",
        state="Maharashtra",
        region="Western",
        address="100 Station Road, Pune",
        trust_name="Shree Ram Educational Trust",
        trust_registration_number="TR-SHREE-01",
    )
    inst2 = Institution(
        id=20,
        name="Shree Ram Institute of Technology",
        code="1-902",
        city="Nagpur",
        state="Maharashtra",
        region="Western",
        address="45 Hingna Road, Nagpur",
        trust_name="Shree Ram Educational Trust",
        trust_registration_number="TR-SHREE-01",
    )
    in_memory_db.add_all([inst1, inst2])

    # 2. Graph entities
    e_inst1 = GraphEntity(id=10, entity_type="institution", entity_id="1-901", name="Shree Ram College", metadata_json="{}")
    e_inst2 = GraphEntity(id=20, entity_type="institution", entity_id="1-902", name="Shree Ram Institute", metadata_json="{}")
    e_faculty = GraphEntity(id=30, entity_type="faculty", entity_id="FAC_RAM_01", name="Dr. A. K. Sharma", metadata_json="{}")
    e_land = GraphEntity(id=40, entity_type="land", entity_id="77/A", name="Survey 77/A", metadata_json="{}")
    in_memory_db.add_all([e_inst1, e_inst2, e_faculty, e_land])

    # 3. Relations: Both claim the same faculty full-time, and both share a land parcel
    r_fac1 = GraphRelation(id=101, source_entity_id=30, target_entity_id=10, relation_type="employed_at", is_flagged=False)
    r_fac2 = GraphRelation(id=102, source_entity_id=30, target_entity_id=20, relation_type="employed_at", is_flagged=False)
    r_land1 = GraphRelation(id=103, source_entity_id=10, target_entity_id=40, relation_type="owns_land", is_flagged=False)
    r_land2 = GraphRelation(id=104, source_entity_id=20, target_entity_id=40, relation_type="owns_land", is_flagged=False)
    in_memory_db.add_all([r_fac1, r_fac2, r_land1, r_land2])
    await in_memory_db.commit()

    # 4. Run Graph Collusion Detection
    graph_service = GraphService()
    await graph_service.detect_anomalies_and_flag(in_memory_db)

    # 5. Fetch relations from DB
    res_rels = (await in_memory_db.execute(select(GraphRelation))).scalars().all()
    rel_map = {r.id: r for r in res_rels}

    # Faculty duplication across cities MUST be flagged CRITICAL GHOST FACULTY
    assert rel_map[101].is_flagged is True
    assert "CRITICAL GHOST FACULTY" in rel_map[101].flag_reason
    assert "different cities" in rel_map[101].flag_reason.lower()

    # Land sharing under the same trust MUST be marked legitimate SHARED SPONSOR (not flagged)
    assert rel_map[103].is_flagged is False
    assert "SHARED SPONSOR" in rel_map[103].flag_reason


@pytest.mark.asyncio
async def test_submission_date_used_never_created_at_for_expiry(in_memory_db):
    """Test (b): Expiry checking strictly uses application.submission_date,

    never created_at or DB insert timestamp.
    """
    from datetime import datetime, timezone
    from app.services.validate.service import ValidationService
    from app.models.application import Application
    from app.models.document import Document, ExtractedData

    # Inst
    inst = Institution(
        id=50, name="Apex Engg", code="1-501", city="Chennai",
        state="TN", region="Southern", address="OMR",
        trust_name="Apex Trust", trust_registration_number="TR-50",
    )
    in_memory_db.add(inst)

    # Application where created_at is 2025-01-01 (DB insert time),
    # but actual submission_date is 2025-04-10
    app = Application(
        id=50,
        institution_id=50,
        category="extension_of_approval",
        academic_year="2025-2026",
        status="under_review",
        submission_date=date(2025, 4, 10),
        created_at=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
    )
    in_memory_db.add(app)

    # Document expiring on 2025-02-15
    # Relative to created_at (2025-01-01): it would be VALID (future).
    # Relative to submission_date (2025-04-10): it is EXPIRED (54 days past, exceeds 30-day grace).
    doc = Document(
        id=501,
        application_id=50,
        institution_id=50,
        document_type="fire_safety_certificate",
        filename="fire_cert.pdf",
        original_filename="fire_cert.pdf",
        file_path="/dummy/fire_cert.pdf",
        file_hash_sha256="dummyhash123",
        status="verified",
    )
    ext_issue = ExtractedData(
        id=501,
        document_id=501,
        field_name="issue_date",
        field_value="2024-02-15",
    )
    ext_expiry = ExtractedData(
        id=502,
        document_id=501,
        field_name="expiry_date",
        field_value="2025-02-15",
    )
    in_memory_db.add_all([doc, ext_issue, ext_expiry])
    await in_memory_db.commit()

    val_service = ValidationService()
    report = await val_service.validate_application(in_memory_db, application_id=50, persist_flags=False)

    # Must find VAL-DOC-EXPIRED flag
    expiry_flags = [f for f in report.flags if f.code == "VAL-DOC-EXPIRED"]
    assert len(expiry_flags) == 1, "Document expiring on 2025-02-15 must be flagged expired against submission_date 2025-04-10"
    assert "2025-04-10" in expiry_flags[0].reason
    assert "submission date 2025-04-10" in expiry_flags[0].reason


def test_font_check_returns_not_run_when_pymupdf_missing(tmp_path, monkeypatch):
    """Test (c): When PyMuPDF is unavailable, font consistency check reports

    status='not_run', passed=False (never passed=True), with clear reason.
    """
    import app.services.forensics.service as fmod
    monkeypatch.setattr(fmod, "HAS_FITZ", False)
    monkeypatch.setattr(fmod, "fitz", None)

    forensics = ForensicsService()
    test_pdf = tmp_path / "sample.pdf"
    create_test_pdf(test_pdf, producer="Sample PDF Producer")

    findings = forensics.check_font_consistency(str(test_pdf))
    assert len(findings) == 1
    finding = findings[0]

    assert finding.status == "not_run"
    assert finding.passed is False, "Must NEVER report passed=True when check was not run"
    assert "PyMuPDF library unavailable" in finding.reason

