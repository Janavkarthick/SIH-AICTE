# AICTE-Verify Demo Script

## 5-Minute Walkthrough

This script walks through the key features of AICTE-Verify using the seeded synthetic data.

> ⚠️ **All data is SIMULATED. No real institutions, documents, or government records are used.**

### Prerequisites
- Application running: `docker compose up --build` or local dev setup
- Frontend at http://localhost:5173
- Backend at http://localhost:8000

---

### Step 1: Login as Admin (30 seconds)

1. Open http://localhost:5173
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

### Step 8: Deficiency Letter (15 seconds)

1. Return to a flagged application
2. Click **"Generate Deficiency Letter"**
3. Preview the letter listing all open flags and required actions
4. Select language (English/Tamil/Hindi template)
5. Click **"Approve Letter"** (officer action, logged in audit trail)

---

### Demo Credentials

| Username | Password | Role | Scope |
|----------|----------|------|-------|
| admin | admin123 | Admin | Full access, all regions |
| officer1 | officer123 | Officer | West region |
| officer2 | officer123 | Officer | South region |
| college1 | college123 | College User | Own applications only |
| college2 | college123 | College User | Own applications only |

### Key Points to Highlight

- ✅ **Advisory only**: Every flag says "preliminary indicator — human verification required"
- ✅ **Explainable**: Every flag has code, reason, evidence, confidence, and rule ID
- ✅ **Auditable**: Every action is logged in a tamper-evident audit chain
- ✅ **No auto-reject**: Officers must confirm every adverse action
- ✅ **Simulated**: All verification services are clearly labelled SIMULATED
- ✅ **Configurable**: All thresholds in JSON config files, easily replaced with real norms
