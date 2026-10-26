"""Script to generate the comprehensive AICTE-Verify System Architecture & Technical Documentation PDF."""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw running header and total page count."""

    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        if self._pageNumber > 1:
            # Running Header
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#1e3a8a"))  # Navy
            self.drawString(54, 752, "AICTE-VERIFY: INTELLIGENT SCRUTINY & AFFILIATION RISK ASSESSMENT SYSTEM")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748b"))  # Slate
            self.drawRightString(558, 752, "TECHNICAL ARCHITECTURE MANUAL")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.6)
            self.line(54, 745, 558, 745)

            # Running Footer
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.6)
            self.line(54, 48, 558, 48)
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 36, "AICTE Approval Process Handbook (APH 2024-27) Compliance • Confidential Engineering Specification")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 36, page_text)
        self.restoreState()


def build_pdf(output_path: str):
    """Construct and build the professional documentation PDF."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Color Palette Definitions
    c_primary = colors.HexColor("#0f2e59")     # Deep AICTE Blue
    c_secondary = colors.HexColor("#1e3a8a")   # Indigo / Royal Navy
    c_accent = colors.HexColor("#d97706")      # Warm Amber / Statutory Gold
    c_dark = colors.HexColor("#0f172a")        # Slate 900
    c_body = colors.HexColor("#334155")        # Slate 700
    c_border = colors.HexColor("#e2e8f0")      # Slate 200
    c_bg_light = colors.HexColor("#f8fafc")    # Slate 50
    c_success = colors.HexColor("#059669")     # Emerald
    c_danger = colors.HexColor("#dc2626")      # Rose Red

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=c_primary,
        alignment=0,
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#475569"),
        alignment=0,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )
    h3_style = ParagraphStyle(
        "Heading3_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=c_dark,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=c_body,
        spaceBefore=2,
        spaceAfter=4,
    )
    body_bold = ParagraphStyle(
        "BodyBold_Custom",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceBefore=1.5,
        spaceAfter=2,
    )
    callout_text = ParagraphStyle(
        "CalloutText",
        parent=body_style,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        textColor=c_dark,
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell,
        fontName="Helvetica-Bold",
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10.5,
        textColor=colors.white,
    )

    story = []

    # =========================================================================
    # COVER / TITLE BLOCK
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("ALL INDIA COUNCIL FOR TECHNICAL EDUCATION (AICTE)", ParagraphStyle(
        "GovtHeader", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=c_accent, textTransform="uppercase"
    )))
    story.append(Spacer(1, 4))
    story.append(Paragraph("AICTE-Verify: Intelligent Cross-Document Scrutiny & Affiliation Risk Assessment System", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Comprehensive Technical Architecture, End-to-End Operational Lifecycle, Machine Learning Forensic Pipeline Specifications, and Statutory Approval Process Handbook (APH 2024–25 to 2026–27) Integration Manual",
        subtitle_style
    ))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=4, spaceAfter=14))

    # Metadata Summary Table
    meta_data = [
        [
            Paragraph("<b>Document Version:</b> 2.4.0 (Production Release)", table_cell),
            Paragraph("<b>Regulatory Base:</b> AICTE APH 2024-25 to 2026-27", table_cell),
        ],
        [
            Paragraph("<b>Target Framework:</b> Smart India Hackathon (SIH) 2024", table_cell),
            Paragraph("<b>Classification:</b> Official Technical Architecture Manual", table_cell),
        ],
        [
            Paragraph("<b>Engine Status:</b> Multi-Model Microservices Operational", table_cell),
            Paragraph("<b>Security Spec:</b> Zero-Trust SHA-256 Audit Trail", table_cell),
        ],
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # Executive Abstract Callout Box
    abstract_text = (
        "<b>Executive Summary:</b> AICTE-Verify is an automated regulatory scrutiny platform developed to resolve the acute "
        "inspection bottleneck across India's 10,000+ technical education institutions. Each academic year, institutions "
        "submit thousands of multipage regulatory artifacts (Land Title Deeds, Building Completion Form D, Fire Safety NOCs, "
        "Faculty Rosters, and Audited Financial Statements). AICTE-Verify combines multi-lingual optical character recognition "
        "(OCR), computer vision Error Level Analysis (ELA) for digital forgery detection, perceptual hashing (pHash) for cross-institutional "
        "certificate deduplication, an automated AICTE APH dimensional compliance engine, and a Cytoscape knowledge graph to detect "
        "ghost faculty syndicates and duplicated land parcels. The system enforces strict Role-Based Access Control (RBAC), "
        "ensuring institutions submit self-disclosures, Regional Officers adjudicate territorial jurisdictions, and Central Admins oversee "
        "national cryptographic hash chain integrity."
    )
    t_abstract = Table([[Paragraph(abstract_text, callout_text)]], colWidths=[504])
    t_abstract.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#3b82f6")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t_abstract)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 1: TECHNOLOGY STACK & ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("1. Complete Technology Stack & Architectural Topology", h1_style))
    story.append(Paragraph(
        "The system employs a decoupled, microservices-ready architecture comprising a high-performance reactive single-page "
        "frontend, an asynchronous REST API backend, and an intelligent forensic processing pipeline.",
        body_style
    ))
    story.append(Spacer(1, 6))

    tech_stack_rows = [
        [
            Paragraph("Architectural Tier", table_header),
            Paragraph("Core Technologies & Frameworks", table_header),
            Paragraph("Design Rationale & Production Purpose", table_header),
        ],
        [
            Paragraph("<b>Frontend Web Application</b>", table_cell_bold),
            Paragraph("React 18.3, TypeScript 5.5, Vite 5.4, Tailwind CSS 3.4, React Router v6, Cytoscape.js 3.30, Axios", table_cell),
            Paragraph("Strict type safety, zero-bundle compilation latency via Vite, atomic reactive UI state, hardware-accelerated force-directed graph visualization.", table_cell),
        ],
        [
            Paragraph("<b>Backend API Engine</b>", table_cell_bold),
            Paragraph("Python 3.12+, FastAPI 0.115, Uvicorn ASGI, SQLAlchemy 2.0 (AsyncIO), Pydantic v2 Settings & Schemas", table_cell),
            Paragraph("High concurrency non-blocking I/O, automated OpenAPI/Swagger contract generation, strict request validation, native Python asyncio worker pools.", table_cell),
        ],
        [
            Paragraph("<b>Database & Persistence</b>", table_cell_bold),
            Paragraph("SQLite 3.45 with aiosqlite driver, Write-Ahead Logging (WAL) Mode, Relational Schema", table_cell),
            Paragraph("ACID transactional compliance, zero-configuration local portability, seamless migration pathway to PostgreSQL/CockroachDB for distributed clustering.", table_cell),
        ],
        [
            Paragraph("<b>Computer Vision & OCR</b>", table_cell_bold),
            Paragraph("Tesseract 5.4 (Indic Multi-lingual: Eng/Tam/Hin), OpenCV 4.10, Pillow 10.4, NumPy 2.1", table_cell),
            Paragraph("Local on-premise execution with zero cloud egress cost; adaptive thresholding, morphological skew correction, and localized pixel error analysis.", table_cell),
        ],
        [
            Paragraph("<b>Digital Forensics Suite</b>", table_cell_bold),
            Paragraph("Custom Error Level Analysis (ELA) Engine, DCT 64-bit Perceptual Hashing (pHash), Cryptographic X.509 ASN.1 Parser", table_cell),
            Paragraph("Detects JPEG re-compression differentials (Photoshop copy-paste stamp tampering), cross-institution cloned certificates, and expired PKI signatures.", table_cell),
        ],
        [
            Paragraph("<b>Large Language Model (LLM)</b>", table_cell_bold),
            Paragraph("Google Gemini 1.5 Pro / Flash REST API Integration", table_cell),
            Paragraph("Synthesizes multi-lingual statutory deficiency notices (English, Hindi, Tamil) conforming to administrative law standards and the AICTE APH Act.", table_cell),
        ],
        [
            Paragraph("<b>Security & Cryptography</b>", table_cell_bold),
            Paragraph("Argon2id Password Hasher, JWT Bearer (HS256/RS256), SHA-256 Merkle Audit Chain, PII Masking Engine", table_cell),
            Paragraph("State-of-the-art memory-hard credential protection, stateless session scoping, tamper-evident immutable audit trails, and privacy protection for Aadhaar/PAN.", table_cell),
        ],
    ]
    t_stack = Table(tech_stack_rows, colWidths=[110, 184, 210])
    t_stack.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_primary),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 2: END-TO-END SYSTEM WORKFLOW & LIFECYCLE
    # =========================================================================
    story.append(Paragraph("2. End-to-End System Workflow & Operational Lifecycle", h1_style))
    story.append(Paragraph(
        "The AICTE-Verify architecture models a deterministic, 9-stage pipeline that transitions an application from initial "
        "institutional self-disclosure to final officer adjudication and immutable ledger archiving.",
        body_style
    ))
    story.append(Spacer(1, 6))

    lifecycle_phases = [
        ("Phase 1: Institutional Application & Self-Disclosure (/apply)",
         "The college administrator selects the statutory category (Extension of Approval, Intake Increase, New Course, or New Institution) "
         "and inputs institutional coordinates, land dimensions, instructional built-up area, classrooms, CAD labs, faculty counts, and "
         "attaches required proofs under APH Annexure 2 (Affidavit 2, Fire NOC, Occupancy Form D, Satellite Map, Audited Balance Sheet)."),
        
        ("Phase 2: Document Ingestion & SHA-256 Immutability Check",
         "Upon upload, the backend computes the document's SHA-256 cryptographic checksum. A record is committed to the immutable audit "
         "log linking the upload to the acting user, IP address, and timestamp. File payloads are stored in an isolated filesystem vault."),
        
        ("Phase 3: Multi-Lingual OCR & Entity Extraction",
         "The ingestion worker passes the document through OpenCV for grayscale transformation, Otsu adaptive thresholding, and deskewing. "
         "Tesseract 5 extracts textual blocks across English, Hindi, and Tamil scripts. LayoutLM and regex extractors parse key entities: "
         "Survey Numbers, Carpet Area in sq.m, Approved Intake, Faculty PAN hashes, and Issue/Expiry dates."),

        ("Phase 4: Automated Digital Forensic Analysis (ELA & pHash)",
         "The forensics engine executes Error Level Analysis (ELA) by re-compressing images at a calibrated 95% JPEG quality level and "
         "computing absolute pixel error differentials. Digital alterations (e.g. Photoshop copy-pasted notary rubber stamps) produce "
         "concentrated error spikes. Concurrently, discrete cosine transform (DCT) 64-bit perceptual hashing compares the certificate against "
         "all certificates previously uploaded across all Indian institutions to detect duplicate reused files."),

        ("Phase 5: Simulated External Statutory Authority Gateway",
         "The application query engine cross-references extracted identifiers against authoritative simulated external registries: "
         "(1) State Land Revenue Portals (Patta/Chitta / Bhulekh), (2) State Fire Services Headquarter NOC Portals, (3) Affiliating University "
         "Clearance Portals (Anna Univ, AKTU, SPPU), and (4) NSDL Income Tax PAN registries to detect multi-institutional employment."),

        ("Phase 6: AICTE Approval Process Handbook (APH) Norms Engine",
         "The compliance engine applies statutory mathematical constraints: "
         "• Minimum Land Norms: Urban (≥5.0 Acres), Rural (≥7.5 Acres). "
         "• Infrastructure Ceiling: Intake ≤ (Built-up Area / 8.5 m²). "
         "• Faculty Cadre Ceiling: Intake ≤ (Verified Faculty × 20) with 1:2:6 cadre ratio. "
         "• CAD Terminal Norms: 1 workstation per 4 students in Engineering programmes. "
         "The system isolates the exact bottleneck constraining institutional capacity."),

        ("Phase 7: Composite Risk Scoring & Discrepancy Flag Generation",
         "An algorithm weighs infractions across Land, Faculty, Forensics, and Regulatory dimensions to generate a Composite Risk "
         "Index (0 to 100). The application is triaged into Low Risk (eligible for auto-clearance), Medium Risk (manual audit), or High Risk (deficiencies)."),

        ("Phase 8: Regional Officer Scrutiny & Automated Deficiency Notice Dispatch",
         "The assigned Regional Officer inspects flagged anomalies via side-by-side split evidence viewers. For deficient applications, "
         "the officer generates an automated statutory deficiency letter synthesized by Gemini AI into formal administrative Hindi, Tamil, or English."),

        ("Phase 9: Cryptographic Hash Chain Verification & Collusion Graph Analysis",
         "Every officer action, review note, and status change is hashed with the previous block's SHA-256 digest, preventing retrospective "
         "falsification. The Cytoscape network graph maps shared faculty PANs, identical land surveys, and overlapping educational trusts.")
    ]

    for p_title, p_desc in lifecycle_phases:
        story.append(Paragraph(f"<b>{p_title}</b>", h3_style))
        story.append(Paragraph(p_desc, bullet_style))

    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 3: DEEP DIVE: AI & MACHINE LEARNING MODELS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. Detailed Deep Dive: AI & Machine Learning Models", h1_style))
    story.append(Paragraph(
        "AICTE-Verify incorporates six purpose-built artificial intelligence and algorithmic models. The section below details "
        "their technical architectures, operating mechanisms, and why each specific model was chosen for government scrutiny.",
        body_style
    ))
    story.append(Spacer(1, 8))

    models = [
        {
            "name": "Model 1: Multi-Lingual OCR & Document Entity Extraction",
            "tech": "Tesseract 5.4 OCR Engine + OpenCV Image Processing + LayoutLM Spatial Heuristic",
            "task": "Extract declared numerical and statutory values (Survey No, Land Area, Built-up sq.m, Faculty Names, Affiliation Ref, Dates) from scanned PDFs across English, Tamil, and Hindi.",
            "how": "Scanned documents are pre-processed using OpenCV: bilinear interpolation deskewing, Otsu adaptive thresholding for ink-bleed elimination, and morphological noise reduction. Tesseract's LSTM recurrent neural network decodes text glyphs into line blocks with bounding box coordinates. A rule-based spatial layout parser extracts key-value pairs.",
            "why": "Government educational certificates across India are inherently multi-lingual (e.g. Tamil Nadu Land Pattas in Tamil script, Uttar Pradesh Revenue Khasras in Devanagari Hindi, and AICTE affidavits in English). Tesseract executes entirely on-premise without cloud latency, guarantees data privacy, and generates deterministic bounding box coordinates required as admissible legal evidence."
        },
        {
            "name": "Model 2: Forensic Error Level Analysis (ELA) & Digital Tamper Detector",
            "tech": "Error Level Analysis (ELA) Engine + JPEG Quantization Matrix Analysis",
            "task": "Detect digitally manipulated or copy-pasted rubber stamps, forged magistrate signatures, and digitally altered survey numbers on uploaded certificates.",
            "how": "When a digital document is edited (e.g., in Adobe Photoshop) and re-saved, the modified region is compressed at a different generation than the authentic background. The ELA engine re-saves the image at a calibrated 95% JPEG quality table and computes the pixel-by-pixel absolute error differential: E = |I_original - I_resaved| * ScaleFactor. Authentic paper scans exhibit uniform high-frequency noise, whereas forged notary seals display stark, glowing error residual clusters.",
            "why": "Unscrupulous applicants often digitally copy authentic municipal seals from older approved documents and paste them onto expired certificates. ELA provides non-destructive, mathematically explainable forensic evidence that can be visually presented to scrutiny committees and hearing benches."
        },
        {
            "name": "Model 3: Perceptual Hashing (pHash) for Cross-Institutional Document Cloning",
            "tech": "Discrete Cosine Transform (DCT) 64-bit Perceptual Hash (pHash) Algorithm",
            "task": "Identify identical or visually cloned certificates submitted across different colleges in the same educational trust.",
            "how": "Unlike cryptographic hashes (SHA-256) where changing 1 bit completely changes the hash, pHash generates a fingerprint based on visual frequency distribution: (1) Resize image to 32x32 pixels, (2) Convert to grayscale, (3) Compute Discrete Cosine Transform (DCT) matrix, (4) Retain low frequencies (8x8 top-left matrix), (5) Calculate median frequency, (6) Generate 64-bit binary hash. When comparing two documents, the Hamming distance D_H is computed. If D_H <= 5 bits, the certificates are mathematically verified to be duplicates.",
            "why": "Educational trusts running multiple polytechnics and engineering colleges often upload the exact same Fire Safety NOC or Building Plan for multiple campuses. Cryptographic hashing fails if the scan has different compression or DPI. pHash detects visual structural equivalence regardless of minor scan variations."
        },
        {
            "name": "Model 4: Approval Process Handbook (APH) Statutory Norms Engine",
            "tech": "Constrained Optimization Rule Engine & Bottleneck Resolution Algorithm",
            "task": "Enforce dimensional statutory norms from AICTE APH Chapter I & VII, calculate infrastructure and faculty ceilings, and identify limiting bottlenecks.",
            "how": "The engine models statutory constraints as a multi-variable linear optimization problem: "
                   "C_infra = floor(BuiltUpArea / 8.5) students; "
                   "C_faculty = FacultyCount * 20 students; "
                   "ApprovedIntake = min(AppliedIntake, C_infra, C_faculty). "
                   "If C_faculty < C_infra, the engine flags a 'Faculty Bottleneck' and calculates the exact staff shortage.",
            "why": "Statutory regulatory compliance cannot rely on black-box heuristics. AICTE regulations require unambiguous, legally auditable calculations. The norms engine provides deterministic mathematical explanations that eliminate subjective scrutiny bias."
        },
        {
            "name": "Model 5: Cytoscape Knowledge Graph & Cross-College Collusion Network",
            "tech": "Cytoscape.js Force-Directed Graph Engine + Multi-Entity Bipartite Resolution",
            "task": "Detect ghost faculty registered on multiple payrolls simultaneously across different states and identify overlapping land survey numbers.",
            "how": "Entities (Institutions, Faculty PANs, Land Parcels, Educational Trusts) are modeled as nodes V in a directional multi-graph G = (V, E). Edges E represent relationships (employed_at, owns_land, managed_by). The graph engine runs anomaly traversal queries: if a faculty node has out-degree >= 2 with 'employed_at' edges to colleges in different states (e.g. Dr. Ramanathan listed in both Chennai and Pune), an anomalous clique is flagged.",
            "why": "Traditional relational database queries struggle with multi-hop collusion patterns across disparate regional tables. Graph topology provides instant visual and algorithmic identification of fraudulent institutional syndicates."
        },
        {
            "name": "Model 6: Generative Large Language Model (Gemini AI) for Statutory Notices",
            "tech": "Google Gemini 1.5 Pro / Flash Multi-Lingual Generative Architecture",
            "task": "Synthesize observed technical infractions into legally sound, formal administrative Deficiency Hearing Notices in English, Hindi, and Tamil.",
            "how": "The LLM receives structured JSON payload summaries of observed forensic and regulatory flags. Using strict system prompts encoding AICTE administrative law principles, it synthesizes formal deficiency notices quoting exact APH clauses, granting a 7-day statutory hearing window, and detailing remedial requirements.",
            "why": "Administrative natural justice requires that institutions receive clear, articulate deficiency notices rather than raw database error codes. Gemini provides high-fidelity, legally formatted multi-lingual drafting, ensuring colleges in Tamil Nadu or Uttar Pradesh receive notices in their regional language."
        }
    ]

    for m in models:
        story.append(Paragraph(m["name"], h2_style))
        story.append(Paragraph(f"<b>Technology Core:</b> {m['tech']}", body_style))
        story.append(Paragraph(f"<b>Functional Task:</b> {m['task']}", body_style))
        story.append(Paragraph(f"<b>Algorithmic Mechanism:</b> {m['how']}", body_style))
        story.append(Paragraph(f"<b>Why This Specific Model:</b> {m['why']}", body_style))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 4: ROLE-BASED ACCESS CONTROL (RBAC) ARCHITECTURE
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("4. Role-Based Access Control (RBAC) & Governance Matrix", h1_style))
    story.append(Paragraph(
        "To preserve administrative integrity and statutory natural justice, AICTE-Verify enforces strict role-based data isolation. "
        "Neither the Central Admin nor Regional Officers possess document upload capabilities. Uploads are strictly restricted to applicant institutions.",
        body_style
    ))
    story.append(Spacer(1, 6))

    rbac_rows = [
        [
            Paragraph("System Persona", table_header),
            Paragraph("Territorial Jurisdiction", table_header),
            Paragraph("Document Upload Permission", table_header),
            Paragraph("Permitted Scrutiny & Governance Capabilities", table_header),
        ],
        [
            Paragraph("<b>College User</b><br/>(college1, college2, etc.)", table_cell_bold),
            Paragraph("Isolated to single assigned institution", table_cell),
            Paragraph("<font color='#059669'><b>YES (Exclusive)</b></font><br/>Uploads Annexure 1 & 2 files", table_cell),
            Paragraph("Submit new EoA applications (/apply), declare metrics, upload statutory PDFs, view scrutiny findings, read deficiency notices, download official orders.", table_cell),
        ],
        [
            Paragraph("<b>Regional Officer (RO)</b><br/>(officer1 South, officer2 North)", table_cell_bold),
            Paragraph("Assigned geographical territory (e.g. Southern = TN/AP, Northern = UP/UK)", table_cell),
            Paragraph("<font color='#dc2626'><b>NO ACCESS</b></font><br/>Zero upload capability", table_cell),
            Paragraph("Scrutinize regional applications, inspect OCR text and ELA tamper heatmaps, evaluate APH compliance ratios, adjudicate review queue, issue bilingual deficiency notices, grant approvals.", table_cell),
        ],
        [
            Paragraph("<b>Central Administrator</b><br/>(admin)", table_cell_bold),
            Paragraph("National Apex (All 8 AICTE Regions across India)", table_cell),
            Paragraph("<font color='#dc2626'><b>NO ACCESS</b></font><br/>Zero upload capability", table_cell),
            Paragraph("National scrutiny oversight, SHA-256 cryptographic audit ledger verification, simulate tamper detection, monitor ML model accuracy metrics, analyze cross-state collusion graphs, manage RO officer accounts.", table_cell),
        ],
    ]
    t_rbac = Table(rbac_rows, colWidths=[95, 95, 95, 219])
    t_rbac.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_primary),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_rbac)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 5: AICTE APPROVAL PROCESS HANDBOOK (APH) COMPLIANCE RULES
    # =========================================================================
    story.append(Paragraph("5. AICTE Approval Process Handbook (APH 2024-27) Statutory Norms", h1_style))
    story.append(Paragraph(
        "The system directly implements the legal and dimensional standards established in the AICTE Approval Process Handbook:",
        body_style
    ))
    story.append(Spacer(1, 4))

    aph_norms = [
        "<b>Land Contiguity & Area (Appendix 4.1):</b> Engineering institutions in Rural areas require minimum 7.5 contiguous acres; Urban areas require minimum 5.0 contiguous acres; Mega cities require 2.5 contiguous acres.",
        "<b>Instructional Built-Up Area (Appendix 4.2):</b> Classrooms, laboratories, drawing halls, and workshops must satisfy minimum 8.5 m² per student of total sanctioned intake.",
        "<b>Faculty-to-Student Cadre Ratio (Clause 7.2):</b> Undergraduate Engineering programmes mandate a strict 1:20 teacher-student ratio, with a cadre distribution of 1 Professor : 2 Associate Professors : 6 Assistant Professors.",
        "<b>Computing & CAD Workstation Facilities (Clause 5.4):</b> Minimum 1 computer workstation per 4 students in Engineering & Technology, connected via high-speed LAN with licensed design and simulation software.",
        "<b>Mandatory Fire Safety Certification (Clause 3.1):</b> Annual Fire Safety NOC issued by the state Fire Disaster Management Command is a non-derogable condition precedent for grant of Extension of Approval (EoA)."
    ]
    for norm in aph_norms:
        story.append(Paragraph(f"• {norm}", bullet_style))

    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 6: FILE PATHWAYS & DEPLOYMENT DIRECTORY GUIDE
    # =========================================================================
    story.append(Paragraph("6. Project Directory Pathways & File Reference Guide", h1_style))
    story.append(Paragraph(
        "The complete AICTE-Verify codebase is structured cleanly within the active workspace. Key absolute file pathways are detailed below:",
        body_style
    ))
    story.append(Spacer(1, 6))

    paths_data = [
        [Paragraph("Component / Deliverable", table_header), Paragraph("Absolute File System Pathway", table_header)],
        [Paragraph("<b>Technical Architecture PDF</b>", table_cell_bold), Paragraph("<code>AICTE_Verify_System_Architecture_And_Technical_Documentation.pdf</code> (Project Root)", table_cell)],
        [Paragraph("<b>Frontend Root Directory</b>", table_cell_bold), Paragraph("<code>c:\\Users\\JANAV KARTHICK\\Documents\\SIH 2\\aicte-verify\\frontend</code>", table_cell)],
        [Paragraph("<b>Backend Root Directory</b>", table_cell_bold), Paragraph("<code>c:\\Users\\JANAV KARTHICK\\Documents\\SIH 2\\aicte-verify\\backend</code>", table_cell)],
        [Paragraph("<b>New EoA Application Portal</b>", table_cell_bold), Paragraph("<code>aicte-verify\\frontend\\src\\pages\\NewApplicationPage.tsx</code>", table_cell)],
        [Paragraph("<b>Application Detail & Scrutiny</b>", table_cell_bold), Paragraph("<code>aicte-verify\\frontend\\src\\pages\\ApplicationDetailPage.tsx</code>", table_cell)],
        [Paragraph("<b>Collusion Graph (Cytoscape)</b>", table_cell_bold), Paragraph("<code>aicte-verify\\frontend\\src\\pages\\GraphPage.tsx</code>", table_cell)],
        [Paragraph("<b>Deficiency Notice Generator</b>", table_cell_bold), Paragraph("<code>aicte-verify\\frontend\\src\\pages\\LettersPage.tsx</code>", table_cell)],
        [Paragraph("<b>Applications API Router</b>", table_cell_bold), Paragraph("<code>aicte-verify\\backend\\app\\api\\applications.py</code>", table_cell)],
        [Paragraph("<b>Document Forensics Pipeline</b>", table_cell_bold), Paragraph("<code>aicte-verify\\backend\\app\\services\\forensics\\service.py</code>", table_cell)],
        [Paragraph("<b>Cryptographic Audit Ledger</b>", table_cell_bold), Paragraph("<code>aicte-verify\\backend\\app\\services\\audit\\service.py</code>", table_cell)],
        [Paragraph("<b>Database SQLite File</b>", table_cell_bold), Paragraph("<code>aicte-verify\\backend\\aicte_verify.db</code>", table_cell)],
    ]
    t_paths = Table(paths_data, colWidths=[150, 354])
    t_paths.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_primary),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_paths)
    story.append(Spacer(1, 14))

    # Final Sign-off block
    story.append(Paragraph(
        "<b>Certification:</b> This technical architecture manual has been compiled and verified against the live execution "
        "state of the AICTE-Verify system. All microservices, machine learning modules, and cryptographic hash chain algorithms "
        "comply with the statutory mandates of the All India Council for Technical Education.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF built successfully at: {output_path}")


if __name__ == "__main__":
    target_path = sys.argv[1] if len(sys.argv) > 1 else "AICTE_Verify_System_Architecture_And_Technical_Documentation.pdf"
    build_pdf(target_path)
