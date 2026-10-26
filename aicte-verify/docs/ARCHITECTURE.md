# AICTE-Verify Architecture

## Overview

AICTE-Verify is a decision-support platform for AICTE officers that validates institution applications and supporting documents using AI-powered analysis. **All AI output is advisory only; human officers make every final decision.**

## System Architecture

```mermaid
flowchart TD
    subgraph Frontend["Frontend (React + Vite + TypeScript)"]
        UI[Dashboard / Pages]
        EV[Evidence Viewer]
        GV[Graph Viewer - Cytoscape.js]
        CH[Charts - Recharts]
    end

    subgraph Backend["Backend (FastAPI + Python 3.12)"]
        API[API Layer - FastAPI Routes]
        AUTH[Auth - JWT + Argon2 + RBAC]
        
        subgraph Pipeline["Document Processing Pipeline"]
            OCR[OCR Service - Tesseract/PyMuPDF]
            CLS[Classifier - Rule/Keyword]
            EXT[Extractor - Regex/Keyword]
        end
        
        subgraph Analysis["Analysis Services"]
            VAL[Validator - Checklist Engine]
            FOR[Forensics - PDF/Image Analysis]
            VER[Verifier - Issuer Lookup]
            COM[Compliance - Rule Engine]
            GRA[Graph Builder - NetworkX]
            RSK[Risk Scorer]
        end
        
        subgraph Support["Support Services"]
            AUD[Audit Logger - Hash Chain]
            EVD[Evidence Builder]
            LET[Letter Generator - Jinja2]
        end
        
        MOCK[Mock Issuer Service - SIMULATED]
    end

    subgraph Data["Data Layer"]
        DB[(SQLite / PostgreSQL)]
        FS[File Storage]
        CFG[Config Rules - JSON]
    end

    UI --> API
    EV --> API
    GV --> API
    API --> AUTH
    API --> Pipeline
    API --> Analysis
    API --> Support
    API --> MOCK
    Pipeline --> DB
    Analysis --> DB
    Analysis --> CFG
    Support --> DB
    MOCK --> DB
```

## Pipeline Flow

```mermaid
flowchart LR
    A[Upload PDF/Image] --> B[Preprocess - OpenCV]
    B --> C{Native Text?}
    C -->|Yes| D[PyMuPDF Extract]
    C -->|No| E[Tesseract OCR]
    D --> F[Classify Document]
    E --> F
    F --> G[Extract Fields]
    G --> H[Validate Against Checklist]
    H --> I[Run Forensics Checks]
    I --> J[Verify with Issuer]
    J --> K[Check Compliance]
    K --> L[Compute Risk Score]
    L --> M[Generate Flags & Evidence]
```

## Module Responsibilities

| Module | Responsibility | Status |
|--------|---------------|--------|
| `core/config.py` | Application settings from .env | Implemented |
| `core/database.py` | SQLAlchemy engine, session, Base | Implemented |
| `core/security.py` | JWT auth, password hashing, RBAC, PII masking | Implemented |
| `core/audit.py` | Append-only audit chain with SHA-256 integrity | Implemented |
| `services/ocr/` | OCR pipeline: preprocess → extract text | Implemented |
| `services/classify/` | Rule+keyword document type classification | Implemented |
| `services/extract/` | Field extraction via regex + keyword anchoring | Implemented |
| `services/validate/` | Checklist validation, cross-doc consistency | Implemented |
| `services/forensics/` | PDF metadata, font analysis, ELA, copy-move, signatures, duplicates | Implemented |
| `services/verify/` | Verification adapter + mock issuer integration | Implemented |
| `services/compliance/` | Infrastructure norms, photo checks, capacity calculator | Implemented |
| `services/graph/` | Knowledge graph: ghost faculty, shared land/trust detection | Implemented |
| `services/risk/` | Weighted risk scoring with breakdown | Implemented |
| `services/letters/` | Jinja2 deficiency letter generation + optional Gemini | Implemented |
| `services/evidence/` | Evidence page rendering with highlights & overlays | Implemented |
| `mock_issuer/` | SIMULATED issuing authority verification service | Implemented |

## Simulated vs Real Components

| Component | Current Status | Real Integration Path |
|-----------|---------------|----------------------|
| Issuer verification | **SIMULATED** mock service | Replace adapter with real API clients |
| University affiliation check | **SIMULATED** | Integrate with university systems |
| Fire safety verification | **SIMULATED** | Connect to state fire department APIs |
| Accreditation check | **SIMULATED** | Connect to NBA/NAAC systems |
| Outside signals (A8) | **SIMULATED** local JSON | Connect to real accreditation/ranking databases |
| OCR | Real (Tesseract) | Could upgrade to cloud OCR for better accuracy |
| Forensics | Real (heuristic) | Could add ML-based forgery detection |
| Digital signatures | Real (pyHanko) | Works with real PKI certificates |

## Security Model

- **Authentication**: JWT tokens with configurable expiry
- **Password Storage**: Argon2 hashing (OWASP recommended)
- **Authorization**: Role-based access control (admin, officer, college_user)
- **PII Protection**: Automatic masking of Aadhaar-like numbers and phone numbers
- **Audit Trail**: Append-only with SHA-256 hash chain for tamper detection
- **Upload Security**: Type validation, size limits, filename sanitization

## Data Model

```mermaid
erDiagram
    User ||--o{ Application : submits
    User ||--o{ Application : reviews
    Institution ||--o{ Application : has
    Application ||--o{ Document : contains
    Application ||--o{ Flag : has
    Application ||--o{ ComplianceResult : has
    Document ||--o{ ExtractedData : has
    Document ||--o{ Flag : triggers
    Document ||--o{ VerificationResult : has
    Document ||--o{ DocumentClassification : has
    User ||--o{ AuditEntry : performs
    GraphEntity ||--o{ GraphRelation : source
    GraphEntity ||--o{ GraphRelation : target
```

## Future Scope (Not Implemented)

- **Satellite imagery verification**: Cross-reference campus images with satellite data
- **Full native inspector app**: Mobile app for physical inspection workflows
- **Real DigiLocker integration**: Verify documents through DigiLocker API
- **Real university system integration**: Direct affiliation verification
- **Real AICTE system integration**: Pull application data from AICTE portal
- **ML-based document classification**: Deep learning model for complex layouts
- **Advanced forgery detection**: GAN-based or deep learning forgery detectors
- **Multi-language NLP**: Named entity recognition for Indian languages
- **Workflow automation**: Automated routing and escalation based on rules
- **Digital certificate issuance**: Issue verified certificates with digital signatures
