# AICTE-Verify

**AI-Powered Application Validation, Document Authentication and Regulatory Compliance Verification**

> ⚠️ **Decision-support only. Final decisions rest with authorised AICTE officials.**
> 
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

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

#### Prerequisites
- Python 3.12+
- Node.js 20+
- Tesseract OCR with language packs:
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

| Username | Password | Role | Access |
|----------|----------|------|--------|
| `admin` | `admin123` | Admin | Full access, all regions, user management |
| `officer1` | `officer123` | Officer | West region applications, review & approve |
| `officer2` | `officer123` | Officer | South region applications, review & approve |
| `college1` | `college123` | College User | Own institution applications only |
| `college2` | `college123` | College User | Own institution applications only |

## Features

### Core Features
- **C1. Application Validation**: Checklist-based validation per application category
- **C2. OCR & Extraction**: Tesseract OCR (English/Tamil/Hindi) + PyMuPDF for native PDFs
- **C3. Forensics**: PDF metadata, font analysis, ELA, copy-move, digital signatures, duplicates
- **C4. Verification**: SIMULATED issuer verification with all 6 statuses
- **C5. Compliance**: Infrastructure norms, photo checks, capacity calculator
- **C6. Dashboard**: Applications, review queue, alerts, analytics, audit log
- **C7. Evidence Viewer**: Document pages with highlights, overlays, and flag details
- **C8. Safeguards**: RBAC, PII masking, audit trail, upload validation

### Add-on Features
- **A1. Capacity Calculator**: Maximum intake from infrastructure
- **A2. YoY Jump Detector**: Flag unexplained intake/faculty jumps
- **A3. Resubmission Diff**: Show changes between versions
- **A4. Deficiency Letters**: Jinja2 templates (EN/TA/HI) + optional Gemini improvement
- **A5. Knowledge Graph**: Ghost faculty, shared land/trust detection with Cytoscape.js
- **A6. Regional OCR**: Tamil and Hindi certificate processing

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

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
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
