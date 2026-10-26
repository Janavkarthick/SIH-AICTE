# AICTE-Verify Demo Script

## 5-Minute Walkthrough

This script walks through the key features of AICTE-Verify using the seeded synthetic data.

> ⚠️ **All data is SIMULATED. No real institutions, documents, or government records are used.**

### Prerequisites
- Application running: `docker compose up --build` or local dev setup
- Frontend at http://localhost:3000
- Backend API at http://localhost:8000 (Swagger docs at http://127.0.0.1:8000/api/v1/docs)

---

### Step 1: Login as Admin (30 seconds)

1. Open http://localhost:3000
2. Note the advisory banner: "Decision-support only. Final decisions rest with authorised AICTE officials."
3. Login with: **admin / admin123**
4. You'll see the Dashboard with summary cards showing applications, flags, and verification stats.

### Step 2: Explore Applications List (45 seconds)

1. Click **"Applications"** in the sidebar
2. See 18 applications across 6 institutions and 3 academic years
3. Filter by **Risk Level: High** — notice institutions with the most flags
4. Filter by **Category: Extension of Approval**
5. Sort by **Risk Score** descending

### Step 3: Review a Flagged Application (90 seconds)

1. Click on an application for **"Rajiv Gandhi Institute of Technology" (2026)**
2. **Overview tab**: See risk score breakdown — weighted sum of all flags
3. **Documents tab**: See all uploaded documents with status badges
4. **Validation tab**: 
   - Note the **intake mismatch flag**: Application form shows intake 1500 but affidavit shows 1200
   - Each flag shows: code (VAL-001), severity (High), reason, confidence, rule ID
   - Click **"View Evidence"** on a flag
5. **Evidence Viewer**: 
   - See the document page with highlighted bounding box around the mismatched field
   - Toggle between Original / ELA Heatmap view
   - Note the "Advisory Only" badge
6. **Forensics tab**: Review PDF metadata analysis, font consistency checks
7. **Verification tab**: See issuer verification results (SIMULATED)
8. **Compliance tab**: See infrastructure norms comparison — some gaps flagged

### Step 4: Check Ghost Faculty Graph (45 seconds)

1. Click **"Knowledge Graph"** in the sidebar
2. See the interactive Cytoscape graph with institutions, faculty, land, and trusts
3. Notice **red highlighted edges**:
   - FAC011 (Dr. Vikram Singh) connected to both INST001 (Pune) and INST002 (Chennai)
   - Same land survey number shared between INST001 and INST006
4. Click a flagged edge to see the explanation panel
5. Toggle "Show Flagged Only" to filter the view

### Step 5: Review Queue and Officer Actions (45 seconds)

1. Click **"Review Queue"** in the sidebar
2. See items sorted by risk — manual review items first
3. Click on an item requiring manual review
4. As an officer, click **"Resolve Flag"** on a flag
5. A confirmation modal appears: "This action will be logged in the audit trail"
6. Enter a resolution note and confirm
7. The flag is now marked resolved with the officer's name and timestamp

### Step 6: Audit Trail Integrity (30 seconds)

1. Click **"Audit Log"** in the sidebar
2. See the chronological log of all actions
3. Click **"Verify Chain Integrity"** button
4. See the result: "Chain integrity verified — no tampering detected"
5. (Dev mode) Click **"Simulate Tamper"** — modify one entry
6. Click **"Verify Chain Integrity"** again — now it detects the tampered entry

### Step 7: Analytics and Evaluation (30 seconds)

1. Click **"Analytics"** in the sidebar
2. See charts: flags by type (bar), verification outcomes (pie), processing times (line)
3. Click **"Evaluation"** in the sidebar
4. See the pipeline evaluation results: OCR accuracy, detection P/R/F1, processing times
5. Note: These are REAL measured numbers, including limitations

### Step 8: Draft Deficiency Notice & Governance (15 seconds)

1. Return to a flagged application
2. Click **"Generate Draft Deficiency Notice"**
3. Preview the draft notice listing open discrepancies with statutory clause placeholders: `[Clause reference - verify against Approval Process Handbook]`
4. Notice prominent warning banner: `*** DRAFT DEFICIENCY NOTICE - PENDING REGIONAL OFFICER SCRUTINY & APPROVAL ***`
5. Select language template (English, Tamil, or Hindi)
6. Adverse decisions are phrased as **"Recommend rejection"**; the final decision rests exclusively with the competent statutory authority. Recommending rejection requires officer confirmation, a written justification of at least 10 characters, and is cryptographically audit-logged (no automatic email dispatch).

---

### Demo Credentials

| Username | Password | Role | Scope |
|----------|----------|------|-------|
| `admin` | `admin123` | Central Admin | Full access, all regions, user management |
| `officer1` | `officer123` | Regional Officer | Southern Region (OMR / Chennai / Bangalore) |
| `officer2` | `officer123` | Regional Officer | Northern Region (Lucknow / Delhi / Jaipur) |
| `college1` | `college123` | College User | Apex Institute of Technology (PID: 1-100234) |
| `college2` | `college123` | College User | Zenith College of Engineering (PID: 1-100567) |

### Key Points to Highlight

- ✅ **Advisory only**: Every finding explicitly tagged "preliminary indicator — human verification required"
- ✅ **Explainable**: Every flag has code, reason, evidence, confidence, and rule ID (no black-box ML claims)
- ✅ **Auditable**: Every action is cryptographically chained in a SHA-256 tamper-evident audit ledger
- ✅ **No auto-reject / No auto-dispatch**: Officers must confirm every adverse action; phrased as "Recommend rejection", final decision rests with the competent authority
- ✅ **Sister Campus Recognition**: Sister colleges under the same sponsoring trust sharing land are recognized as legitimate sister campuses (INFO). Duplication of full-time faculty across campuses is strictly flagged as ghost faculty (HIGH within same city, CRITICAL across different cities)
- ✅ **Simulated**: All verification services are clearly labelled SIMULATED
- ✅ **Multilingual OCR Status**: Tamil/Hindi OCR is configured in the Docker image but has not been verified end to end.
- ✅ **Configurable**: All normative thresholds stored in JSON config files, easily updated to official Approval Process Handbook updates
