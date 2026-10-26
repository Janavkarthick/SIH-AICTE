"""
AICTE-Verify Synthetic Data Generator
======================================
SIMULATED DATA ONLY - All institutions, persons, and documents are fictional.

Generates realistic-looking PDFs/images with planted faults for testing
the full validation pipeline. Each fault is recorded in ground_truth.json.
"""

import json
import os
import random
import hashlib
import struct
import sys
from datetime import datetime, timedelta
from pathlib import Path
from io import BytesIO
from typing import Any

# Optional imports - graceful fallback
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch, cm
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import black, red, blue, gray, white, HexColor
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("WARNING: reportlab not installed. Using text-based synthetic data.")

try:
    from PIL import Image, ImageDraw, ImageFont
    from PIL.ExifTags import Base as ExifBase
    import piexif
    HAS_PIL = True
except ImportError:
    try:
        from PIL import Image, ImageDraw, ImageFont
        HAS_PIL = True
    except ImportError:
        HAS_PIL = False
        print("WARNING: Pillow not installed.")

try:
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False
    print("WARNING: qrcode not installed.")

# ─── Configuration ───────────────────────────────────────────────────────────

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "synthetic"
GROUND_TRUTH_PATH = OUTPUT_DIR / "ground_truth.json"

# 6 fictional institutions across different regions
INSTITUTIONS = [
    {
        "id": "INST001",
        "name": "Rajiv Gandhi Institute of Technology",
        "code": "RGIT-MH-001",
        "city": "Pune",
        "state": "Maharashtra",
        "region": "West",
        "address": "123 Engineering Road, Pune 411001",
        "trust_name": "Rajiv Education Trust",
        "trust_reg_no": "MH/TRUST/2005/1234",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "established_year": 2005,
    },
    {
        "id": "INST002",
        "name": "Sri Lakshmi Engineering College",
        "code": "SLEC-TN-002",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "region": "South",
        "address": "456 College Avenue, Chennai 600028",
        "trust_name": "Lakshmi Educational Foundation",
        "trust_reg_no": "TN/TRUST/2008/5678",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "established_year": 2008,
    },
    {
        "id": "INST003",
        "name": "Bharati Vidyapeeth College of Engineering",
        "code": "BVCE-KA-003",
        "city": "Bangalore",
        "state": "Karnataka",
        "region": "South",
        "address": "789 Tech Park, Bangalore 560001",
        "trust_name": "Bharati Education Society",
        "trust_reg_no": "KA/SOC/2003/9012",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "established_year": 2003,
    },
    {
        "id": "INST004",
        "name": "Netaji Subhas Institute of Technology",
        "code": "NSIT-UP-004",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "region": "North",
        "address": "101 University Road, Lucknow 226001",
        "trust_name": "Subhas Memorial Trust",
        "trust_reg_no": "UP/TRUST/2010/3456",
        "latitude": 26.8467,
        "longitude": 80.9462,
        "established_year": 2010,
    },
    {
        "id": "INST005",
        "name": "Kalam Technical University",
        "code": "KTU-TN-005",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "region": "South",
        "address": "202 Innovation Drive, Coimbatore 641001",
        "trust_name": "Kalam Foundation for Education",
        "trust_reg_no": "TN/TRUST/2012/7890",
        "latitude": 11.0168,
        "longitude": 76.9558,
        "established_year": 2012,
    },
    {
        "id": "INST006",
        "name": "Savitribai Phule Polytechnic",
        "code": "SPP-MH-006",
        "city": "Nagpur",
        "state": "Maharashtra",
        "region": "West",
        "address": "303 Education Lane, Nagpur 440001",
        "trust_name": "Rajiv Education Trust",  # Same trust as INST001 - for graph detection
        "trust_reg_no": "MH/TRUST/2005/1234",  # Same - planted fault
        "latitude": 21.1458,
        "longitude": 79.0882,
        "established_year": 2007,
    },
]

FACULTY_MEMBERS = [
    {"id": "FAC001", "name": "Dr. Arun Kumar", "qualification": "PhD CS", "designation": "Professor"},
    {"id": "FAC002", "name": "Dr. Priya Sharma", "qualification": "PhD ECE", "designation": "Associate Professor"},
    {"id": "FAC003", "name": "Dr. Rajesh Patel", "qualification": "PhD ME", "designation": "Professor"},
    {"id": "FAC004", "name": "Dr. Sita Devi", "qualification": "PhD Civil", "designation": "Associate Professor"},
    {"id": "FAC005", "name": "Prof. Mohammed Ali", "qualification": "MTech CSE", "designation": "Assistant Professor"},
    {"id": "FAC006", "name": "Dr. Lakshmi Narayan", "qualification": "PhD Physics", "designation": "Professor"},
    {"id": "FAC007", "name": "Prof. Anitha Kumari", "qualification": "MTech IT", "designation": "Assistant Professor"},
    {"id": "FAC008", "name": "Dr. Venkatesh Rao", "qualification": "PhD Mathematics", "designation": "Associate Professor"},
    {"id": "FAC009", "name": "Prof. Deepa Menon", "qualification": "MTech VLSI", "designation": "Assistant Professor"},
    {"id": "FAC010", "name": "Dr. Suresh Babu", "qualification": "PhD Chemistry", "designation": "Professor"},
    # Ghost faculty - assigned to multiple institutions in different cities
    {"id": "FAC011", "name": "Dr. Vikram Singh", "qualification": "PhD CSE", "designation": "Professor", "ghost": True},
    {"id": "FAC012", "name": "Dr. Meena Kumari", "qualification": "PhD ECE", "designation": "Professor", "ghost": True},
]

# Faculty assignments (institution_id -> list of faculty IDs)
FACULTY_ASSIGNMENTS = {
    "INST001": ["FAC001", "FAC002", "FAC003", "FAC005", "FAC011"],  # FAC011 is ghost
    "INST002": ["FAC004", "FAC006", "FAC007", "FAC009", "FAC011"],  # FAC011 also here - different city!
    "INST003": ["FAC002", "FAC008", "FAC010", "FAC012"],  # FAC012 is ghost
    "INST004": ["FAC003", "FAC005", "FAC006", "FAC012"],  # FAC012 also here - different city!
    "INST005": ["FAC001", "FAC007", "FAC009", "FAC010"],
    "INST006": ["FAC004", "FAC008"],
}

# Land survey numbers - some shared across institutions (planted fault)
LAND_SURVEYS = {
    "INST001": "MH/PUNE/SUR/2005/001",
    "INST002": "TN/CHN/SUR/2008/002",
    "INST003": "KA/BLR/SUR/2003/003",
    "INST004": "UP/LKO/SUR/2010/004",
    "INST005": "TN/CBE/SUR/2012/005",
    "INST006": "MH/PUNE/SUR/2005/001",  # Same as INST001! Different city, same survey no.
}

MOCK_ISSUER_REGISTRY: list[dict] = []

GROUND_TRUTH: dict[str, Any] = {
    "_meta": {
        "description": "Ground truth manifest for AICTE-Verify synthetic data evaluation",
        "generated_at": None,
        "simulated": True,
    },
    "planted_faults": [],
    "clean_documents": [],
    "institutions": INSTITUTIONS,
    "faculty_assignments": FACULTY_ASSIGNMENTS,
    "applications": [],
}


def ensure_dirs():
    """Create output directories."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "documents").mkdir(exist_ok=True)
    (OUTPUT_DIR / "photos").mkdir(exist_ok=True)
    (OUTPUT_DIR / "heatmaps").mkdir(exist_ok=True)


def add_fault(fault_type: str, document: str, description: str, details: dict | None = None):
    """Record a planted fault in ground truth."""
    entry = {
        "fault_type": fault_type,
        "document": document,
        "description": description,
        "details": details or {},
    }
    GROUND_TRUTH["planted_faults"].append(entry)


def add_clean(document: str, doc_type: str, institution_id: str):
    """Record a clean (no-fault) document."""
    GROUND_TRUTH["clean_documents"].append({
        "document": document,
        "document_type": doc_type,
        "institution_id": institution_id,
    })


def register_with_issuer(doc_type: str, ref_number: str, institution_id: str,
                          issuer_name: str, issue_date: str, expiry_date: str | None,
                          status: str = "verified", payload: dict | None = None):
    """Register a certificate with the mock issuer."""
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


# ─── PDF Generation ──────────────────────────────────────────────────────────

def generate_qr_image(data: str, size: int = 150) -> Image.Image | None:
    """Generate a QR code image from data string."""
    if not HAS_QR or not HAS_PIL:
        return None
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").get_image()


def create_simple_pdf(filepath: str, title: str, body_lines: list[str],
                       qr_data: str | None = None,
                       producer: str = "ReportLab",
                       tamper_font: bool = False,
                       add_extra_eof: bool = False) -> str:
    """Create a simple PDF document with optional planted faults."""
    if not HAS_REPORTLAB:
        # Fallback: create a text file with .pdf extension
        with open(filepath, 'w') as f:
            f.write(f"%%PDF-SIMULATED\n{title}\n")
            for line in body_lines:
                f.write(line + "\n")
            f.write("%%EOF\n")
        return filepath

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # Set metadata
    c.setTitle(title)
    c.setAuthor("AICTE-Verify Synthetic Generator (SIMULATED)")
    c.setProducer(producer)

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, title)

    # Body
    y = height - 90
    for line in body_lines:
        if y < 80:
            c.showPage()
            y = height - 50

        if tamper_font and "Date:" in line:
            # Plant font inconsistency: use different font for date field
            c.setFont("Courier", 11)
            c.drawString(72, y, line)
            c.setFont("Helvetica", 11)
        else:
            c.setFont("Helvetica", 11)
            c.drawString(72, y, line)
        y -= 18

    # QR code
    if qr_data and HAS_QR and HAS_PIL:
        qr_img = generate_qr_image(qr_data)
        if qr_img:
            qr_path = filepath + ".qr.png"
            qr_img.save(qr_path)
            c.drawImage(qr_path, width - 200, 60, width=100, height=100)
            # Clean up temp QR image after save
            try:
                os.remove(qr_path)
            except OSError:
                pass

    c.save()

    # Post-processing: add extra EOF markers for forensics detection
    if add_extra_eof:
        with open(filepath, 'ab') as f:
            f.write(b"\n%%EOF\n%%EOF\n")

    return filepath


def create_infrastructure_photo(filepath: str, inst: dict,
                                 wrong_gps: bool = False,
                                 old_date: bool = False,
                                 is_blurry: bool = False,
                                 is_duplicate_of: str | None = None) -> str:
    """Generate a synthetic infrastructure photo with controllable EXIF."""
    if not HAS_PIL:
        # Minimal placeholder
        with open(filepath, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n')  # PNG header stub
        return filepath

    # Create a simple image with text
    width, height = 1280, 960
    img = Image.new('RGB', (width, height), color=(200, 220, 240))
    draw = ImageDraw.Draw(img)

    # Draw building-like shapes
    draw.rectangle([100, 300, 500, 700], fill=(180, 180, 180), outline=(100, 100, 100), width=3)
    draw.rectangle([120, 350, 200, 450], fill=(135, 206, 250))  # Window
    draw.rectangle([220, 350, 300, 450], fill=(135, 206, 250))  # Window
    draw.rectangle([320, 350, 400, 450], fill=(135, 206, 250))  # Window
    draw.rectangle([250, 500, 350, 700], fill=(139, 90, 43))    # Door
    draw.rectangle([550, 400, 900, 700], fill=(180, 180, 180), outline=(100, 100, 100), width=3)
    draw.rectangle([570, 450, 650, 530], fill=(135, 206, 250))
    draw.rectangle([700, 450, 780, 530], fill=(135, 206, 250))

    # Add text overlay
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except (IOError, OSError):
        font = ImageFont.load_default()

    draw.text((100, 750), f"{inst['name']} - Campus Building", fill=(50, 50, 50), font=font)
    draw.text((100, 800), f"[SIMULATED PHOTO - Not a real institution]", fill=(200, 50, 50), font=font)

    if is_blurry:
        from PIL import ImageFilter
        img = img.filter(ImageFilter.GaussianBlur(radius=10))

    img.save(filepath, "JPEG", quality=85)

    # Add EXIF data
    try:
        import piexif

        lat = inst["latitude"]
        lng = inst["longitude"]

        if wrong_gps:
            # Plant wrong GPS - 500km away
            lat += 5.0
            lng += 5.0

        def to_deg_min_sec(val):
            """Convert decimal degrees to (degrees, minutes, seconds) tuples for EXIF."""
            val = abs(val)
            d = int(val)
            m = int((val - d) * 60)
            s = int(((val - d) * 60 - m) * 60 * 100)
            return ((d, 1), (m, 1), (s, 100))

        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: b'N' if lat >= 0 else b'S',
            piexif.GPSIFD.GPSLatitude: to_deg_min_sec(lat),
            piexif.GPSIFD.GPSLongitudeRef: b'E' if lng >= 0 else b'W',
            piexif.GPSIFD.GPSLongitude: to_deg_min_sec(lng),
        }

        if old_date:
            date_str = "2023:01:15 10:30:00"
        else:
            date_str = datetime.now().strftime("%Y:%m:%d %H:%M:%S")

        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: date_str.encode(),
            piexif.ExifIFD.DateTimeDigitized: date_str.encode(),
        }

        zeroth_ifd = {
            piexif.ImageIFD.Make: b"SIMULATED Camera",
            piexif.ImageIFD.Model: b"SyntheticCam v1",
            piexif.ImageIFD.DateTime: date_str.encode(),
        }

        exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd}
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filepath)
    except (ImportError, Exception) as e:
        print(f"  Warning: Could not add EXIF data: {e}")

    return filepath


# ─── Document Generators ─────────────────────────────────────────────────────

def gen_affidavit(inst: dict, app_id: str, intake: int, year: str,
                  name_mismatch: bool = False) -> tuple[str, dict]:
    """Generate an affidavit document."""
    ref_no = f"AFF/{inst['state'][:2]}/{year}/{random.randint(1000,9999)}"
    displayed_name = inst["name"] + " (Misspelled)" if name_mismatch else inst["name"]

    lines = [
        "AFFIDAVIT ON STAMP PAPER",
        "=" * 50,
        f"Reference No: {ref_no}",
        f"Date: 01-04-{year}",
        "",
        f"I, the undersigned, authorized signatory of {displayed_name},",
        f"Institution ID: {inst['code']}",
        f"hereby declare that:",
        "",
        f"1. The institution is located at {inst['address']}",
        f"2. The total student intake for academic year {year}-{int(year)+1} is {intake}",
        f"3. All information provided is true and correct.",
        f"4. The institution complies with all AICTE norms.",
        "",
        f"Trust/Society: {inst['trust_name']}",
        f"Registration No: {inst['trust_reg_no']}",
        "",
        "Signature: ________________________",
        f"Name: {random.choice(['Dr. A. Kumar', 'Prof. B. Singh', 'Dr. C. Patel'])}",
        f"Designation: Principal/Director",
        "",
        "[SIMULATED DOCUMENT - Not a real affidavit]",
    ]

    filename = f"{inst['id']}_{app_id}_affidavit.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)

    qr_payload = json.dumps({"ref": ref_no, "inst": inst["code"], "type": "affidavit", "intake": intake})
    create_simple_pdf(filepath, "AFFIDAVIT", lines, qr_data=qr_payload)

    register_with_issuer("affidavit", ref_no, inst["id"], "Notary Public", f"01-04-{year}", None, "verified")

    meta = {
        "ref_number": ref_no,
        "institution_name": displayed_name,
        "institution_id": inst["code"],
        "intake": intake,
        "issue_date": f"01-04-{year}",
        "trust_name": inst["trust_name"],
    }
    return filename, meta


def gen_fire_safety(inst: dict, app_id: str, year: str,
                    expired: bool = False, tamper_font: bool = False) -> tuple[str, dict]:
    """Generate a fire safety certificate."""
    ref_no = f"FSC/{inst['state'][:2]}/{year}/{random.randint(1000,9999)}"

    if expired:
        issue_date = f"01-01-{int(year)-2}"
        expiry_date = f"31-12-{int(year)-1}"
        status = "expired"
    else:
        issue_date = f"01-01-{year}"
        expiry_date = f"31-12-{year}"
        status = "verified"

    lines = [
        "FIRE SAFETY CERTIFICATE",
        "=" * 50,
        f"Certificate No: {ref_no}",
        f"Date of Issue: {issue_date}",
        f"Valid Until: {expiry_date}",
        "",
        f"This is to certify that the premises of:",
        f"Institution: {inst['name']}",
        f"Address: {inst['address']}",
        "",
        "have been inspected and found to comply with fire safety regulations.",
        "",
        f"Issued by: City Fire Department, {inst['city']}",
        "Chief Fire Officer: Shri/Smt. Fire Officer (SIMULATED)",
        "",
        "[SIMULATED DOCUMENT - Not a real fire safety certificate]",
    ]

    filename = f"{inst['id']}_{app_id}_fire_safety.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)

    qr_payload = json.dumps({"ref": ref_no, "type": "fire_safety", "inst": inst["code"]})
    create_simple_pdf(filepath, "FIRE SAFETY CERTIFICATE", lines,
                       qr_data=qr_payload, tamper_font=tamper_font)

    register_with_issuer("fire_safety_certificate", ref_no, inst["id"],
                          f"City Fire Department, {inst['city']}", issue_date, expiry_date, status)

    meta = {
        "ref_number": ref_no,
        "institution_name": inst["name"],
        "issue_date": issue_date,
        "expiry_date": expiry_date,
        "issuing_authority": f"City Fire Department, {inst['city']}",
    }
    return filename, meta


def gen_noc(inst: dict, app_id: str, year: str) -> tuple[str, dict]:
    """Generate a No Objection Certificate."""
    ref_no = f"NOC/{inst['state'][:2]}/{year}/{random.randint(1000,9999)}"
    issue_date = f"15-03-{year}"
    expiry_date = f"14-03-{int(year)+1}"

    lines = [
        "NO OBJECTION CERTIFICATE",
        "=" * 50,
        f"Reference No: {ref_no}",
        f"Date: {issue_date}",
        f"Valid Until: {expiry_date}",
        "",
        f"The State Government of {inst['state']} has no objection to",
        f"the continued operation of {inst['name']} ({inst['code']})",
        f"located at {inst['address']}.",
        "",
        f"Issued by: Department of Technical Education, {inst['state']}",
        "",
        "[SIMULATED DOCUMENT - Not a real NOC]",
    ]

    filename = f"{inst['id']}_{app_id}_noc.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)
    qr_payload = json.dumps({"ref": ref_no, "type": "noc", "inst": inst["code"]})
    create_simple_pdf(filepath, "NO OBJECTION CERTIFICATE", lines, qr_data=qr_payload)

    register_with_issuer("noc", ref_no, inst["id"],
                          f"Dept of Technical Education, {inst['state']}", issue_date, expiry_date, "verified")

    return filename, {"ref_number": ref_no, "issue_date": issue_date, "expiry_date": expiry_date,
                       "institution_name": inst["name"], "institution_id": inst["code"]}


def gen_accreditation(inst: dict, app_id: str, year: str,
                       mismatch_qr: bool = False) -> tuple[str, dict]:
    """Generate an accreditation certificate."""
    ref_no = f"ACC/{year}/{random.randint(10000,99999)}"
    issue_date = f"01-07-{int(year)-2}"
    expiry_date = f"30-06-{int(year)+3}"

    lines = [
        "ACCREDITATION CERTIFICATE",
        "=" * 50,
        f"Certificate No: {ref_no}",
        f"Date of Accreditation: {issue_date}",
        f"Valid Until: {expiry_date}",
        "",
        f"This is to certify that {inst['name']}",
        f"Institution Code: {inst['code']}",
        "has been accredited with Grade 'A' by the",
        "National Accreditation Body (SIMULATED)",
        "",
        "Accreditation Council",
        "",
        "[SIMULATED DOCUMENT - Not a real accreditation certificate]",
    ]

    filename = f"{inst['id']}_{app_id}_accreditation.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)

    # QR mismatch: QR says different ref number than printed
    qr_ref = f"ACC/{year}/{random.randint(10000,99999)}" if mismatch_qr else ref_no
    qr_payload = json.dumps({"ref": qr_ref, "type": "accreditation", "inst": inst["code"]})
    create_simple_pdf(filepath, "ACCREDITATION CERTIFICATE", lines, qr_data=qr_payload)

    register_with_issuer("accreditation_certificate", ref_no, inst["id"],
                          "National Accreditation Body (SIMULATED)", issue_date, expiry_date, "verified")

    meta = {
        "ref_number": ref_no,
        "qr_ref_number": qr_ref,
        "institution_name": inst["name"],
        "issue_date": issue_date,
        "expiry_date": expiry_date,
    }
    return filename, meta


def gen_land_document(inst: dict, app_id: str, year: str) -> tuple[str, dict]:
    """Generate a land document."""
    survey_no = LAND_SURVEYS[inst["id"]]
    area_acres = round(random.uniform(5, 25), 2)

    lines = [
        "LAND OWNERSHIP DOCUMENT",
        "=" * 50,
        f"Survey Number: {survey_no}",
        f"Total Area: {area_acres} acres ({area_acres * 43560:.0f} sq.ft)",
        "",
        f"Owner: {inst['trust_name']}",
        f"Trust Registration: {inst['trust_reg_no']}",
        f"Location: {inst['address']}",
        f"City: {inst['city']}, State: {inst['state']}",
        "",
        "This document certifies ownership of the above land parcel.",
        f"Registered on: 01-01-{inst['established_year']}",
        "",
        f"Sub-Registrar Office, {inst['city']}",
        "",
        "[SIMULATED DOCUMENT - Not a real land document]",
    ]

    filename = f"{inst['id']}_{app_id}_land_document.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)
    create_simple_pdf(filepath, "LAND OWNERSHIP DOCUMENT", lines)

    return filename, {"survey_number": survey_no, "area_acres": area_acres,
                       "trust_name": inst["trust_name"], "institution_name": inst["name"]}


def gen_affiliation_letter(inst: dict, app_id: str, year: str) -> tuple[str, dict]:
    """Generate a university affiliation letter."""
    ref_no = f"AFFL/{inst['state'][:2]}/{year}/{random.randint(1000,9999)}"
    university_name = f"State Technical University, {inst['state']} (SIMULATED)"

    lines = [
        "UNIVERSITY AFFILIATION LETTER",
        "=" * 50,
        f"Reference No: {ref_no}",
        f"Date: 15-05-{year}",
        "",
        f"To: The Principal/Director",
        f"{inst['name']}",
        f"{inst['address']}",
        "",
        f"Subject: Affiliation for Academic Year {year}-{int(year)+1}",
        "",
        f"This is to confirm that {inst['name']} (Code: {inst['code']})",
        f"is affiliated to {university_name}",
        f"for the academic year {year}-{int(year)+1}.",
        "",
        "Registrar",
        university_name,
        "",
        "[SIMULATED DOCUMENT - Not a real affiliation letter]",
    ]

    filename = f"{inst['id']}_{app_id}_affiliation.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)
    qr_payload = json.dumps({"ref": ref_no, "type": "affiliation", "inst": inst["code"]})
    create_simple_pdf(filepath, "UNIVERSITY AFFILIATION LETTER", lines, qr_data=qr_payload)

    register_with_issuer("university_affiliation_letter", ref_no, inst["id"],
                          university_name, f"15-05-{year}", f"14-05-{int(year)+1}", "verified")

    return filename, {"ref_number": ref_no, "university_name": university_name,
                       "institution_name": inst["name"], "issue_date": f"15-05-{year}"}


def gen_faculty_list(inst: dict, app_id: str, year: str,
                      count_override: int | None = None) -> tuple[str, dict]:
    """Generate a faculty list document."""
    faculty_ids = FACULTY_ASSIGNMENTS.get(inst["id"], ["FAC001", "FAC002"])
    faculty_data = []
    for fid in faculty_ids:
        for f in FACULTY_MEMBERS:
            if f["id"] == fid:
                faculty_data.append(f)
                break

    lines = [
        "FACULTY LIST",
        "=" * 50,
        f"Institution: {inst['name']}",
        f"Code: {inst['code']}",
        f"Academic Year: {year}-{int(year)+1}",
        "",
        f"Total Faculty: {count_override or len(faculty_data)}",
        "",
        "S.No | Faculty ID | Name | Qualification | Designation",
        "-" * 70,
    ]

    for i, f in enumerate(faculty_data, 1):
        lines.append(f"  {i}  | {f['id']}  | {f['name']}  | {f['qualification']}  | {f['designation']}")

    lines.extend([
        "",
        "Principal/Director",
        inst["name"],
        "",
        "[SIMULATED DOCUMENT - Not a real faculty list]",
    ])

    filename = f"{inst['id']}_{app_id}_faculty_list.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)
    create_simple_pdf(filepath, "FACULTY LIST", lines)

    return filename, {"institution_name": inst["name"], "faculty_count": len(faculty_data),
                       "faculty_ids": faculty_ids, "displayed_count": count_override or len(faculty_data)}


def gen_electricity_bill(inst: dict, app_id: str, year: str) -> tuple[str, dict]:
    """Generate an electricity bill."""
    bill_no = f"EB/{inst['city'][:3].upper()}/{year}/{random.randint(100000,999999)}"

    lines = [
        "ELECTRICITY BILL",
        "=" * 50,
        f"Bill No: {bill_no}",
        f"Bill Date: 01-02-{year}",
        f"Billing Period: January {year}",
        "",
        f"Consumer: {inst['trust_name']}",
        f"Premises: {inst['address']}",
        f"Consumer No: {random.randint(1000000, 9999999)}",
        "",
        f"Units Consumed: {random.randint(5000, 20000)} kWh",
        f"Amount: Rs. {random.randint(50000, 200000)}/-",
        "",
        f"State Electricity Board, {inst['state']} (SIMULATED)",
        "",
        "[SIMULATED DOCUMENT - Not a real electricity bill]",
    ]

    filename = f"{inst['id']}_{app_id}_electricity_bill.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)
    create_simple_pdf(filepath, "ELECTRICITY BILL", lines)

    return filename, {"bill_number": bill_no, "institution_name": inst["trust_name"],
                       "bill_date": f"01-02-{year}"}


def gen_application_form(inst: dict, app_id: str, category: str, year: str,
                          intake: int, intake_mismatch_value: int | None = None) -> tuple[str, dict]:
    """Generate an application form."""
    displayed_intake = intake_mismatch_value if intake_mismatch_value else intake

    cat_label = {
        "extension_of_approval": "Extension of Approval",
        "increase_of_intake": "Increase of Intake",
        "new_course": "New Course Introduction",
        "closure": "Closure of Institution/Course",
    }.get(category, category)

    lines = [
        "AICTE APPLICATION FORM (SIMULATED)",
        "=" * 50,
        f"Application ID: {app_id}",
        f"Category: {cat_label}",
        f"Academic Year: {year}-{int(year)+1}",
        "",
        f"Institution Name: {inst['name']}",
        f"Institution Code: {inst['code']}",
        f"Address: {inst['address']}",
        f"City: {inst['city']}, State: {inst['state']}",
        "",
        f"Trust/Society: {inst['trust_name']}",
        f"Registration No: {inst['trust_reg_no']}",
        "",
        f"Current Approved Intake: {intake}",
        f"Applied Intake: {displayed_intake}",
        "",
        f"Total Built-up Area: {random.randint(20000, 100000)} sq.ft",
        f"Total Land Area: {round(random.uniform(5, 25), 2)} acres",
        f"Number of Classrooms: {random.randint(10, 40)}",
        f"Number of Labs: {random.randint(5, 20)}",
        "",
        "Declaration: All information is true and correct.",
        "",
        "[SIMULATED DOCUMENT - Not a real AICTE application]",
    ]

    filename = f"{inst['id']}_{app_id}_application_form.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)
    create_simple_pdf(filepath, f"AICTE APPLICATION - {cat_label}", lines)

    return filename, {
        "application_id": app_id,
        "category": category,
        "institution_name": inst["name"],
        "institution_id": inst["code"],
        "intake": displayed_intake,
        "actual_intake": intake,
    }


def gen_tamil_certificate(inst: dict, app_id: str, year: str) -> tuple[str, dict]:
    """Generate a certificate with Tamil text content."""
    ref_no = f"TN/CERT/{year}/{random.randint(1000,9999)}"

    lines = [
        "சான்றிதழ் / CERTIFICATE",
        "=" * 50,
        f"சான்றிதழ் எண் / Certificate No: {ref_no}",
        f"தேதி / Date: 01-06-{year}",
        "",
        f"நிறுவனம் / Institution: {inst['name']}",
        f"நிறுவன குறியீடு / Code: {inst['code']}",
        "",
        "இந்த சான்றிதழ் மேற்கண்ட நிறுவனத்திற்கு வழங்கப்படுகிறது.",
        "This certificate is issued to the above institution.",
        "",
        f"வழங்கியவர் / Issued by: தமிழ்நாடு தொழில்நுட்பக் கல்வித் துறை",
        f"Department of Technical Education, Tamil Nadu",
        "",
        "[SIMULATED - போலி ஆவணம்]",
    ]

    filename = f"{inst['id']}_{app_id}_tamil_cert.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)
    create_simple_pdf(filepath, "சான்றிதழ் / CERTIFICATE", lines)

    register_with_issuer("noc", ref_no, inst["id"],
                          "Dept of Technical Education, Tamil Nadu", f"01-06-{year}",
                          f"31-05-{int(year)+1}", "verified")

    return filename, {"ref_number": ref_no, "language": "tamil",
                       "institution_name": inst["name"]}


def gen_hindi_certificate(inst: dict, app_id: str, year: str) -> tuple[str, dict]:
    """Generate a certificate with Hindi text content."""
    ref_no = f"UP/CERT/{year}/{random.randint(1000,9999)}"

    lines = [
        "प्रमाण पत्र / CERTIFICATE",
        "=" * 50,
        f"प्रमाण पत्र संख्या / Certificate No: {ref_no}",
        f"दिनांक / Date: 01-06-{year}",
        "",
        f"संस्थान / Institution: {inst['name']}",
        f"संस्थान कोड / Code: {inst['code']}",
        "",
        "यह प्रमाण पत्र उपरोक्त संस्थान को जारी किया जाता है।",
        "This certificate is issued to the above institution.",
        "",
        f"जारीकर्ता / Issued by: उत्तर प्रदेश तकनीकी शिक्षा विभाग",
        f"Department of Technical Education, Uttar Pradesh",
        "",
        "[SIMULATED - नकली दस्तावेज़]",
    ]

    filename = f"{inst['id']}_{app_id}_hindi_cert.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)
    create_simple_pdf(filepath, "प्रमाण पत्र / CERTIFICATE", lines)

    register_with_issuer("noc", ref_no, inst["id"],
                          "Dept of Technical Education, UP", f"01-06-{year}",
                          f"31-05-{int(year)+1}", "verified")

    return filename, {"ref_number": ref_no, "language": "hindi",
                       "institution_name": inst["name"]}


def create_duplicate_document(src_filename: str, dst_filename: str):
    """Create an exact duplicate of a document (for duplicate detection testing)."""
    src_path = OUTPUT_DIR / "documents" / src_filename
    dst_path = OUTPUT_DIR / "documents" / dst_filename
    if src_path.exists():
        import shutil
        shutil.copy2(str(src_path), str(dst_path))


def create_edited_metadata_pdf(inst: dict, app_id: str, year: str) -> tuple[str, dict]:
    """Create a PDF whose metadata says it was created by an editing tool (planted fault)."""
    ref_no = f"MET/{year}/{random.randint(1000,9999)}"

    lines = [
        "OFFICIAL CERTIFICATE (SIMULATED)",
        "=" * 50,
        f"Reference: {ref_no}",
        f"Date: 01-03-{year}",
        f"Institution: {inst['name']}",
        "",
        "This certificate is issued for official purposes.",
        "",
        "[SIMULATED - Metadata edited by different tool]",
    ]

    filename = f"{inst['id']}_{app_id}_edited_metadata.pdf"
    filepath = str(OUTPUT_DIR / "documents" / filename)
    # Producer set to an editing tool name
    create_simple_pdf(filepath, "OFFICIAL CERTIFICATE", lines,
                       producer="Adobe Acrobat Pro DC (edited)", add_extra_eof=True)

    return filename, {"ref_number": ref_no, "producer": "Adobe Acrobat Pro DC (edited)",
                       "extra_eof": True}


# ─── Application Generator ───────────────────────────────────────────────────

def generate_applications():
    """Generate all synthetic applications with planted faults."""
    print("Generating synthetic applications and documents...")
    ensure_dirs()

    applications = []
    app_counter = 0

    # Academic years for YoY comparison
    years = ["2024", "2025", "2026"]

    for inst in INSTITUTIONS:
        for year_idx, year in enumerate(years):
            app_counter += 1
            app_id = f"APP{app_counter:03d}"

            # Determine category
            if year_idx == 0:
                category = "extension_of_approval"
            elif year_idx == 1:
                category = random.choice(["extension_of_approval", "increase_of_intake"])
            else:
                if inst["id"] == "INST003":
                    category = "new_course"
                elif inst["id"] == "INST006":
                    category = "closure"
                else:
                    category = random.choice(["extension_of_approval", "increase_of_intake"])

            # Base intake with YoY jumps for some institutions
            base_intake = random.choice([60, 120, 180, 240])
            if inst["id"] == "INST004" and year == "2026":
                intake = base_intake * 3  # 200% jump - planted fault
                intake_jump = True
            else:
                intake = base_intake + (year_idx * 30)
                intake_jump = False

            documents = []
            doc_faults = []

            # ─── Generate documents per application ───

            # 1. Application Form
            if inst["id"] == "INST001" and year == "2026":
                # Intake mismatch between form and affidavit
                fname, meta = gen_application_form(inst, app_id, category, year, intake,
                                                     intake_mismatch_value=intake + 300)
                doc_faults.append("intake_mismatch_form_vs_affidavit")
                add_fault("number_mismatch", fname,
                          f"Application form shows intake {intake+300} but affidavit shows {intake}",
                          {"form_intake": intake+300, "affidavit_intake": intake})
            else:
                fname, meta = gen_application_form(inst, app_id, category, year, intake)
            documents.append({"filename": fname, "type": "application_form", "meta": meta})

            # 2. Affidavit
            if inst["id"] == "INST002" and year == "2026":
                # Name mismatch
                fname, meta = gen_affidavit(inst, app_id, intake, year, name_mismatch=True)
                doc_faults.append("name_mismatch")
                add_fault("name_mismatch", fname,
                          "Institution name in affidavit differs from application form",
                          {"affidavit_name": meta["institution_name"]})
            else:
                fname, meta = gen_affidavit(inst, app_id, intake, year)
            documents.append({"filename": fname, "type": "affidavit", "meta": meta})

            # 3. Fire Safety Certificate
            if inst["id"] == "INST003" and year == "2025":
                # Expired certificate
                fname, meta = gen_fire_safety(inst, app_id, year, expired=True)
                doc_faults.append("expired_certificate")
                add_fault("expired_document", fname,
                          f"Fire safety certificate expired on {meta['expiry_date']}",
                          {"expiry_date": meta["expiry_date"]})
            elif inst["id"] == "INST005" and year == "2026":
                # Font tamper
                fname, meta = gen_fire_safety(inst, app_id, year, tamper_font=True)
                doc_faults.append("font_inconsistency")
                add_fault("font_inconsistency", fname,
                          "Date field uses different font (Courier) from rest of document (Helvetica)",
                          {"tampered_field": "date", "expected_font": "Helvetica", "found_font": "Courier"})
            else:
                fname, meta = gen_fire_safety(inst, app_id, year)
                if not doc_faults:
                    add_clean(fname, "fire_safety_certificate", inst["id"])
            documents.append({"filename": fname, "type": "fire_safety_certificate", "meta": meta})

            # 4. NOC
            if category != "closure" or year != "2026":
                fname, meta = gen_noc(inst, app_id, year)
                documents.append({"filename": fname, "type": "noc", "meta": meta})
                if not doc_faults:
                    add_clean(fname, "noc", inst["id"])

            # 5. Accreditation (optional but useful)
            if random.random() > 0.3:
                if inst["id"] == "INST004" and year == "2026":
                    # QR mismatch
                    fname, meta = gen_accreditation(inst, app_id, year, mismatch_qr=True)
                    doc_faults.append("qr_mismatch")
                    add_fault("qr_payload_mismatch", fname,
                              "QR code reference number doesn't match printed certificate number",
                              {"printed_ref": meta["ref_number"], "qr_ref": meta["qr_ref_number"]})
                else:
                    fname, meta = gen_accreditation(inst, app_id, year)
                documents.append({"filename": fname, "type": "accreditation_certificate", "meta": meta})

            # 6. Land Document
            fname, meta = gen_land_document(inst, app_id, year)
            documents.append({"filename": fname, "type": "land_document", "meta": meta})

            # 7. Affiliation Letter
            fname, meta = gen_affiliation_letter(inst, app_id, year)
            documents.append({"filename": fname, "type": "university_affiliation_letter", "meta": meta})
            if not doc_faults:
                add_clean(fname, "university_affiliation_letter", inst["id"])

            # 8. Faculty List
            fname, meta = gen_faculty_list(inst, app_id, year)
            documents.append({"filename": fname, "type": "faculty_list", "meta": meta})

            # 9. Electricity Bill (not always)
            if random.random() > 0.4:
                fname, meta = gen_electricity_bill(inst, app_id, year)
                documents.append({"filename": fname, "type": "electricity_bill", "meta": meta})

            # 10. Infrastructure Photos
            photo_count = random.randint(2, 4)
            for p_idx in range(photo_count):
                photo_filename = f"{inst['id']}_{app_id}_photo_{p_idx+1}.jpg"
                photo_path = str(OUTPUT_DIR / "photos" / photo_filename)

                if inst["id"] == "INST001" and year == "2026" and p_idx == 0:
                    # Wrong GPS
                    create_infrastructure_photo(photo_path, inst, wrong_gps=True)
                    doc_faults.append("wrong_gps")
                    add_fault("photo_wrong_gps", photo_filename,
                              "Photo GPS coordinates are ~500km from claimed campus location",
                              {"expected_lat": inst["latitude"], "expected_lng": inst["longitude"]})
                elif inst["id"] == "INST002" and year == "2026" and p_idx == 0:
                    # Old photo
                    create_infrastructure_photo(photo_path, inst, old_date=True)
                    doc_faults.append("old_photo")
                    add_fault("photo_not_recent", photo_filename,
                              "Photo taken more than 180 days ago",
                              {"photo_date": "2023-01-15"})
                elif inst["id"] == "INST006" and year == "2026" and p_idx == 0:
                    # Blurry
                    create_infrastructure_photo(photo_path, inst, is_blurry=True)
                    doc_faults.append("blurry_photo")
                    add_fault("photo_quality_issue", photo_filename,
                              "Photo is blurry (below quality threshold)",
                              {"issue": "blur"})
                else:
                    create_infrastructure_photo(photo_path, inst)

                documents.append({"filename": photo_filename, "type": "infrastructure_photo",
                                   "meta": {"institution_name": inst["name"]}})

            # 11. Tamil certificate for Tamil Nadu institution
            if inst["state"] == "Tamil Nadu" and year == "2026":
                fname, meta = gen_tamil_certificate(inst, app_id, year)
                documents.append({"filename": fname, "type": "noc", "meta": meta})
                add_clean(fname, "noc_tamil", inst["id"])

            # 12. Hindi certificate for UP institution
            if inst["state"] == "Uttar Pradesh" and year == "2026":
                fname, meta = gen_hindi_certificate(inst, app_id, year)
                documents.append({"filename": fname, "type": "noc", "meta": meta})
                add_clean(fname, "noc_hindi", inst["id"])

            # 13. Edited metadata PDF (for forensics)
            if inst["id"] == "INST005" and year == "2025":
                fname, meta = create_edited_metadata_pdf(inst, app_id, year)
                doc_faults.append("edited_metadata")
                add_fault("metadata_edited", fname,
                          "PDF producer/creator indicates editing tool, multiple EOF markers found",
                          {"producer": meta["producer"]})
                documents.append({"filename": fname, "type": "noc", "meta": meta})

            # 14. Missing mandatory document for one application
            if inst["id"] == "INST006" and year == "2026" and category != "closure":
                # Don't generate affiliation letter - it's mandatory but missing
                doc_faults.append("missing_document")
                add_fault("missing_document", f"{app_id}_missing",
                          "Missing mandatory document: University Affiliation Letter",
                          {"missing_type": "university_affiliation_letter"})

            # 15. Duplicate document across institutions
            if inst["id"] == "INST003" and year == "2026":
                # Copy INST001's fire safety cert as a near-duplicate
                src = f"INST001_APP001_fire_safety.pdf"
                dst = f"INST003_{app_id}_duplicate_cert.pdf"
                create_duplicate_document(src, dst)
                if (OUTPUT_DIR / "documents" / dst).exists():
                    doc_faults.append("duplicate_document")
                    add_fault("duplicate_document_across_institutions", dst,
                              "This document is identical to one submitted by a different institution",
                              {"source_institution": "INST001", "source_document": src})
                    documents.append({"filename": dst, "type": "fire_safety_certificate", "meta": {}})

            # 16. Duplicate photo across institutions
            if inst["id"] == "INST004" and year == "2026":
                src_photo = f"INST001_APP001_photo_1.jpg"
                dst_photo = f"INST004_{app_id}_photo_dup.jpg"
                src_path = OUTPUT_DIR / "photos" / src_photo
                dst_path = OUTPUT_DIR / "photos" / dst_photo
                if src_path.exists():
                    import shutil
                    shutil.copy2(str(src_path), str(dst_path))
                    doc_faults.append("duplicate_photo")
                    add_fault("duplicate_photo_across_institutions", dst_photo,
                              "This infrastructure photo is identical to one submitted by a different institution",
                              {"source_institution": "INST001"})
                    documents.append({"filename": dst_photo, "type": "infrastructure_photo", "meta": {}})

            # Record intake jump fault
            if intake_jump:
                add_fault("yoy_intake_jump", f"{app_id}",
                          "Intake increased by 200%+ YoY with no corresponding infrastructure increase",
                          {"previous_intake": base_intake, "current_intake": intake, "jump_pct": 200})

            # Record application
            app_data = {
                "id": app_id,
                "institution_id": inst["id"],
                "institution_name": inst["name"],
                "category": category,
                "academic_year": year,
                "intake": intake,
                "documents": documents,
                "planted_faults": doc_faults,
                "region": inst["region"],
                "status": "submitted",
            }
            applications.append(app_data)

    # ─── Record graph faults ───
    # Ghost faculty
    add_fault("ghost_faculty", "FAC011",
              "Faculty FAC011 (Dr. Vikram Singh) listed as full-time at INST001 (Pune) and INST002 (Chennai) simultaneously",
              {"faculty_id": "FAC011", "institutions": ["INST001", "INST002"],
               "cities": ["Pune", "Chennai"]})
    add_fault("ghost_faculty", "FAC012",
              "Faculty FAC012 (Dr. Meena Kumari) listed as full-time at INST003 (Bangalore) and INST004 (Lucknow) simultaneously",
              {"faculty_id": "FAC012", "institutions": ["INST003", "INST004"],
               "cities": ["Bangalore", "Lucknow"]})

    # Shared land
    add_fault("shared_land_survey", "MH/PUNE/SUR/2005/001",
              "Same land survey number used by INST001 (Pune) and INST006 (Nagpur)",
              {"survey_number": "MH/PUNE/SUR/2005/001",
               "institutions": ["INST001", "INST006"]})

    # Same trust across institutions
    add_fault("shared_trust", "MH/TRUST/2005/1234",
              "Same trust (Rajiv Education Trust) behind INST001 and INST006",
              {"trust_reg_no": "MH/TRUST/2005/1234",
               "institutions": ["INST001", "INST006"]})

    # ─── Record verification statuses ───
    # Make sure all 6 statuses are represented
    verification_statuses = [
        {"status": "verified", "institution": "INST001", "doc": "fire_safety"},
        {"status": "mismatch_detected", "institution": "INST004", "doc": "accreditation"},
        {"status": "expired", "institution": "INST003", "doc": "fire_safety"},
        {"status": "verification_pending", "institution": "INST005", "doc": "noc"},
        {"status": "source_unavailable", "institution": "INST006", "doc": "noc"},
        {"status": "manual_review_required", "institution": "INST002", "doc": "affidavit"},
    ]

    # Build institution capacity data for compliance checking
    # INST004 has excessive intake for its infrastructure
    for inst in INSTITUTIONS:
        if inst["id"] == "INST004":
            add_fault("intake_exceeds_capacity", inst["id"],
                      "Applied intake (720) exceeds computed maximum capacity (360) based on infrastructure",
                      {"applied_intake": 720, "max_capacity": 360})

    GROUND_TRUTH["applications"] = applications
    GROUND_TRUTH["verification_statuses"] = verification_statuses
    GROUND_TRUTH["_meta"]["generated_at"] = datetime.now().isoformat()

    return applications


def save_ground_truth():
    """Save ground truth manifest."""
    with open(GROUND_TRUTH_PATH, 'w', encoding='utf-8') as f:
        json.dump(GROUND_TRUTH, f, indent=2, ensure_ascii=False)
    print(f"Ground truth saved to {GROUND_TRUTH_PATH}")


def save_issuer_registry():
    """Save mock issuer registry."""
    registry_path = OUTPUT_DIR / "mock_issuer_registry.json"
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(MOCK_ISSUER_REGISTRY, f, indent=2, ensure_ascii=False)
    print(f"Mock issuer registry saved to {registry_path}")


def save_outside_signals():
    """Save SIMULATED outside signals (accreditation/ranking entries) for A8."""
    signals_path = OUTPUT_DIR / "outside_signals.json"
    signals = {
        "_meta": {
            "description": "SIMULATED accreditation and ranking entries for outside-signals check (A8)",
            "simulated": True
        },
        "accredited_institutions": [
            {"code": "RGIT-MH-001", "name": "Rajiv Gandhi Institute of Technology", "grade": "A", "valid_until": "2028-06-30"},
            {"code": "SLEC-TN-002", "name": "Sri Lakshmi Engineering College", "grade": "B+", "valid_until": "2027-06-30"},
            {"code": "BVCE-KA-003", "name": "Bharati Vidyapeeth College of Engineering", "grade": "A+", "valid_until": "2029-06-30"},
            # INST004, INST005, INST006 deliberately missing for flag testing
        ],
        "ranked_institutions": [
            {"code": "RGIT-MH-001", "rank": 45, "year": 2026},
            {"code": "BVCE-KA-003", "rank": 32, "year": 2026},
        ]
    }
    with open(signals_path, 'w', encoding='utf-8') as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)
    print(f"Outside signals saved to {signals_path}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    """Generate all synthetic data."""
    print("=" * 60)
    print("AICTE-Verify Synthetic Data Generator")
    print("ALL DATA IS SIMULATED - No real institutions or persons")
    print("=" * 60)

    applications = generate_applications()
    save_ground_truth()
    save_issuer_registry()
    save_outside_signals()

    print(f"\nGenerated:")
    print(f"  - {len(applications)} applications")
    print(f"  - {sum(len(a['documents']) for a in applications)} documents")
    print(f"  - {len(GROUND_TRUTH['planted_faults'])} planted faults")
    print(f"  - {len(GROUND_TRUTH['clean_documents'])} clean documents")
    print(f"  - {len(MOCK_ISSUER_REGISTRY)} issuer registry entries")
    print(f"\nOutput directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
