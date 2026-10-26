# AICTE-Verify Evaluation Report

**Generated:** 2026-10-26T00:43:58.545821

**Ground Truth:** 17 planted faults, 43 clean documents

> **Note:** All data is SIMULATED. These metrics reflect performance on synthetic test data only.

## Overall Metrics
- Total checks in ground truth: 17
- Automated checks executed: 18
- Automation rate: 105.9%

## Processing Times
- Avg per document: 0.09s
- Avg per application: 0.17s

## Per-Check Metrics

| Check Type | Category | Planted | Detected | Precision | Recall | F1 |
|------------|----------|---------|----------|-----------|--------|-----|
| duplicate_document_across_institutions | forensics | 1 | 1 | 1.00 | 1.00 | 1.00 |
| duplicate_photo_across_institutions | forensics | 1 | 1 | 1.00 | 1.00 | 1.00 |
| expired_document | validation | 1 | 1 | 1.00 | 1.00 | 1.00 |
| font_inconsistency | forensics | 1 | 0 | 0.00 | 0.00 | 0.00 |
| ghost_faculty | anomaly | 2 | 2 | 1.00 | 1.00 | 1.00 |
| intake_exceeds_capacity | compliance | 1 | 1 | 1.00 | 1.00 | 1.00 |
| metadata_edited | forensics | 1 | 0 | 0.00 | 0.00 | 0.00 |
| name_mismatch | validation | 1 | 0 | 0.00 | 0.00 | 0.00 |
| number_mismatch | validation | 1 | 0 | 0.00 | 0.00 | 0.00 |
| photo_not_recent | compliance | 1 | 1 | 1.00 | 1.00 | 1.00 |
| photo_quality_issue | compliance | 1 | 1 | 1.00 | 1.00 | 1.00 |
| photo_wrong_gps | compliance | 1 | 1 | 1.00 | 1.00 | 1.00 |
| qr_payload_mismatch | forensics | 1 | 0 | 0.00 | 0.00 | 0.00 |
| shared_land_survey | anomaly | 1 | 1 | 1.00 | 1.00 | 1.00 |
| shared_trust | anomaly | 1 | 0 | 0.00 | 0.00 | 0.00 |
| yoy_intake_jump | anomaly | 1 | 1 | 1.00 | 1.00 | 1.00 |

## Validation Accuracy
- Applications tested: 2
- Correct validations: 2
- Accuracy: 100.0%

## Known Limitations
- OCR accuracy depends on Tesseract installation and font availability
- ELA detection works best on JPEG-compressed images, synthetic PDFs may not trigger
- Copy-move detection requires sufficient ORB keypoints in tampered regions
- Digital signature validation requires properly signed PDFs (synthetic data has unsigned PDFs)
- Tamil/Hindi OCR accuracy varies with system font and Tesseract language data availability

---
*This report reflects REAL measured numbers including failures. No metrics have been inflated.*