# AICTE-Verify Assumptions

All assumptions made during development are documented here.

## Architecture Assumptions

1. **Prototype scope**: This is a decision-support prototype, not a production system. SQLite is the default database for simplicity; PostgreSQL is supported via `DATABASE_URL` env variable.

2. **No real government integrations**: All issuing-authority verification is SIMULATED using mock services within the application. The adapter interface is designed for real integration replacement later.

3. **No real AICTE norms**: All thresholds (faculty ratios, area requirements, lab counts, intake limits) are illustrative values stored in `config/rules/*.json`. These MUST be replaced with actual Approval Process Handbook values before any real use.

4. **Synchronous processing**: Document processing (OCR, forensics, verification) runs synchronously for simplicity. A production system would use a task queue (Celery/RQ).

5. **Single-server deployment**: The prototype runs on a single server. No horizontal scaling, CDN, or load balancing is implemented.

## Technology Assumptions

6. **Tesseract OCR**: We assume Tesseract is installed with `eng`, `tam`, and `hin` language packs. Docker image includes these. For local development, Tesseract must be installed separately.

7. **Font availability**: Noto Sans, Noto Sans Tamil, and Noto Sans Devanagari fonts are installed in the Docker image for proper rendering of multilingual documents. Local development may have different fonts available.

8. **OpenCV without GUI**: We use `opencv-python-headless` to avoid X11 dependency issues in Docker/server environments.

9. **PyMuPDF (fitz)**: Used for native PDF text extraction and page rendering. Preferred over poppler-based solutions for cross-platform compatibility.

10. **pyHanko for signatures**: Digital signature validation uses pyHanko. Synthetic PDFs are unsigned; signature validation is tested against known-absent and known-invalid scenarios.

11. **No zbar dependency**: QR code reading uses OpenCV's QRCodeDetector instead of pyzbar/zbar to avoid native library dependency issues.

12. **Argon2 password hashing**: Using argon2-cffi for password hashing (OWASP recommended). Falls back gracefully if system doesn't support hardware acceleration.

## Data Assumptions

13. **All data is synthetic**: No real institutions, persons, certificates, or government records are used. All names, IDs, and addresses are fictional.

14. **Ground truth is complete**: The `ground_truth.json` file documents all planted faults. Evaluation metrics compare against this manifest.

15. **Document format**: Synthetic documents are generated as simple text-based PDFs using ReportLab. Real-world documents would have more complex layouts, stamps, and signatures.

16. **EXIF data**: Infrastructure photos have synthetic EXIF data including GPS coordinates. The `piexif` library is used for EXIF manipulation.

## Feature Assumptions

17. **Risk scoring**: The risk score is a transparent weighted sum of flags. Weights are configurable but illustrative. No ML model is used for risk scoring.

18. **Document classification**: Uses rule-based keyword matching, not deep learning. Adequate for structured government documents but may struggle with unusual layouts.

19. **ELA (Error Level Analysis)**: Works best on JPEG-compressed images. May produce false positives on synthetic PDFs that haven't been through real compression cycles.

20. **Copy-move detection**: Uses ORB keypoints for basic copy-move detection. Not as sophisticated as deep learning approaches but sufficient for obvious duplications.

21. **Ghost faculty detection**: Based on matching faculty IDs across institutions. Doesn't verify actual employment records.

22. **Gemini API integration**: Optional. The app works fully without any API key. When GEMINI_API_KEY is set, it provides an "improve wording" option for deficiency letters only.

23. **No email sending**: Deficiency letters are generated and approved but not actually sent. The system logs the approval action in the audit trail.

## Security Assumptions

24. **Development credentials**: Default JWT secret and demo user passwords are for development only. Must be changed in production.

25. **PII masking**: Aadhaar-like numbers (12 digits) and phone numbers (10 digits starting with 6-9) are masked in logs and UI. Officer reveal action is audited.

26. **File upload security**: Files are validated for type (PDF, JPEG, PNG), size (configurable max), and filename sanitization. No path traversal is possible through the upload API.

27. **Rate limiting**: Auth routes are rate-limited. Other routes are not rate-limited in the prototype.

## Library Version Choices

28. **FastAPI 0.115.x**: Latest stable at development time.
29. **SQLAlchemy 2.0.x**: Using 2.0 style with declarative mappings.
30. **Pydantic v2**: Using model_config = ConfigDict() pattern.
31. **React 18**: Stable version with concurrent features.
32. **Vite 5**: Fast build tool for React development.
33. **Tailwind CSS 3**: Utility-first CSS framework.

## Known Limitations & Operating Boundaries

1. **Skilled-Forger Bypass**: Flattening edited PDFs to raster image scans (or printing and re-scanning) or stripping EXIF/PDF metadata removes digital manipulation artifacts. Digital forensics heuristics (metadata inspection, font splice analysis) are preliminary advisory signals, not absolute guarantees; true authenticity requires cryptographic issuer verification (e.g., DigiLocker integration or issuing authority signature verification).
2. **Simulated Issuing Authorities**: All third-party issuing authorities (State Technical Education Departments, Fire & Emergency Services, Municipal Corporations, Universities) are simulated via an internal mock issuer registry. Production deployment requires live API integration with state portals.
3. **Illustrative Normative Thresholds**: Built-up instructional area requirements, faculty-to-student ratios (1:20), and lab capacity bounds are illustrative administrative heuristics calibrated to the 2024-27 Approval Process Handbook; actual regional council approvals depend on expert scrutiny committee evaluations.
4. **Synthetic-Only Benchmark Evaluation**: The evaluation suite evaluates against 285 synthetic test units with neutral IDs (`DOC_0001`..`DOC_0295`) to prevent data leakage. Real-world document distribution contains varied paper scans, handwritten notary stamps, folded sheets, and low-contrast mobile camera captures requiring human officer scrutiny.
5. **Document Classification**: Operates via deterministic statutory keyword pattern and regex scoring across 11 statutory categories (no black-box machine learning model is claimed or deployed).
6. **Deficiency Notice Governance**: Deficiency notices are strictly generated as **DRAFT DEFICIENCY NOTICES** requiring regional officer review and authorization; no notices are dispatched automatically. Any adverse application status transition to `Rejected` mandates officer confirmation and written justification.
7. **Sister Campus Trust Recognition**: Colleges operating under the same registered educational trust sharing land or faculty are recognized as legitimate sister campuses and not falsely flagged as collusion. Collusion flags are reserved for cross-trust claims across unrelated sponsoring entities.
