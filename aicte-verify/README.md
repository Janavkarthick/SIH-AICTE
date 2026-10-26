# AICTE-Verify

**AI-Powered Application Validation, Document Authentication and Regulatory Compliance Verification**

> ⚠️ **Decision-support only. Final decisions rest with authorised AICTE officials.**
> 
> **DEMO DATA ONLY:** All passwords, seed entities, and cryptographic fixtures are simulated for hackathon evaluation.
> All verification services, institutions, and data in this prototype are **SIMULATED**. This is a hackathon prototype (SIH 2026, PS SIH26261).

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and enter directory
cd aicte-verify

# Copy environment file
cp .env.example .env

# Build and run
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs (Swagger): http://127.0.0.1:8000/api/v1/docs
- OpenAPI JSON: http://127.0.0.1:8000/api/v1/openapi.json

### Option 2: Local Development

#### Prerequisites
- Python 3.12+ (in virtual environment `.venv`)
- Node.js 20+
- Tesseract OCR (Optional for local Windows run; Docker recommended for full multilingual OCR):
  > [!NOTE]
  > **Multilingual OCR Status:** Tamil/Hindi OCR is configured in the Docker image but has not been verified end to end.
  ```bash
  # Ubuntu/Debian
  sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-tam tesseract-ocr-hin
  sudo apt install fonts-noto fonts-noto-cjk
  
  # macOS
  brew install tesseract
  brew install tesseract-lang
  
  # Windows
  # Download from: https://github.com/UB-Mannheim/tesseract/wiki
  # Add to PATH, install eng+tam+hin language packs
  ```

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will automatically:
1. Create the SQLite database
2. Generate synthetic data
3. Seed the database with demo data

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Option 3: Docker with PostgreSQL
```bash
docker compose --profile postgres up --build
```
Set `DATABASE_URL=postgresql://aicte:aicte_verify_dev@postgres:5432/aicte_verify` in `.env`.

## Demo Credentials

| Username | Password | Role | Region / Scope |
|----------|----------|------|----------------|
| `admin` | `admin123` | Central Admin | Full access, all regions, user management |
| `officer1` | `officer123` | Regional Officer | Southern Region (OMR / Chennai / Bangalore) |
| `officer2` | `officer123` | Regional Officer | Northern Region (Lucknow / Delhi / Jaipur) |
| `college1` | `college123` | College User | Apex Institute of Technology (PID: 1-100234) |
| `college2` | `college123` | College User | Zenith College of Engineering (PID: 1-100567) |

## Features

### Core Features
- **C1. Application Validation**: Checklist-based validation per Approval Process Handbook category with configurable 30-day grace periods.
- **C2. Classification & Entity Extraction**: Deterministic rule-based regex scoring across 11 statutory categories + Tesseract OCR (English/Tamil/Hindi) + PyMuPDF text fallback.
- **C3. Forensics Suite**: PDF metadata revision inspection (distinguishing compressor utilities from image editors), font consistency analysis, ELA visual inspection aid, copy-move duplication detection, and pyHanko cryptographic integrity check.
- **C4. Verification**: SIMULATED issuer verification with all 6 statutory statuses (`verified`, `mismatch_detected`, `expired`, `verification_pending`, `source_unavailable`, `manual_review_required`).
- **C5. Compliance Engine**: APH built-up infrastructure norms, classroom/lab capacity solver, and geofenced photo compliance.
- **C6. Review Dashboard**: Risk-scored queue (0-100 score with weighted breakdown, uncalibrated heuristic thresholds), alerts, and immutable hash-chained audit log.
- **C7. Evidence Viewer**: Interactive document viewer with bounding box callouts, ELA overlay toggles, and preliminary indicator advisory tags.
- **C8. Institutional Safeguards**: Role-based access control, PII masking (Aadhaar/phone), tamper-evident audit trails, and officer confirmation workflows.

### Differentiator Features
- **A1. Capacity & Deficit Solver**: Computes maximum intake capacity directly from instructional built-up area and faculty roster.
- **A2. YoY Intake Jump Detector**: Flags uncalibrated >100% year-over-year intake jumps without infrastructure expansion.
- **A3. Multi-Campus Collusion Graph**: Cytoscape.js visual graph detecting ghost faculty (shared across cities) and shared land parcels, with intelligent sponsoring trust resolution (sister campuses under the same trust are not flagged as collusion).
- **A4. Draft Deficiency Notices**: Tri-lingual (English, Tamil, Hindi) deficiency notice drafts with statutory clause references requiring explicit officer scrutiny, confirmation, and written justification before status updates.
- **A5. Hash-Chained Audit Ledger**: Cryptographically chained SHA-256 ledger recording every officer action, flag resolution, and application decision.

## System Limitations & Transparency

> [!WARNING]
> **Key Limitations & Operating Boundaries:**
> 1. **Skilled-Forger Bypass**: Flattening PDFs to raster scans or stripping metadata eliminates digital editing artifacts. Digital heuristics (metadata, font splices) are preliminary advisory signals, not silver bullets; absolute authenticity relies on cryptographic issuer verification (e.g. DigiLocker APIs).
> 2. **Simulated Issuing Authorities**: Third-party verification (state technical education depts, fire authorities, municipal corporations) is simulated via an internal mock issuer registry. Real deployment requires production API integrations.
> 3. **Illustrative Normative Thresholds**: Area requirements, faculty ratios, and intake bounds are illustrative administrative heuristics calibrated to the 2024-27 Approval Process Handbook; actual approvals depend on expert scrutiny committee evaluations.
> 4. **Synthetic-Only Benchmark**: The evaluation suite evaluates against 285 synthetic test units with neutral IDs (`DOC_0001`..`DOC_0295`) to prevent data leakage. Real-world documents exhibit physical paper textures, skewed scans, and hand-inked notary stamps requiring human-in-the-loop review.
> 5. **Document Classification**: Operates via deterministic statutory keyword and regex scoring across 11 statutory categories (no black-box machine learning).
> 6. **Deficiency Notices & Adverse Recommendations**: Deficiency notices are strictly generated as **DRAFT DEFICIENCY NOTICES** with statutory clause placeholders requiring regional officer scrutiny and approval; no letters are dispatched automatically. Adverse decisions are phrased as **"Recommend rejection"**; the final decision rests exclusively with the competent statutory authority. Recommending rejection requires officer confirmation, a written justification of at least 10 characters, and is cryptographically audit-logged.
> 7. **Sister Campuses vs Collusion**: Colleges operated under the same sponsoring trust sharing land parcels are recognized as legitimate sister campuses (shared land = INFO). However, duplication of full-time faculty across campuses is strictly flagged as ghost faculty (HIGH within same city, CRITICAL across different cities) because an individual cannot hold simultaneous full-time teaching appointments.

## Project Structure

```
aicte-verify/
├── docker-compose.yml
├── .env.example
├── README.md
├── config/rules/           # Configurable validation rules
│   ├── checklists.json     # Document requirements per category
│   ├── norms.json          # Infrastructure/faculty norms
│   └── doc_validity.json   # Document validity periods
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py         # FastAPI application
│       ├── core/           # Config, DB, security, audit
│       ├── models/         # SQLAlchemy models
│       ├── schemas/        # Pydantic v2 schemas
│       ├── api/            # API route handlers
│       ├── services/       # Business logic services
│       ├── mock_issuer/    # SIMULATED verification service
│       └── seed/           # Database seeding
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── pages/          # Page components
│       ├── components/     # Reusable UI components
│       └── api/            # API client
├── data/
│   ├── synthetic/          # Generated test data + ground truth
│   ├── handbook/           # AICTE handbook (if available)
│   └── uploads/            # User uploads
├── scripts/
│   ├── generate_synthetic.py  # Synthetic data generator
│   ├── seed_db.py            # Database seeder
│   └── evaluate.py           # Pipeline evaluation
└── docs/
    ├── ARCHITECTURE.md
    ├── ASSUMPTIONS.md
    ├── DEMO_SCRIPT.md
    ├── API.md
    └── EVAL.md
```

## Configuration

All validation rules are in `config/rules/`:
- **checklists.json**: Required documents per application category
- **norms.json**: Infrastructure, faculty, and intake norms
- **doc_validity.json**: Document validity/expiry periods

> All values are **illustrative** — replace with actual Approval Process Handbook values.

## API Documentation

- Swagger UI: http://127.0.0.1:8000/api/v1/docs
- OpenAPI JSON: http://127.0.0.1:8000/api/v1/openapi.json
- See [docs/API.md](docs/API.md) for detailed endpoint documentation

## Testing

```bash
cd backend
pytest tests/ -v
```

## Evaluation

```bash
# With the backend running:
python scripts/evaluate.py
```

Results are saved to `docs/EVAL.md` and available at the in-app Evaluation page.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design, pipeline flow, data model
- [Assumptions](docs/ASSUMPTIONS.md) - All assumptions and known limitations
- [Demo Script](docs/DEMO_SCRIPT.md) - 5-minute walkthrough
- [API](docs/API.md) - API endpoints reference
- [Evaluation](docs/EVAL.md) - Pipeline evaluation metrics

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Pydantic v2 |
| Frontend | React 18, Vite 5, TypeScript, Tailwind CSS |
| OCR | Tesseract (eng+tam+hin), PyMuPDF |
| Forensics | OpenCV, Pillow, imagehash, pyHanko, scikit-image |
| Graph | NetworkX (backend), Cytoscape.js (frontend) |
| Charts | Recharts |
| Auth | JWT (PyJWT), Argon2 |
| Database | SQLite (default) / PostgreSQL |
| Deployment | Docker Compose |

## License

This is a hackathon prototype. Not licensed for production use.

---

**Smart India Hackathon 2026 | PS SIH26261 | AICTE**
