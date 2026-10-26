"""
AICTE-Verify Synthetic Benchmark Dataset Generator
===================================================
SIMULATED DATA ONLY - All institutions, persons, and documents are fictional.

Generates realistic PDFs and images with neutral filenames (DOC_0001.pdf, DOC_0002.jpg, ...)
to evaluate pipeline heuristics without data leakage or filename hints.
Planted faults: 10 randomised variants across 16 fault categories (160 planted faults).
Clean controls: 125 clean documents across all 11 statutory categories.
Total benchmark dataset: 285 neutral documents.
"""

import json
import os
import random
import shutil
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from io import BytesIO
from typing import Any, Dict, List, Tuple

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch, cm
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import black, red, blue, gray, white, HexColor
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("WARNING: reportlab not installed.")

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("WARNING: Pillow not installed.")

try:
    import piexif
    HAS_PIEXIF = True
except ImportError:
    HAS_PIEXIF = False

try:
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False

# ─── Configuration ───────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "synthetic"
DOCS_DIR = OUTPUT_DIR / "documents"
PHOTOS_DIR = OUTPUT_DIR / "photos"
GROUND_TRUTH_PATH = OUTPUT_DIR / "ground_truth.json"

# 12 fictional institutions across India (North, South, East, West, Central)
INSTITUTIONS = [
    {
        "id": "INST001",
        "name": "Rajiv Gandhi Institute of Technology",
        "code": "1-100101",
        "city": "Pune",
        "state": "Maharashtra",
        "region": "Western",
        "address": "123 Engineering Highway, Hinjawadi",
        "trust_name": "Rajiv Education Trust",
        "trust_reg_no": "TR-MH-2005-1234",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "established_year": 2005,
    },
    {
        "id": "INST002",
        "name": "Sri Lakshmi Engineering College",
        "code": "1-100202",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "region": "Southern",
        "address": "456 Knowledge Avenue, OMR Highway",
        "trust_name": "Lakshmi Educational Foundation",
        "trust_reg_no": "TR-TN-2008-5678",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "established_year": 2008,
    },
    {
        "id": "INST003",
        "name": "Bharati Vidyapeeth College of Engineering",
        "code": "1-100303",
        "city": "Bangalore",
        "state": "Karnataka",
        "region": "Southern",
        "address": "789 Electronic City Ring Road",
        "trust_name": "Bharati Education Society",
        "trust_reg_no": "TR-KA-2003-9012",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "established_year": 2003,
    },
    {
        "id": "INST004",
        "name": "Netaji Subhas Institute of Technology",
        "code": "1-100404",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "region": "Northern",
        "address": "101 Vidhan Sabha Marg",
        "trust_name": "Subhas Memorial Trust",
        "trust_reg_no": "TR-UP-2010-3456",
        "latitude": 26.8467,
        "longitude": 80.9462,
        "established_year": 2010,
    },
    {
        "id": "INST005",
        "name": "Kalam Technical University College",
        "code": "1-100505",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "region": "Southern",
        "address": "202 Innovation Corridor",
        "trust_name": "Lakshmi Educational Foundation",  # Sister college of INST002!
        "trust_reg_no": "TR-TN-2008-5678",
        "latitude": 11.0168,
        "longitude": 76.9558,
        "established_year": 2012,
    },
    {
        "id": "INST006",
        "name": "Savitribai Phule Polytechnic",
        "code": "1-100606",
        "city": "Nagpur",
        "state": "Maharashtra",
        "region": "Western",
        "address": "303 Education Park, Wardha Road",
        "trust_name": "Rajiv Education Trust",  # Sister college of INST001!
        "trust_reg_no": "TR-MH-2005-1234",
        "latitude": 21.1458,
        "longitude": 79.0882,
        "established_year": 2007,
    },
    {
        "id": "INST007",
        "name": "Jadavpur Institute of Technology",
        "code": "1-100707",
        "city": "Kolkata",
        "state": "West Bengal",
        "region": "Eastern",
        "address": "88 Salt Lake Sector V",
        "trust_name": "Tagore Educational Trust",
        "trust_reg_no": "TR-WB-2001-1122",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "established_year": 2001,
    },
    {
        "id": "INST008",
        "name": "Malaviya Engineering Institute",
        "code": "1-100808",
        "city": "Jaipur",
        "state": "Rajasthan",
        "region": "Northern",
        "address": "55 JLN Marg, Malviya Nagar",
        "trust_name": "Malaviya Foundation",
        "trust_reg_no": "TR-RJ-2006-3344",
        "latitude": 26.9124,
        "longitude": 75.7873,
        "established_year": 2006,
    },
    {
        "id": "INST009",
        "name": "Visvesvaraya Technical Campus",
        "code": "1-100909",
        "city": "Hyderabad",
        "state": "Telangana",
        "region": "South-Central",
        "address": "90 Gachibowli Tech Enclave",
        "trust_name": "Deccan Shiksha Samiti",
        "trust_reg_no": "TR-TS-2011-5566",
        "latitude": 17.3850,
        "longitude": 78.4867,
        "established_year": 2011,
    },
    {
        "id": "INST010",
        "name": "Aryabhata College of Engineering",
        "code": "1-101010",
        "city": "Patna",
        "state": "Bihar",
        "region": "Eastern",
        "address": "14 Bailey Road",
        "trust_name": "Aryabhata Research Society",
        "trust_reg_no": "TR-BR-2014-7788",
        "latitude": 25.5941,
        "longitude": 85.1376,
        "established_year": 2014,
    },
    {
        "id": "INST011",
        "name": "Sardar Patel Institute of Technology",
        "code": "1-101111",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "region": "Western",
        "address": "77 Ashram Road",
        "trust_name": "Sardar Patel Vidyapeeth",
        "trust_reg_no": "TR-GJ-2004-9900",
        "latitude": 23.0225,
        "longitude": 72.5714,
        "established_year": 2004,
    },
    {
        "id": "INST012",
        "name": "Chanakya Technical Institute",
        "code": "1-101212",
        "city": "Bhopal",
        "state": "Madhya Pradesh",
        "region": "Central",
        "address": "32 Hoshangabad Road",
        "trust_name": "Central Bharat Trust",
        "trust_reg_no": "TR-MP-2009-2233",
        "latitude": 23.2599,
        "longitude": 77.4126,
        "established_year": 2009,
    },
]

MOCK_ISSUER_REGISTRY: List[Dict[str, Any]] = []

GROUND_TRUTH: Dict[str, Any] = {
    "_meta": {
        "description": "AICTE-Verify Synthetic Benchmark Ground Truth",
        "simulated": True,
        "neutral_filenames": True,
        "naming_scheme": "DOC_0001.pdf / DOC_XXXX.jpg (no semantic hints in filenames)",
        "generated_at": None,
    },
    "planted_faults": [],
    "clean_documents": [],
    "institutions": INSTITUTIONS,
    "applications": [],
    "verification_statuses": [],
}

doc_counter = 0

def get_next_neutral_filename(is_photo: bool = False) -> Tuple[str, Path]:
    """Generate a strictly neutral filename with NO keyword hints (DOC_0001.pdf or DOC_0001.jpg)."""
    global doc_counter
    doc_counter += 1
    ext = ".jpg" if is_photo else ".pdf"
    filename = f"DOC_{doc_counter:04d}{ext}"
    target_dir = PHOTOS_DIR if is_photo else DOCS_DIR
    return filename, target_dir / filename


def ensure_dirs():
    """Clean and initialize synthetic output directories."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    if PHOTOS_DIR.exists():
        shutil.rmtree(PHOTOS_DIR)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)


def register_issuer_entry(doc_type: str, ref_number: str, institution_id: str,
                          issuer_name: str, issue_date: str, expiry_date: str | None,
                          status: str = "verified", payload: dict | None = None):
    entry = {
        "doc_type": doc_type,
        "ref_number": ref_number,
        "institution_id": institution_id,
        "issuer_name": issuer_name,
        "issue_date": issue_date,
        "expiry_date": expiry_date,
        "status": status,
        "payload": payload or {},
    }
    MOCK_ISSUER_REGISTRY.append(entry)
    return entry


def create_simple_pdf(filepath: Path, title: str, body_lines: List[str],
                      qr_data: str | None = None,
                      producer: str = "ReportLab PDF Library v3.6.12",
                      creator: str = "AICTE-Verify Statutory Regulatory System",
                      tamper_font: bool = False,
                      add_extra_eof: bool = False) -> str:
    """Generate a clean vector PDF with controlled metadata and typography."""
    if not HAS_REPORTLAB:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"%PDF-1.4\n%{title}\n")
            for line in body_lines:
                f.write(line + "\n")
            f.write("%%EOF\n")
        return str(filepath)

    c = canvas.Canvas(str(filepath), pagesize=A4)
    width, height = A4

    c.setTitle(title)
    c.setAuthor("AICTE Regulatory Authority (SIMULATED)")
    c.setProducer(producer)
    c.setCreator(creator)

    # Document Header
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(width / 2, height - 50, title)

    y = height - 90
    for line in body_lines:
        if y < 80:
            c.showPage()
            y = height - 50

        if tamper_font and ("Date:" in line or "Reference" in line or "Intake:" in line or "Survey" in line):
            # Spliced Courier font into Helvetica layout across multiple lines
            c.setFont("Courier", 11)
            c.drawString(72, y, line)
            c.setFont("Helvetica", 10)
        else:
            c.setFont("Helvetica", 10)
            c.drawString(72, y, line)
        y -= 17

    if qr_data and HAS_QR and HAS_PIL:
        qr = qrcode.QRCode(version=1, box_size=3, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").get_image()
        qr_path = str(filepath) + ".qr.png"
        qr_img.save(qr_path)
        c.drawImage(qr_path, width - 180, 50, width=90, height=90)
        try:
            os.remove(qr_path)
        except OSError:
            pass

    c.save()

    if add_extra_eof:
        with open(filepath, 'ab') as f:
            f.write(b"\n%%EOF\n%%EOF\n%%EOF\n")

    return str(filepath)


def create_infrastructure_photo(filepath: Path, inst: dict,
                                 wrong_gps: bool = False,
                                 old_date: bool = False,
                                 is_blurry: bool = False) -> str:
    """Generate an infrastructure photo asset with EXIF geotags."""
    if not HAS_PIL:
        with open(filepath, 'wb') as f:
            f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xFF\xDB')
        return str(filepath)

    width, height = 1280, 960
    img = Image.new('RGB', (width, height), color=(220, 230, 245))
    draw = ImageDraw.Draw(img)

    # Campus building blocks
    draw.rectangle([100, 250, 550, 750], fill=(180, 185, 195), outline=(90, 95, 105), width=4)
    for wy in range(300, 650, 80):
        for wx in range(140, 500, 90):
            draw.rectangle([wx, wy, wx + 60, wy + 50], fill=(135, 206, 250), outline=(60, 60, 60))
    draw.rectangle([280, 620, 370, 750], fill=(110, 65, 30))  # Main entrance

    draw.rectangle([600, 350, 1150, 750], fill=(190, 195, 205), outline=(90, 95, 105), width=4)
    for wy in range(400, 680, 90):
        for wx in range(650, 1100, 110):
            draw.rectangle([wx, wy, wx + 75, wy + 55], fill=(135, 206, 250), outline=(60, 60, 60))

    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except (IOError, OSError):
        font = ImageFont.load_default()

    draw.text((120, 800), f"Campus Infrastructure - {inst['name']} ({inst['city']})", fill=(40, 40, 40), font=font)
    draw.text((120, 840), "SIMULATED COMPLIANCE PHOTO - STATUTORY BENCHMARK", fill=(180, 40, 40), font=font)

    if is_blurry:
        img = img.filter(ImageFilter.GaussianBlur(radius=14))

    img.save(str(filepath), "JPEG", quality=85)

    if HAS_PIEXIF:
        lat = inst["latitude"]
        lng = inst["longitude"]
        if wrong_gps:
            # Shift 500km away
            lat += 5.5
            lng += 5.5

        def to_deg(val):
            val = abs(val)
            d = int(val)
            m = int((val - d) * 60)
            s = int(((val - d) * 60 - m) * 60 * 100)
            return ((d, 1), (m, 1), (s, 100))

        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: b'N' if lat >= 0 else b'S',
            piexif.GPSIFD.GPSLatitude: to_deg(lat),
            piexif.GPSIFD.GPSLongitudeRef: b'E' if lng >= 0 else b'W',
            piexif.GPSIFD.GPSLongitude: to_deg(lng),
        }

        if old_date:
            date_str = "2023:01:10 10:00:00"
        else:
            date_str = datetime.now().strftime("%Y:%m:%d %H:%M:%S")

        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: date_str.encode(),
            piexif.ExifIFD.DateTimeDigitized: date_str.encode(),
        }
        zeroth_ifd = {
            piexif.ImageIFD.Make: b"Canon (SIMULATED)",
            piexif.ImageIFD.Model: b"EOS AICTE Compliance",
            piexif.ImageIFD.DateTime: date_str.encode(),
        }
        try:
            exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd}
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, str(filepath))
        except Exception:
            pass

    return str(filepath)


# ─── Generator Suite ─────────────────────────────────────────────────────────

def generate_benchmark_suite():
    global doc_counter
    doc_counter = 0
    ensure_dirs()
    print("=" * 65)
    print("AICTE-Verify Benchmark Generator (DOC_0001..DOC_XXXX Neutral IDs)")
    print("=" * 65)

    applications = []
    created_docs: List[Dict[str, Any]] = []

    # Map institutions to land survey numbers
    land_surveys = {
        inst["id"]: f"{inst['state'][:2]}/{inst['city'][:3].upper()}/SUR/2010/{100 + idx}"
        for idx, inst in enumerate(INSTITUTIONS)
    }

    # 1. GENERATE 125 CLEAN STATUTORY DOCUMENTS (CONTROLS)
    print("Generating 125 clean statutory control documents...")
    doc_types = [
        "affidavit", "fire_safety_certificate", "noc", "accreditation_certificate",
        "land_document", "university_affiliation_letter", "faculty_list",
        "electricity_bill", "infrastructure_photo", "noc_tamil", "noc_hindi"
    ]

    for i in range(125):
        inst = INSTITUTIONS[i % len(INSTITUTIONS)]
        year = "2025"
        app_id = f"APP_CLEAN_{(i // len(INSTITUTIONS)) + 1:03d}_{inst['id']}"
        dtype = doc_types[i % len(doc_types)]
        is_photo = (dtype == "infrastructure_photo")
        fname, fpath = get_next_neutral_filename(is_photo=is_photo)

        ref_no = f"REG/{inst['state'][:2]}/{year}/{5000 + i}"
        issue_d = f"10-04-{year}"
        expiry_d = f"09-04-{int(year) + 2}"

        if dtype == "infrastructure_photo":
            create_infrastructure_photo(fpath, inst)
        elif dtype == "affidavit":
            lines = [
                "AFFIDAVIT ON NON-JUDICIAL STAMP PAPER",
                "=" * 50,
                f"Reference: {ref_no}",
                f"Date: {issue_d}",
                f"I, the authorized signatory of {inst['name']} (PID: {inst['code']}),",
                f"located at {inst['address']}, solemnly affirm and state:",
                "1. That our institution complies with all AICTE Approval Process Norms.",
                f"2. That the approved intake for Academic Year {year}-{int(year)+1} is 360 seats.",
                f"3. Sponsoring Trust: {inst['trust_name']} (Reg: {inst['trust_reg_no']}).",
                "Deponent Signature & Notary Seal",
            ]
            qr_data = json.dumps({"ref": ref_no, "inst": inst["code"], "type": "affidavit"})
            create_simple_pdf(fpath, "AFFIDAVIT", lines, qr_data=qr_data)
            register_issuer_entry("affidavit", ref_no, inst["id"], "Notary Public", issue_d, None)
        elif dtype == "fire_safety_certificate":
            lines = [
                "STATE FIRE & RESCUE SERVICES DEPARTMENT",
                "=" * 50,
                "FIRE SAFETY CLEARANCE CERTIFICATE",
                f"Certificate No: {ref_no}",
                f"Date of Issue: {issue_d}",
                f"Valid Until: {expiry_d}",
                f"This certifies that {inst['name']} premises at {inst['address']}",
                "have been thoroughly inspected and equipped with required fire safety mechanisms.",
                f"Issued by: Chief Fire Officer, {inst['city']}",
            ]
            qr_data = json.dumps({"ref": ref_no, "inst": inst["code"], "type": "fire_safety"})
            create_simple_pdf(fpath, "FIRE SAFETY CERTIFICATE", lines, qr_data=qr_data)
            register_issuer_entry("fire_safety_certificate", ref_no, inst["id"], f"Fire Dept {inst['city']}", issue_d, expiry_d)
        elif dtype == "noc":
            lines = [
                f"GOVERNMENT OF {inst['state'].upper()}",
                "DEPARTMENT OF HIGHER & TECHNICAL EDUCATION",
                "=" * 50,
                "NO OBJECTION CERTIFICATE (NOC)",
                f"Reference No: {ref_no}",
                f"Date: {issue_d}",
                f"Valid Until: {expiry_d}",
                f"The State Government grants No Objection for continuation of {inst['name']} ({inst['code']}).",
                "Secretary to Government, Higher Education",
            ]
            qr_data = json.dumps({"ref": ref_no, "inst": inst["code"], "type": "noc"})
            create_simple_pdf(fpath, "NO OBJECTION CERTIFICATE", lines, qr_data=qr_data)
            register_issuer_entry("noc", ref_no, inst["id"], f"Dept of Higher Education {inst['state']}", issue_d, expiry_d)
        elif dtype == "accreditation_certificate":
            lines = [
                "NATIONAL BOARD OF ACCREDITATION",
                "=" * 50,
                "CERTIFICATE OF ACCREDITATION",
                f"Accreditation Ref: {ref_no}",
                f"Date of Award: {issue_d}",
                f"Valid Until: {expiry_d}",
                f"This is to certify that programs at {inst['name']} ({inst['code']})",
                "have been evaluated and accredited with Grade A.",
                "Member Secretary, NBA",
            ]
            qr_data = json.dumps({"ref": ref_no, "inst": inst["code"], "type": "accreditation_certificate"})
            create_simple_pdf(fpath, "ACCREDITATION CERTIFICATE", lines, qr_data=qr_data)
            register_issuer_entry("accreditation_certificate", ref_no, inst["id"], "National Board of Accreditation", issue_d, expiry_d)
        elif dtype == "land_document":
            sno = land_surveys[inst["id"]]
            lines = [
                "LAND OWNERSHIP AND REGISTRATION DEED",
                "=" * 50,
                f"Title Deed No: {ref_no}",
                f"Survey No: {sno}",
                f"Total Land Area: 12.50 Acres",
                f"Registered in the name of: {inst['trust_name']}",
                f"For educational campus of: {inst['name']}",
                f"Sub-Registrar Office, {inst['city']}",
            ]
            create_simple_pdf(fpath, "LAND OWNERSHIP DOCUMENT", lines)
        elif dtype == "university_affiliation_letter":
            lines = [
                f"STATE TECHNICAL UNIVERSITY, {inst['state'].upper()}",
                "=" * 50,
                "CONTINUATION OF AFFILIATION ORDER",
                f"Affiliation Order No: {ref_no}",
                f"Date: {issue_d}",
                f"Valid Until: {expiry_d}",
                f"Affiliation is granted to {inst['name']} ({inst['code']}) for 2025-2026.",
                "Registrar, State Technical University",
            ]
            qr_data = json.dumps({"ref": ref_no, "inst": inst["code"], "type": "university_affiliation_letter"})
            create_simple_pdf(fpath, "UNIVERSITY AFFILIATION LETTER", lines, qr_data=qr_data)
            register_issuer_entry("university_affiliation_letter", ref_no, inst["id"], "State Technical University", issue_d, expiry_d)
        elif dtype == "faculty_list":
            lines = [
                f"FACULTY LIST AND TEACHING STAFF ROSTER",
                f"Institution: {inst['name']} (PID: {inst['code']})",
                "=" * 50,
                "S.No | Faculty ID | Name | Qualification | Designation",
                f"1 | FAC_{inst['id']}_01 | Dr. R. Sharma | PhD CSE | Professor",
                f"2 | FAC_{inst['id']}_02 | Dr. P. Verma | PhD ECE | Associate Professor",
                f"3 | FAC_{inst['id']}_03 | Prof. S. Rao | MTech ME | Assistant Professor",
                f"4 | FAC_{inst['id']}_04 | Dr. A. Gupta | PhD Civil | Professor",
                "Principal & Head of Institution",
            ]
            create_simple_pdf(fpath, "FACULTY LIST", lines)
        elif dtype == "electricity_bill":
            lines = [
                f"STATE POWER DISTRIBUTION COMPANY",
                "=" * 50,
                "ELECTRICITY CONSUMPTION BILL",
                f"Consumer Number: 778899{i}",
                f"Bill Number: {ref_no}",
                f"Billing Month: March {year}",
                f"Consumer: {inst['trust_name']} ({inst['name']})",
                "Units Consumed: 14,200 kWh",
                "Current Tariff: Commercial Educational HT-2",
            ]
            create_simple_pdf(fpath, "ELECTRICITY BILL", lines)
        elif dtype == "noc_tamil":
            lines = [
                "தமிழ்நாடு அரசு - உயர் கல்வித் துறை",
                "=" * 50,
                "தடையில்லாச் சான்றிதழ் (NO OBJECTION CERTIFICATE)",
                f"சான்றிதழ் எண் / Ref: {ref_no}",
                f"நிறுவனம்: {inst['name']}",
                "அரசு செயலாளர், தொழில்நுட்பக் கல்வித் துறை",
            ]
            create_simple_pdf(fpath, "NO OBJECTION CERTIFICATE (TAMIL)", lines)
            register_issuer_entry("noc", ref_no, inst["id"], "Tamil Nadu DOTE", issue_d, expiry_d)
        elif dtype == "noc_hindi":
            lines = [
                "उत्तर प्रदेश शासन - प्राविधिक शिक्षा विभाग",
                "=" * 50,
                "अनापत्ति प्रमाण पत्र (NO OBJECTION CERTIFICATE)",
                f"पत्रांक संख्या / Ref: {ref_no}",
                f"संस्थान: {inst['name']}",
                "विशेष सचिव, प्राविधिक शिक्षा",
            ]
            create_simple_pdf(fpath, "NO OBJECTION CERTIFICATE (HINDI)", lines)
            register_issuer_entry("noc", ref_no, inst["id"], "UP Technical Education", issue_d, expiry_d)

        GROUND_TRUTH["clean_documents"].append({
            "document": fname,
            "document_type": dtype,
            "institution_id": inst["id"],
            "application_id": app_id,
        })

    # 2. GENERATE 160 PLANTED FAULTS (EXACTLY 10 PER FAULT CATEGORY)
    print("Generating 160 planted fault test documents (10 variants x 16 fault categories)...")

    # (1) name_mismatch (10 variants)
    for v in range(10):
        inst = INSTITUTIONS[v]
        fname, fpath = get_next_neutral_filename(is_photo=False)
        mismatched_name = inst["name"].replace("Engineering", "Polytechnic").replace("Institute", "Global Academy")
        lines = [
            "AFFIDAVIT ON STAMP PAPER",
            "=" * 50,
            f"Reference: AFF/MIS/{v}/2025",
            f"I, Secretary of {mismatched_name}, solemnly affirm that all details are accurate.",
            f"Institution PID: {inst['code']}",
        ]
        create_simple_pdf(fpath, "AFFIDAVIT", lines)
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "name_mismatch",
            "document": fname,
            "institution_id": inst["id"],
            "description": f"Institution name '{mismatched_name}' in document mismatches registered '{inst['name']}'.",
            "details": {"found": mismatched_name, "expected": inst["name"]}
        })

    # (2) number_mismatch (10 variants)
    for v in range(10):
        inst = INSTITUTIONS[v]
        fname, fpath = get_next_neutral_filename(is_photo=False)
        declared_intake = 360
        mismatched_intake = declared_intake + 120 + (v * 30)
        lines = [
            "AFFIDAVIT ON STAMP PAPER",
            "=" * 50,
            f"Reference: AFF/NUM/{v}/2025",
            f"Institution: {inst['name']}",
            f"Total Student Intake Declared: {mismatched_intake} seats.",
            "AICTE Approved Capacity: Verified.",
        ]
        create_simple_pdf(fpath, "AFFIDAVIT", lines)
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "number_mismatch",
            "document": fname,
            "institution_id": inst["id"],
            "description": f"Affidavit claims intake of {mismatched_intake} but application form declared {declared_intake}.",
            "details": {"doc_intake": mismatched_intake, "form_intake": declared_intake}
        })

    # (3) expired_document (10 variants)
    for v in range(10):
        inst = INSTITUTIONS[v]
        fname, fpath = get_next_neutral_filename(is_photo=False)
        ref_no = f"EXP/FS/{v}/2022"
        issue_d = "01-01-2022"
        expiry_d = f"31-12-202{3 if v < 5 else 4}"  # Expired before 2025
        lines = [
            "FIRE SAFETY COMPLIANCE CERTIFICATE",
            "=" * 50,
            f"Certificate Ref: {ref_no}",
            f"Date of Issue: {issue_d}",
            f"Valid Until: {expiry_d}",
            f"Premises: {inst['name']}, {inst['address']}",
            "Status: EXPIRED",
        ]
        create_simple_pdf(fpath, "FIRE SAFETY CERTIFICATE", lines)
        register_issuer_entry("fire_safety_certificate", ref_no, inst["id"], f"Fire Dept {inst['city']}", issue_d, expiry_d, status="expired")
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "expired_document",
            "document": fname,
            "institution_id": inst["id"],
            "description": f"Fire safety certificate expired on {expiry_d} (prior to submission date 2025-04-10).",
            "details": {"expiry_date": expiry_d}
        })

    # (4) font_inconsistency (10 variants)
    for v in range(10):
        inst = INSTITUTIONS[v]
        fname, fpath = get_next_neutral_filename(is_photo=False)
        lines = [
            "STATE GOVERNMENT NO OBJECTION CERTIFICATE",
            "=" * 50,
            f"Reference: NOC/TAMPER/{v}/2025",
            f"Date: 15-08-2025",
            f"Intake: 480 seats",
            f"Institution: {inst['name']}",
            f"Survey Number: 104/{v}A",
            "Director of Technical Education",
        ]
        create_simple_pdf(fpath, "NO OBJECTION CERTIFICATE", lines, tamper_font=True)
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "font_inconsistency",
            "document": fname,
            "institution_id": inst["id"],
            "description": "Critical certificate lines (date/intake/survey) spliced with Courier font in Helvetica canvas.",
            "details": {"tampered_lines": ["Date", "Intake", "Survey"]}
        })

    # (5) metadata_edited (10 variants)
    editors = [
        "Adobe Photoshop CC 2024 (Windows)",
        "GIMP 2.10.34 (Linux)",
        "Adobe Illustrator 28.0",
        "CorelDRAW 2023 Graphics Suite",
        "Inkscape 1.3 vector drawing",
        "Adobe Photoshop 25.1",
        "GIMP 2.10.30",
        "Adobe Illustrator CC 2023",
        "Photoshop Elements 2024",
        "Adobe Photoshop Lightroom 13.0",
    ]
    for v in range(10):
        inst = INSTITUTIONS[v]
        fname, fpath = get_next_neutral_filename(is_photo=False)
        lines = [
            "GOVERNMENT ACCREDITATION CERTIFICATE",
            "=" * 50,
            f"Accreditation Ref: ACC/META/{v}/2025",
            f"Institution: {inst['name']}",
            "Evaluated by Regulatory Board",
        ]
        create_simple_pdf(fpath, "ACCREDITATION CERTIFICATE", lines, producer=editors[v], add_extra_eof=(v % 2 == 0))
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "metadata_edited",
            "document": fname,
            "institution_id": inst["id"],
            "description": f"PDF Producer indicates graphic manipulation tool: {editors[v]}.",
            "details": {"producer": editors[v], "extra_eof": (v % 2 == 0)}
        })

    # (6) qr_payload_mismatch (10 variants)
    for v in range(10):
        inst = INSTITUTIONS[v]
        fname, fpath = get_next_neutral_filename(is_photo=False)
        printed_ref = f"ACC/PRINT/{v}/2025"
        qr_ref = f"ACC/TAMPERED_QR/{v + 999}/2021"
        lines = [
            "ACCREDITATION COUNCIL CERTIFICATE",
            "=" * 50,
            f"Certificate Reference: {printed_ref}",
            f"Awarded to: {inst['name']} ({inst['code']})",
            "Grade: A+",
        ]
        qr_payload = json.dumps({"ref": qr_ref, "inst": "1-MISMATCHED", "type": "accreditation"})
        create_simple_pdf(fpath, "ACCREDITATION CERTIFICATE", lines, qr_data=qr_payload)
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "qr_payload_mismatch",
            "document": fname,
            "institution_id": inst["id"],
            "description": f"QR payload encodes '{qr_ref}' but printed certificate text displays '{printed_ref}'.",
            "details": {"printed": printed_ref, "qr_payload": qr_ref}
        })

    # (7) duplicate_document_across_institutions (10 variants)
    for v in range(10):
        inst_a = INSTITUTIONS[v]
        inst_b = INSTITUTIONS[(v + 6) % len(INSTITUTIONS)]  # Unrelated college in different state
        fname_a, fpath_a = get_next_neutral_filename(is_photo=False)
        fname_b, fpath_b = get_next_neutral_filename(is_photo=False)

        lines = [
            "MUNICIPAL ELECTRICAL SAFETY NOC",
            "=" * 50,
            f"NOC Ref: ELEC/DUP/{v}/2025",
            f"Certified compliant with statutory load norms.",
            "Municipal Chief Engineer",
        ]
        create_simple_pdf(fpath_a, "ELECTRICAL SAFETY NOC", lines)
        shutil.copy2(str(fpath_a), str(fpath_b))  # Identical SHA-256 hash!

        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "duplicate_document_across_institutions",
            "document": fname_b,
            "institution_id": inst_b["id"],
            "description": f"Document {fname_b} has identical hash to {fname_a} submitted by unrelated {inst_a['name']}.",
            "details": {"source_doc": fname_a, "target_doc": fname_b, "source_inst": inst_a["id"], "target_inst": inst_b["id"]}
        })

    # (8) duplicate_photo_across_institutions (10 variants)
    for v in range(10):
        inst_a = INSTITUTIONS[v]
        inst_b = INSTITUTIONS[(v + 5) % len(INSTITUTIONS)]
        fname_a, fpath_a = get_next_neutral_filename(is_photo=True)
        fname_b, fpath_b = get_next_neutral_filename(is_photo=True)

        create_infrastructure_photo(fpath_a, inst_a)
        shutil.copy2(str(fpath_a), str(fpath_b))

        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "duplicate_photo_across_institutions",
            "document": fname_b,
            "institution_id": inst_b["id"],
            "description": f"Infrastructure photo {fname_b} is a duplicate of {fname_a} submitted by {inst_a['name']}.",
            "details": {"source_photo": fname_a, "target_photo": fname_b, "source_inst": inst_a["id"], "target_inst": inst_b["id"]}
        })

    # (9) photo_wrong_gps (10 variants)
    for v in range(10):
        inst = INSTITUTIONS[v]
        fname, fpath = get_next_neutral_filename(is_photo=True)
        create_infrastructure_photo(fpath, inst, wrong_gps=True)
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "photo_wrong_gps",
            "document": fname,
            "institution_id": inst["id"],
            "description": f"Photo GPS tags are > 500km away from campus location ({inst['latitude']}, {inst['longitude']}).",
            "details": {"expected_lat": inst["latitude"], "expected_lng": inst["longitude"]}
        })

    # (10) photo_not_recent (10 variants)
    for v in range(10):
        inst = INSTITUTIONS[v]
        fname, fpath = get_next_neutral_filename(is_photo=True)
        create_infrastructure_photo(fpath, inst, old_date=True)
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "photo_not_recent",
            "document": fname,
            "institution_id": inst["id"],
            "description": "Photo EXIF timestamp is older than 180 days prior to application deadline.",
            "details": {"photo_date": "2023-01-10"}
        })

    # (11) photo_quality_issue (10 variants)
    for v in range(10):
        inst = INSTITUTIONS[v]
        fname, fpath = get_next_neutral_filename(is_photo=True)
        create_infrastructure_photo(fpath, inst, is_blurry=True)
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "photo_quality_issue",
            "document": fname,
            "institution_id": inst["id"],
            "description": "Infrastructure photo is heavily blurred (Laplacian variance below quality cutoff).",
            "details": {"issue": "severe_blur"}
        })

    # (12) ghost_faculty (10 variants)
    for v in range(10):
        fid = f"FAC_GHOST_{v+1:02d}"
        inst_a = INSTITUTIONS[v]
        inst_b = INSTITUTIONS[(v + 3) % len(INSTITUTIONS)]
        fname_a, fpath_a = get_next_neutral_filename(is_photo=False)
        fname_b, fpath_b = get_next_neutral_filename(is_photo=False)

        lines_a = [
            f"FACULTY TEACHING ROSTER - {inst_a['name']}",
            "=" * 50,
            f"Faculty ID: {fid} | Name: Dr. Ghost Faculty {v+1} | Full-Time Professor | City: {inst_a['city']}",
        ]
        lines_b = [
            f"FACULTY TEACHING ROSTER - {inst_b['name']}",
            "=" * 50,
            f"Faculty ID: {fid} | Name: Dr. Ghost Faculty {v+1} | Full-Time Professor | City: {inst_b['city']}",
        ]
        create_simple_pdf(fpath_a, "FACULTY LIST", lines_a)
        create_simple_pdf(fpath_b, "FACULTY LIST", lines_b)

        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "ghost_faculty",
            "document": fname_b,
            "institution_id": inst_b["id"],
            "description": f"Faculty {fid} claimed simultaneously as full-time professor at {inst_a['name']} ({inst_a['city']}) and {inst_b['name']} ({inst_b['city']}).",
            "details": {"faculty_id": fid, "institutions": [inst_a["id"], inst_b["id"]], "cities": [inst_a["city"], inst_b["city"]]}
        })

    # (13) shared_land_survey (10 variants)
    for v in range(10):
        inst_a = INSTITUTIONS[v]
        # Choose college under DIFFERENT trust
        inst_b = INSTITUTIONS[(v + 4) % len(INSTITUTIONS)]
        survey_shared = f"SUR/PARCEL/SHARED/{v+100}"

        fname_a, fpath_a = get_next_neutral_filename(is_photo=False)
        fname_b, fpath_b = get_next_neutral_filename(is_photo=False)

        lines_a = [
            "LAND DEED OWNERSHIP CERTIFICATE",
            "=" * 50,
            f"Survey Number: {survey_shared}",
            f"Owner Trust: {inst_a['trust_name']}",
            f"College: {inst_a['name']} ({inst_a['city']})",
        ]
        lines_b = [
            "LAND DEED OWNERSHIP CERTIFICATE",
            "=" * 50,
            f"Survey Number: {survey_shared}",
            f"Owner Trust: {inst_b['trust_name']}",
            f"College: {inst_b['name']} ({inst_b['city']})",
        ]
        create_simple_pdf(fpath_a, "LAND OWNERSHIP DOCUMENT", lines_a)
        create_simple_pdf(fpath_b, "LAND OWNERSHIP DOCUMENT", lines_b)

        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "shared_land_survey",
            "document": fname_b,
            "institution_id": inst_b["id"],
            "description": f"Land survey parcel {survey_shared} claimed across unrelated trusts '{inst_a['trust_name']}' and '{inst_b['trust_name']}'.",
            "details": {"survey_number": survey_shared, "trusts": [inst_a["trust_name"], inst_b["trust_name"]]}
        })

    # (14) yoy_intake_jump (10 variants)
    for v in range(10):
        inst = INSTITUTIONS[v]
        app_id = f"APP_JUMP_{v+1:03d}_{inst['id']}"
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "yoy_intake_jump",
            "document": app_id,
            "institution_id": inst["id"],
            "description": f"YoY intake jumped by 180% (from 180 to 500) without corresponding infrastructure expansion.",
            "details": {"previous_intake": 180, "current_intake": 500, "jump_pct": 177.7}
        })

    # (15) intake_exceeds_capacity (10 variants)
    for v in range(10):
        inst = INSTITUTIONS[v]
        app_id = f"APP_CAP_{v+1:03d}_{inst['id']}"
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "intake_exceeds_capacity",
            "document": app_id,
            "institution_id": inst["id"],
            "description": "Requested intake of 720 exceeds maximum physical built-up capacity (360) computed per APH norms.",
            "details": {"applied_intake": 720, "max_capacity": 360}
        })

    # (16) missing_document (10 variants)
    missing_statutory_types = [
        "university_affiliation_letter", "fire_safety_certificate", "noc",
        "land_document", "faculty_list", "university_affiliation_letter",
        "fire_safety_certificate", "noc", "land_document", "faculty_list"
    ]
    for v in range(10):
        inst = INSTITUTIONS[v]
        app_id = f"APP_MISSING_{v+1:03d}_{inst['id']}"
        mtype = missing_statutory_types[v]
        GROUND_TRUTH["planted_faults"].append({
            "fault_type": "missing_document",
            "document": app_id,
            "institution_id": inst["id"],
            "description": f"Mandatory statutory document '{mtype}' is missing from submission packet.",
            "details": {"missing_type": mtype}
        })

    GROUND_TRUTH["_meta"]["generated_at"] = datetime.now().isoformat()
    GROUND_TRUTH["_meta"]["total_documents"] = doc_counter
    GROUND_TRUTH["_meta"]["total_planted_faults"] = len(GROUND_TRUTH["planted_faults"])
    GROUND_TRUTH["_meta"]["total_clean_controls"] = len(GROUND_TRUTH["clean_documents"])

    # Save Ground Truth Manifest
    with open(GROUND_TRUTH_PATH, 'w', encoding='utf-8') as f:
        json.dump(GROUND_TRUTH, f, indent=2, ensure_ascii=False)
    print(f"Ground truth saved to {GROUND_TRUTH_PATH}")

    # Save Mock Issuer Registry
    issuer_path = OUTPUT_DIR / "mock_issuer_registry.json"
    with open(issuer_path, 'w', encoding='utf-8') as f:
        json.dump(MOCK_ISSUER_REGISTRY, f, indent=2, ensure_ascii=False)
    print(f"Mock issuer registry saved to {issuer_path}")

    # Save Outside Signals
    signals_path = OUTPUT_DIR / "outside_signals.json"
    signals = {
        "_meta": {"description": "SIMULATED NIRF and NAAC accreditation records", "simulated": True},
        "accredited_institutions": [
            {"code": inst["code"], "name": inst["name"], "grade": "A+", "valid_until": "2028-12-31"}
            for inst in INSTITUTIONS[:6]
        ],
        "ranked_institutions": [
            {"code": inst["code"], "rank": 25 + idx * 10, "year": 2025}
            for idx, inst in enumerate(INSTITUTIONS[:4])
        ]
    }
    with open(signals_path, 'w', encoding='utf-8') as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)
    print(f"Outside signals saved to {signals_path}")

    print("\nBenchmark Suite Summary:")
    print(f"  - Total Generated Neutral Files: {doc_counter} (DOC_0001..DOC_{doc_counter:04d})")
    print(f"  - Total Planted Fault Variants: {len(GROUND_TRUTH['planted_faults'])} (16 categories x 10 variants)")
    print(f"  - Total Clean Control Documents: {len(GROUND_TRUTH['clean_documents'])}")
    print(f"  - Mock Issuer Registry Entries: {len(MOCK_ISSUER_REGISTRY)}")
    print(f"  - Data Directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_benchmark_suite()
