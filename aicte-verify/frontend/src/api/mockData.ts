import {
  User,
  Application,
  Document,
  Flag,
  VerificationResult,
  ComplianceResult,
  CapacityCalculation,
  AuditEntry,
  GraphData,
  EvaluationResult,
  Alert,
  DeficiencyLetter,
  AnalyticsSummary,
  ValidationReport,
  TimelineEvent,
  ResubmissionDiff
} from '../types';

export const mockUsers: User[] = [
  {
    id: 'u-1',
    username: 'officer_kumar',
    email: 'rajesh.kumar@aicte-india.org',
    full_name: 'Dr. Rajesh Kumar',
    role: 'officer',
    institution_name: 'AICTE Southern Regional Office',
    created_at: '2024-01-10T10:00:00Z',
  },
  {
    id: 'u-2',
    username: 'scrutiny_priya',
    email: 'priya.sharma@aicte-india.org',
    full_name: 'Priya Sharma',
    role: 'scrutiny_admin',
    institution_name: 'AICTE Scrutiny Cell, New Delhi',
    created_at: '2024-02-15T10:00:00Z',
  },
  {
    id: 'u-3',
    username: 'principal_psg',
    email: 'principal@skce.edu.in',
    full_name: 'Dr. K. Senthil Nathan',
    role: 'college_user',
    institution_name: 'Sri Krishna College of Engineering',
    institution_id: 'inst-001',
    created_at: '2024-03-01T10:00:00Z',
  },
  {
    id: 'u-4',
    username: 'admin',
    email: 'admin@aicte-verify.gov.in',
    full_name: 'System Administrator',
    role: 'admin',
    institution_name: 'AICTE HQ Tech Cell',
    created_at: '2023-11-01T10:00:00Z',
  },
  {
    id: 'u-off1',
    username: 'officer1',
    email: 'officer.south@aicte.gov.in',
    full_name: 'Dr. V. Srinivasan (RO South)',
    role: 'officer',
    institution_name: 'AICTE Southern Regional Office',
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'u-off2',
    username: 'officer2',
    email: 'officer.north@aicte.gov.in',
    full_name: 'Prof. R. K. Sharma (RO North)',
    role: 'officer',
    institution_name: 'AICTE Northern Regional Office',
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'u-off3',
    username: 'officer3',
    email: 'officer.west@aicte.gov.in',
    full_name: 'Dr. A. P. Deshmukh (RO West)',
    role: 'officer',
    institution_name: 'AICTE Western Regional Office',
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'u-clg1',
    username: 'college1',
    email: 'registrar@apextech.edu',
    full_name: 'Registrar, Apex Tech',
    role: 'college_user',
    institution_name: 'Apex Institute of Technology',
    institution_id: '1',
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'u-clg2',
    username: 'college2',
    email: 'dean@zenitheng.edu',
    full_name: 'Dean Admin, Zenith Eng',
    role: 'college_user',
    institution_name: 'Zenith College of Engineering',
    institution_id: '2',
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'u-clg3',
    username: 'college3',
    email: 'registrar@northernpoly.edu',
    full_name: 'Registrar, Northern Poly',
    role: 'college_user',
    institution_name: 'Northern Polytechnic Institute',
    institution_id: '3',
    created_at: '2024-01-01T00:00:00Z',
  },
];

export const mockApplications: Application[] = [
  {
    id: 'app-001',
    application_number: 'AICTE/SRO/2025/0842',
    institution_name: 'Sri Krishna College of Engineering & Tech',
    institution_type: 'Private Self-Financing',
    academic_year: '2025-2026',
    status: 'under_review',
    risk_level: 'high',
    risk_score: 84,
    region: 'Southern',
    state: 'Tamil Nadu',
    applied_intake: 480,
    approved_intake: 360,
    created_at: '2025-02-10T09:30:00Z',
    updated_at: '2025-02-24T14:15:00Z',
    total_flags_count: 5,
    critical_flags_count: 2,
    submission_version: 2,
    submitted_by: 'Dr. K. Senthil Nathan',
    summary: 'Extension of approval with additional intake request for B.Tech AI & Data Science. Cross-verification flagged potential duplicate faculty PAN with Karnataka institute and altered survey number in land title deed.',
    risk_breakdown: {
      composite_score: 84,
      land_risk: 78,
      faculty_risk: 92,
      forensic_risk: 86,
      regulatory_risk: 65,
      primary_concerns: [
        'Document tampering detected in Survey No. 412/A of Land Title Deed',
        'Duplicate faculty record detected across 2 institutions for Prof. Ramesh Babu (PAN: ABCPR4928L)',
        'Built-up area deficit of 340 sq.m against AICTE APH norms for proposed intake'
      ]
    }
  },
  {
    id: 'app-002',
    application_number: 'AICTE/SRO/2025/1109',
    institution_name: 'Coimbatore Institute of Information Sciences',
    institution_type: 'Government Aided',
    academic_year: '2025-2026',
    status: 'verified',
    risk_level: 'low',
    risk_score: 18,
    region: 'Southern',
    state: 'Tamil Nadu',
    applied_intake: 300,
    approved_intake: 300,
    created_at: '2025-02-12T11:00:00Z',
    updated_at: '2025-02-23T16:00:00Z',
    total_flags_count: 1,
    critical_flags_count: 0,
    submission_version: 1,
    submitted_by: 'Dr. M. Soundararajan',
    summary: 'Annual EoA verification. All mandatory documents verified with state digital registries. Minor font inconsistency detected on library invoice flagged as low risk.',
    risk_breakdown: {
      composite_score: 18,
      land_risk: 12,
      faculty_risk: 15,
      forensic_risk: 20,
      regulatory_risk: 10,
      primary_concerns: ['Minor metadata anomaly in statutory attachment [Reference - verify against Approval Process Handbook] (illustrative)']
    }
  },
  {
    id: 'app-003',
    application_number: 'AICTE/WRO/2025/0955',
    institution_name: 'Vellore Academy of Technical Studies',
    institution_type: 'Private Self-Financing',
    academic_year: '2025-2026',
    status: 'deficiency_issued',
    risk_level: 'medium',
    risk_score: 58,
    region: 'Western',
    state: 'Maharashtra',
    applied_intake: 420,
    approved_intake: 300,
    created_at: '2025-02-05T08:15:00Z',
    updated_at: '2025-02-22T10:45:00Z',
    total_flags_count: 3,
    critical_flags_count: 1,
    submission_version: 1,
    submitted_by: 'Prof. Aniket Deshmukh',
    summary: 'Deficiency issued due to expired Fire Safety NOC and failure to meet Cad Lab workstation to student ratio.',
    risk_breakdown: {
      composite_score: 58,
      land_risk: 30,
      faculty_risk: 42,
      forensic_risk: 45,
      regulatory_risk: 75,
      primary_concerns: ['Expired Fire Safety NOC (expired Jan 15, 2025)', 'Shortage of CAD software licenses']
    }
  },
  {
    id: 'app-004',
    application_number: 'AICTE/NRO/2025/0412',
    institution_name: 'Royal College of Technology & Management',
    institution_type: 'Private Self-Financing',
    academic_year: '2025-2026',
    status: 'under_review',
    risk_level: 'high',
    risk_score: 91,
    region: 'Northern',
    state: 'Uttar Pradesh',
    applied_intake: 540,
    created_at: '2025-01-28T14:20:00Z',
    updated_at: '2025-02-25T09:10:00Z',
    total_flags_count: 6,
    critical_flags_count: 3,
    submission_version: 1,
    submitted_by: 'Dr. Vivek Saxena',
    summary: 'Suspicious cloned signatures detected in faculty joining affidavits. Land title deed shares boundary with an unapproved commercial property.',
    risk_breakdown: {
      composite_score: 91,
      land_risk: 88,
      faculty_risk: 94,
      forensic_risk: 96,
      regulatory_risk: 85,
      primary_concerns: [
        'Cloned digital signature across 4 faculty appointment letters',
        'Principal designated simultaneously as Dean at an unaffiliated college in Noida',
        'State revenue registration stamp hash mismatch'
      ]
    }
  },
  {
    id: 'app-005',
    application_number: 'AICTE/SRO/2025/1337',
    institution_name: 'Apex Polytechnic & Technical Institute',
    institution_type: 'Polytechnic Diploma',
    academic_year: '2025-2026',
    status: 'approved',
    risk_level: 'low',
    risk_score: 14,
    region: 'Southern',
    state: 'Kerala',
    applied_intake: 240,
    approved_intake: 240,
    created_at: '2025-01-15T10:00:00Z',
    updated_at: '2025-02-20T17:30:00Z',
    total_flags_count: 0,
    critical_flags_count: 0,
    submission_version: 1,
    submitted_by: 'Dr. George Varghese',
    summary: 'All requirements fully satisfied under AICTE Approval Process Handbook (APH) 2025.',
    risk_breakdown: {
      composite_score: 14,
      land_risk: 10,
      faculty_risk: 12,
      forensic_risk: 14,
      regulatory_risk: 11,
      primary_concerns: []
    }
  }
];

export const mockDocuments: Document[] = [
  {
    id: 'doc-001',
    application_id: 'app-001',
    document_type: 'land_title',
    filename: 'Land_Title_Deed_Khasra_412A.pdf',
    file_size: 4280192,
    mime_type: 'application/pdf',
    file_url: 'https://images.unsplash.com/photo-1568667256549-094345857637?auto=format&fit=crop&w=1200&q=80',
    page_count: 4,
    status: 'flagged',
    version: 2,
    uploaded_at: '2025-02-15T10:30:00Z',
    extracted_fields: {
      survey_number: '412/A-1',
      total_area_acres: 7.5,
      total_area_sqm: 30351.4,
      ownership_type: 'Ownership in the name of Trust',
      trust_name: 'Sri Krishna Educational & Charitable Trust',
      encumbrance_status: 'Nil / Free from all encumbrances',
      registration_date: '2018-06-12',
      registration_office: 'Sub-Registrar Office, Pollachi',
    },
    forensic_report: {
      tampering_score: 88,
      ela_heatmap_url: 'https://images.unsplash.com/photo-1541888946425-d0fbb186c5f7?auto=format&fit=crop&w=1200&q=80',
      cloned_regions_detected: true,
      font_inconsistencies: true,
      metadata_anomalies: [
        'Modified with Adobe Photoshop CC 2023 on 2025-02-14T22:18:00',
        'PDF Producer metadata does not match scanner hardware signature'
      ],
      compression_artifacts: true,
      pii_detected: [
        { type: 'Aadhaar', masked_value: 'XXXX-XXXX-8921', raw_value: '5421-9876-8921', page: 2 },
        { type: 'PAN', masked_value: 'AAAAA****A', raw_value: 'AAATS9842F', page: 3 }
      ],
      analysis_summary: 'Significant Error Level Analysis (ELA) variance on Page 1 line 14 where survey number "412/A-1" replaced "412/B". Differing font kerning and raster compression inconsistencies detected around survey coordinates.'
    }
  },
  {
    id: 'doc-002',
    application_id: 'app-001',
    document_type: 'faculty_list',
    filename: 'Certified_Faculty_Roster_2025.pdf',
    file_size: 2150900,
    mime_type: 'application/pdf',
    file_url: 'https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=1200&q=80',
    page_count: 8,
    status: 'flagged',
    version: 2,
    uploaded_at: '2025-02-15T10:32:00Z',
    extracted_fields: {
      total_faculty_count: 52,
      professors_count: 6,
      associate_professors_count: 14,
      assistant_professors_count: 32,
      phd_qualified_count: 22,
      average_experience_years: 8.4,
    },
    forensic_report: {
      tampering_score: 72,
      cloned_regions_detected: false,
      font_inconsistencies: false,
      metadata_anomalies: [],
      compression_artifacts: false,
      pii_detected: [
        { type: 'PAN', masked_value: 'ABCPR****L', raw_value: 'ABCPR4928L', page: 4 },
        { type: 'Aadhaar', masked_value: 'XXXX-XXXX-4102', raw_value: '8492-1102-4102', page: 4 }
      ],
      analysis_summary: 'Cross-verification with AICTE National Faculty Database identifies Faculty ID FT-2019-9401 (Prof. Ramesh Babu) concurrently enrolled as full-time regular faculty in Bangalore Institute of Technology.'
    }
  },
  {
    id: 'doc-003',
    application_id: 'app-001',
    document_type: 'building_plan',
    filename: 'Approved_Municipal_Floor_Plans.pdf',
    file_size: 15400200,
    mime_type: 'application/pdf',
    file_url: 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=1200&q=80',
    page_count: 12,
    status: 'verified',
    version: 1,
    uploaded_at: '2025-02-10T09:35:00Z',
    extracted_fields: {
      instructional_area_sqm: 11200,
      administrative_area_sqm: 2450,
      amenities_area_sqm: 1800,
      total_built_up_area_sqm: 15450,
      cad_lab_carpet_area_sqm: 120,
      fire_exit_staircase_count: 6,
      approval_authority: 'Directorate of Town and Country Planning (DTCP)',
      approval_order_no: 'DTCP/CBE/2021/B-492'
    },
    forensic_report: {
      tampering_score: 12,
      cloned_regions_detected: false,
      font_inconsistencies: false,
      metadata_anomalies: [],
      compression_artifacts: false,
      analysis_summary: 'DTCP municipal seal and architect digital signature valid. Geometry dimensions verified against declared room schedules.'
    }
  },
  {
    id: 'doc-004',
    application_id: 'app-001',
    document_type: 'fire_safety_cert',
    filename: 'Fire_NOC_Govt_TamilNadu.pdf',
    file_size: 1240000,
    mime_type: 'application/pdf',
    file_url: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80',
    page_count: 2,
    status: 'verified',
    version: 1,
    uploaded_at: '2025-02-10T09:40:00Z',
    extracted_fields: {
      issuing_authority: 'Tamil Nadu Fire and Rescue Services Department',
      noc_number: 'TNFRS/CBE/2024/NOC-8812',
      issue_date: '2024-04-10',
      valid_upto: '2027-04-09',
      building_occupancy_limit: 1500,
      status: 'Valid'
    },
    forensic_report: {
      tampering_score: 8,
      cloned_regions_detected: false,
      font_inconsistencies: false,
      metadata_anomalies: [],
      compression_artifacts: false,
      analysis_summary: 'Verified authentic against TNFRS digital certificate repository.'
    }
  }
];

export const mockFlags: Flag[] = [
  {
    id: 'flg-001',
    application_id: 'app-001',
    document_id: 'doc-001',
    code: 'SEC-FOR-001',
    rule_id: 'RULE_APH_LAND_AUTHENTICITY',
    title: 'Altered Survey Number in Land Title Deed',
    reason: 'Error Level Analysis reveals high pixel variance and Photoshop manipulation artifacts around the survey number field "412/A-1". State land registration portal records reflect Survey No. 412/B with differing easement rights.',
    severity: 'critical',
    confidence: 94.6,
    status: 'open',
    created_at: '2025-02-15T11:00:00Z',
    is_simulated: false,
    evidence_link: {
      document_id: 'doc-001',
      document_name: 'Land_Title_Deed_Khasra_412A.pdf',
      page: 1,
      bounding_boxes: [
        { x: 180, y: 320, width: 220, height: 48, label: 'Altered Survey Number (ELA Discrepancy)', confidence: 0.95 }
      ],
      overlay_type: 'ela'
    }
  },
  {
    id: 'flg-002',
    application_id: 'app-001',
    document_id: 'doc-002',
    code: 'FAC-DUP-002',
    rule_id: 'RULE_FACULTY_CONCURRENT_EMPLOYMENT',
    title: 'Duplicate Faculty PAN Across Institutions',
    reason: 'Faculty member Prof. Ramesh Babu (PAN: ABCPR****L) is claimed as full-time Professor in Sri Krishna College while concurrently listed on the active payroll of Bangalore Institute of Technology for AY 2025-26.',
    severity: 'critical',
    confidence: 98.2,
    status: 'open',
    created_at: '2025-02-15T11:05:00Z',
    is_simulated: false,
    evidence_link: {
      document_id: 'doc-002',
      document_name: 'Certified_Faculty_Roster_2025.pdf',
      page: 4,
      bounding_boxes: [
        { x: 50, y: 410, width: 500, height: 35, label: 'Duplicate Faculty PAN (ABCPR4928L)', confidence: 0.98 }
      ],
      overlay_type: 'annotations'
    }
  },
  {
    id: 'flg-003',
    application_id: 'app-001',
    document_id: 'doc-003',
    code: 'INF-CAD-003',
    rule_id: 'RULE_APH_CAD_LAB_CARPET_AREA',
    title: 'CAD Lab Area Deficit for Proposed Intake',
    reason: 'For applied intake of 480 students across Computer Science & Data Science divisions, APH Table 4.2 mandates minimum 180 sq.m CAD/CAM facility. Extracted architectural plan allocates only 120 sq.m.',
    severity: 'medium',
    confidence: 88.0,
    status: 'open',
    created_at: '2025-02-15T11:10:00Z',
    is_simulated: false,
    evidence_link: {
      document_id: 'doc-003',
      document_name: 'Approved_Municipal_Floor_Plans.pdf',
      page: 3,
      bounding_boxes: [
        { x: 310, y: 560, width: 140, height: 80, label: 'CAD Lab Area 120 sq.m (Req: 180 sq.m)', confidence: 0.88 }
      ],
      overlay_type: 'original'
    }
  },
  {
    id: 'flg-004',
    application_id: 'app-001',
    code: 'REG-FSR-004',
    rule_id: 'RULE_APH_FACULTY_STUDENT_RATIO',
    title: 'Faculty to Student Ratio Borderline Deficiency',
    reason: 'Calculated FSR is 1:21.8 after disqualifying 2 duplicate faculty profiles. AICTE APH Chapter 7 prescribes minimum 1:20 ratio for UG Engineering programs.',
    severity: 'high',
    confidence: 91.5,
    status: 'open',
    created_at: '2025-02-15T11:15:00Z',
    is_simulated: false,
  },
  {
    id: 'flg-005',
    application_id: 'app-001',
    document_id: 'doc-001',
    code: 'SEC-PII-005',
    rule_id: 'RULE_PRIVACY_PII_EXPOSURE',
    title: 'Unmasked Aadhaar Number in Public Document',
    reason: 'Raw 12-digit Aadhaar number found unredacted in Land Title Trust Deed attachment. Auto-masking applied on preview.',
    severity: 'low',
    confidence: 99.0,
    status: 'resolved',
    resolved_by: 'officer_kumar',
    resolved_at: '2025-02-16T14:20:00Z',
    resolution_notes: 'Document automatically masked via AICTE PII redaction pipeline. College informed.',
    created_at: '2025-02-15T11:20:00Z',
    is_simulated: false,
  }
];

export const mockVerifications: VerificationResult[] = [
  {
    id: 'vr-001',
    application_id: 'app-001',
    check_type: 'pan_verification',
    check_name: 'NSDL Income Tax PAN Verification',
    target_identifier: 'AAATS9842F',
    status: 'verified',
    source_authority: 'Income Tax Department (NSDL/Protean e-Gov)',
    verified_at: '2025-02-15T10:45:00Z',
    is_simulated: true,
    response_data: {
      pan: 'AAATS9842F',
      entity_type: 'Trust',
      registered_name: 'SRI KRISHNA EDUCATIONAL AND CHARITABLE TRUST',
      status: 'OPERATIVE',
      aadhaar_seeded: true
    }
  },
  {
    id: 'vr-002',
    application_id: 'app-001',
    check_type: 'land_registry',
    check_name: 'Tamil Nadu Kaveri/e-District Land Registry',
    target_identifier: 'SURVEY-412/A-1-POLLACHI',
    status: 'mismatch',
    source_authority: 'Revenue Department, Govt of Tamil Nadu',
    verified_at: '2025-02-15T10:46:12Z',
    is_simulated: true,
    response_data: {
      queried_survey: '412/A-1',
      registry_record_found: true,
      registered_owner: 'K. RAMASWAMY PILLAI (Agricultural)',
      govt_notified_zoning: 'Wetland Agricultural (Conversion Pending)',
      discrepancy: 'Subdivision 412/A-1 is pending DTCP conversion; College submitted deed claiming completed conversion.'
    }
  },
  {
    id: 'vr-003',
    application_id: 'app-001',
    check_type: 'faculty_duplicate',
    check_name: 'AICTE National Faculty Registry Deduplication',
    target_identifier: 'FAC-52-RECORDS',
    status: 'failed',
    source_authority: 'AICTE Central Faculty Portal API',
    verified_at: '2025-02-15T10:47:05Z',
    is_simulated: false,
    response_data: {
      total_screened: 52,
      unique_faculty: 50,
      conflicts: [
        {
          pan_hash: 'ABCPR4928L',
          name: 'Prof. Ramesh Babu',
          other_institution: 'Bangalore Institute of Technology (BIT-1049)',
          conflict_type: 'Concurrent Full-Time Appointment'
        }
      ]
    }
  },
  {
    id: 'vr-004',
    application_id: 'app-001',
    check_type: 'fire_safety_portal',
    check_name: 'State Disaster Management & Fire Services Portal',
    target_identifier: 'TNFRS/CBE/2024/NOC-8812',
    status: 'verified',
    source_authority: 'Tamil Nadu Fire and Rescue Services',
    verified_at: '2025-02-15T10:48:30Z',
    is_simulated: true,
    response_data: {
      noc_id: 'TNFRS/CBE/2024/NOC-8812',
      valid_until: '2027-04-09',
      inspection_officer: 'Divisional Fire Officer, Coimbatore West',
      status: 'ACTIVE_COMPLIANT'
    }
  },
  {
    id: 'vr-005',
    application_id: 'app-001',
    check_type: 'university_affiliation',
    check_name: 'Affiliating University (Anna University) Database',
    target_identifier: 'AU-AFF-2024-CBE-041',
    status: 'verified',
    source_authority: 'Anna University Centre for Affiliation of Institutions',
    verified_at: '2025-02-15T10:49:15Z',
    is_simulated: true,
    response_data: {
      permanent_affiliation_status: 'Provisional (Valid for AY 2024-25)',
      programs_approved: ['B.E. CSE', 'B.Tech IT', 'B.Tech AI&DS', 'B.E. ECE'],
      sanctioned_intake_by_university: 360
    }
  }
];

export const mockComplianceResults: ComplianceResult[] = [
  {
    id: 'comp-001',
    application_id: 'app-001',
    category: 'land_area',
    item_name: 'Minimum Contiguous Land Area',
    rule_reference: 'APH 2025 Appendix 4.1',
    declared_value: 7.5,
    required_value: 5.0,
    unit: 'Acres (Rural / Other)',
    status: 'gap',
    deficiency_description: 'Although total declared is 7.5 acres, 2.5 acres under Survey No. 412/A-1 contains unverified ownership conversion and boundary litigation flags.',
    intake_impact: 120
  },
  {
    id: 'comp-002',
    application_id: 'app-001',
    category: 'built_up_area',
    item_name: 'Total Instructional Built-up Area',
    rule_reference: 'APH 2025 Table 4.1',
    declared_value: 11200,
    required_value: 10800,
    unit: 'sq.m',
    status: 'pass',
    deficiency_description: 'Sufficient instructional classrooms, seminar halls, and tutorial rooms provided.'
  },
  {
    id: 'comp-003',
    application_id: 'app-001',
    category: 'faculty_student_ratio',
    item_name: 'Faculty to Student Ratio (UG Engineering)',
    rule_reference: 'APH 2025 Section 7.1',
    declared_value: '1 : 18.5',
    required_value: '1 : 20.0',
    unit: 'Ratio',
    status: 'needs_inspection',
    deficiency_description: 'With 2 disputed faculty members removed, actual ratio drops to 1:21.8, failing the minimum 1:20 threshold. Physical spot verification recommended.',
    intake_impact: 60
  },
  {
    id: 'comp-004',
    application_id: 'app-001',
    category: 'cad_labs',
    item_name: 'CAD/CAM Laboratory Area & Equipment',
    rule_reference: 'APH 2025 Table 4.2',
    declared_value: 120,
    required_value: 180,
    unit: 'sq.m',
    status: 'gap',
    deficiency_description: 'Shortfall of 60 sq.m carpet area for computational engineering laboratories.',
    intake_impact: 60
  },
  {
    id: 'comp-005',
    application_id: 'app-001',
    category: 'library_titles',
    item_name: 'Technical Book Titles & National/International Journals',
    rule_reference: 'APH 2025 Table 5.1',
    declared_value: 4200,
    required_value: 3500,
    unit: 'Titles',
    status: 'pass',
    deficiency_description: 'Exceeds minimum prescribed library titles and IEEE e-journal subscriptions.'
  },
  {
    id: 'comp-006',
    application_id: 'app-001',
    category: 'fire_safety',
    item_name: 'Fire Safety Certificate & Evacuation Plan',
    rule_reference: 'National Building Code 2016 Part 4',
    declared_value: 'Valid until 2027',
    required_value: 'Valid NOC',
    unit: 'Status',
    status: 'pass',
    deficiency_description: 'TNFRS NOC valid for full academic term.'
  }
];

export const mockCapacityCalculation: CapacityCalculation = {
  built_up_area_sqm: 11200,
  required_sqm_per_student: 8.5,
  faculty_count: 50,
  faculty_ratio_required: 20,
  max_capacity_infrastructure: 480,
  max_capacity_faculty: 360,
  bottleneck_factor: 'faculty',
  applied_intake: 480,
  suggested_approved_intake: 360,
  explanation: 'While the physical infrastructure supports an intake of 480 students, the qualified faculty roster (after excluding duplicate and invalid profiles) can strictly support a maximum intake of 360 students under the 1:20 norm.'
};

export const mockValidationReport: ValidationReport = {
  application_id: 'app-001',
  total_rules_evaluated: 48,
  passed_rules: 41,
  failed_rules: 7,
  missing_mandatory_documents: [
    'Affidavit 1 (Anti-Ragging and Non-Discriminatory Declaration on Non-Judicial Stamp Paper)',
    'Latest Audited Balance Sheet signed by Chartered Accountant with UDIN'
  ],
  inconsistencies: [
    {
      field: 'Trust Chairman Name',
      source_a: 'Land Title Deed (p. 2)',
      val_a: 'Dr. K. S. Nathan',
      source_b: 'Society Registration Certificate (p. 1)',
      val_b: 'Sri K. Senthil Nathan Pillai',
      severity: 'medium'
    },
    {
      field: 'Survey Plot Coordinates',
      source_a: 'Land Title Deed (p. 1)',
      val_a: 'Survey No. 412/A-1',
      source_b: 'Municipal Approval Plan (p. 1)',
      val_b: 'Survey No. 412/B',
      severity: 'critical'
    }
  ],
  recommendations: [
    'Issuance of Deficiency Letter under statutory hearing rules regarding Survey No discrepancy [Reference - verify against Approval Process Handbook] (illustrative)',
    'Summon original Land Deed for physical inspection at SRO Chennai',
    'Exclude Prof. Ramesh Babu from faculty calculation until dual employment clearance is obtained',
    'Cap approved intake at 360 seats pending compliance resubmission'
  ]
};

export const mockTimelineEvents: TimelineEvent[] = [
  {
    id: 'evt-001',
    application_id: 'app-001',
    timestamp: '2025-02-10T09:30:00Z',
    title: 'Application Submitted',
    description: 'Initial online submission with 4 supporting documents for AY 2025-26.',
    actor: 'Dr. K. Senthil Nathan (College)',
    type: 'status_change'
  },
  {
    id: 'evt-002',
    application_id: 'app-001',
    timestamp: '2025-02-10T09:35:00Z',
    title: 'Automated OCR & Forensic Scan Initiated',
    description: 'AICTE-Verify pipeline queued 26 pages across 4 documents.',
    actor: 'AICTE Automated Engine',
    type: 'document_uploaded'
  },
  {
    id: 'evt-003',
    application_id: 'app-001',
    timestamp: '2025-02-15T11:00:00Z',
    title: 'Critical Flags Generated',
    description: 'Altered survey number and duplicate faculty PAN identified.',
    actor: 'Forensic Detection Module',
    type: 'flag_raised'
  },
  {
    id: 'evt-004',
    application_id: 'app-001',
    timestamp: '2025-02-16T14:20:00Z',
    title: 'PII Redaction Applied',
    description: 'Aadhaar masking flag resolved after auto-redaction.',
    actor: 'Dr. Rajesh Kumar (Officer)',
    type: 'flag_resolved'
  },
  {
    id: 'evt-005',
    application_id: 'app-001',
    timestamp: '2025-02-22T10:00:00Z',
    title: 'Resubmission Version 2 Received',
    description: 'College uploaded amended faculty list and survey clarification.',
    actor: 'Dr. K. Senthil Nathan (College)',
    type: 'status_change'
  }
];

export const mockResubmissionDiff: ResubmissionDiff = {
  previous_version: 1,
  current_version: 2,
  added_documents: ['Survey_Clarification_Affidavit_Pollachi.pdf'],
  removed_documents: ['Old_Faculty_Declaration_Draft.pdf'],
  modified_documents: ['Certified_Faculty_Roster_2025.pdf'],
  changed_fields: [
    { field: 'Declared Faculty Count', old_value: 48, new_value: 52 },
    { field: 'Proposed AI&DS Intake', old_value: 60, new_value: 120 },
    { field: 'Total Built-up Area (sq.m)', old_value: 14900, new_value: 15450 }
  ]
};

export const mockAuditEntries: AuditEntry[] = [
  {
    id: 'aud-001',
    timestamp: '2025-02-10T09:30:12Z',
    actor_id: 'u-3',
    actor_name: 'Dr. K. Senthil Nathan',
    actor_role: 'college_user',
    action: 'APPLICATION_SUBMITTED',
    entity_type: 'Application',
    entity_id: 'app-001',
    details: 'Initial application submitted for Sri Krishna College (AICTE/SRO/2025/0842) with 4 documents.',
    prev_hash: '0000000000000000000000000000000000000000000000000000000000000000',
    curr_hash: '8f4c2e6b1a9d0f3c5b7e8a9d1c3f5e7a9b0c2d4e6f8a0b1c2d3e4f5a6b7c8d9e',
    ip_address: '117.247.182.14',
    is_tampered: false
  },
  {
    id: 'aud-002',
    timestamp: '2025-02-15T11:00:24Z',
    actor_id: 'system',
    actor_name: 'AICTE-Verify Automated Engine',
    actor_role: 'system',
    action: 'FLAG_GENERATED',
    entity_type: 'Flag',
    entity_id: 'flg-001',
    details: 'Critical Flag SEC-FOR-001 raised on doc-001: Altered Survey Number in Land Title Deed (Confidence: 94.6%).',
    prev_hash: '8f4c2e6b1a9d0f3c5b7e8a9d1c3f5e7a9b0c2d4e6f8a0b1c2d3e4f5a6b7c8d9e',
    curr_hash: '3d5e7f9a1b2c4d6e8f0a2b4c6d8e0f1a3b5c7d9e1f2a4b6c8d0e2f4a6b8c0d1e',
    ip_address: '10.0.4.12',
    is_tampered: false
  },
  {
    id: 'aud-003',
    timestamp: '2025-02-16T14:20:45Z',
    actor_id: 'u-1',
    actor_name: 'Dr. Rajesh Kumar',
    actor_role: 'officer',
    action: 'FLAG_RESOLVED',
    entity_type: 'Flag',
    entity_id: 'flg-005',
    details: 'Officer resolved flag SEC-PII-005: Auto-redaction verified for Aadhaar data.',
    prev_hash: '3d5e7f9a1b2c4d6e8f0a2b4c6d8e0f1a3b5c7d9e1f2a4b6c8d0e2f4a6b8c0d1e',
    curr_hash: '2c4b6a8e0f1d3e5a7b9c1d3e5f7a9b0c2d4e6f8a0b1c2d3e4f5a6b7c8d9e0f1a',
    ip_address: '14.139.185.2',
    is_tampered: false
  },
  {
    id: 'aud-004',
    timestamp: '2025-02-20T16:10:00Z',
    actor_id: 'u-1',
    actor_name: 'Dr. Rajesh Kumar',
    actor_role: 'officer',
    action: 'PII_REVEAL_VIEWED',
    entity_type: 'Document',
    entity_id: 'doc-001',
    details: 'Officer unmasked and viewed raw Aadhaar PII on Land Title Deed page 2 for verification audit.',
    prev_hash: '2c4b6a8e0f1d3e5a7b9c1d3e5f7a9b0c2d4e6f8a0b1c2d3e4f5a6b7c8d9e0f1a',
    curr_hash: '9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b',
    ip_address: '14.139.185.2',
    is_tampered: false
  },
  {
    id: 'aud-005',
    timestamp: '2025-02-24T14:15:22Z',
    actor_id: 'u-1',
    actor_name: 'Dr. Rajesh Kumar',
    actor_role: 'officer',
    action: 'STATUS_UPDATED',
    entity_type: 'Application',
    entity_id: 'app-001',
    details: 'Application status changed from SUBMITTED to UNDER_REVIEW. Scrutiny hearing slated.',
    prev_hash: '9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b',
    curr_hash: '7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d',
    ip_address: '14.139.185.2',
    is_tampered: false
  }
];

export const mockGraphData: GraphData = {
  nodes: [
    {
      id: 'inst-1',
      label: 'Sri Krishna College of Engg (Coimbatore)',
      type: 'institution',
      properties: { aicte_id: '1-36829104', state: 'Tamil Nadu', category: 'Engineering' },
      flagged: true,
      flag_reasons: ['Tampering in land title', 'Duplicate faculty']
    },
    {
      id: 'inst-2',
      label: 'Bangalore Institute of Technology (BIT)',
      type: 'institution',
      properties: { aicte_id: '1-10492811', state: 'Karnataka', category: 'Engineering' },
      flagged: false,
    },
    {
      id: 'inst-3',
      label: 'Royal College of Tech (Lucknow)',
      type: 'institution',
      properties: { aicte_id: '1-49201944', state: 'Uttar Pradesh', category: 'Engineering' },
      flagged: true,
      flag_reasons: ['Cloned signatures across appointments']
    },
    {
      id: 'fac-1',
      label: 'Prof. Ramesh Babu (CSE)',
      type: 'faculty',
      properties: { pan_masked: 'ABCPR****L', experience: '14 years', designation: 'Professor' },
      flagged: true,
      flag_reasons: ['Concurrent full-time employment claimed at 2 colleges']
    },
    {
      id: 'fac-2',
      label: 'Dr. Ananya Sundaram (AI)',
      type: 'faculty',
      properties: { pan_masked: 'BZAPS****M', experience: '11 years', designation: 'Assoc. Professor' },
      flagged: false,
    },
    {
      id: 'fac-3',
      label: 'Dr. Vivek Saxena (Principal)',
      type: 'faculty',
      properties: { pan_masked: 'AGTPK****R', experience: '22 years', designation: 'Principal' },
      flagged: true,
      flag_reasons: ['Dual designation at unaffiliated Noida campus']
    },
    {
      id: 'land-1',
      label: 'Survey No. 412/A-1 (Pollachi)',
      type: 'land',
      properties: { area_acres: 7.5, sub_registrar: 'Pollachi', state: 'Tamil Nadu' },
      flagged: true,
      flag_reasons: ['High pixel variance in deed coordinates']
    },
    {
      id: 'land-2',
      label: 'Survey Plot 88-B (Saravanampatti)',
      type: 'land',
      properties: { area_acres: 10.2, sub_registrar: 'Coimbatore North', state: 'Tamil Nadu' },
      flagged: false,
    },
    {
      id: 'trust-1',
      label: 'Sri Krishna Educational & Charitable Trust',
      type: 'trust',
      properties: { reg_no: 'TRUST-TN-491-1998', pan_masked: 'AAATS****F' },
      flagged: false,
    },
    {
      id: 'trust-2',
      label: 'Royal Vidya Vikas Trust',
      type: 'trust',
      properties: { reg_no: 'TRUST-UP-102-2004', pan_masked: 'AAATR****E' },
      flagged: true,
      flag_reasons: ['Common trustee linked to blacklisted institution']
    },
    {
      id: 'sig-1',
      label: 'Signatory: K. Ramaswamy (Notary)',
      type: 'signatory',
      properties: { notary_reg: 'NOT-TN-8419', valid_upto: '2026-12' },
      flagged: false,
    },
    {
      id: 'sig-2',
      label: 'Signatory: Dr. Vivek Saxena (Dual Sign)',
      type: 'signatory',
      properties: { notary_reg: 'N/A', role: 'Principal' },
      flagged: true,
      flag_reasons: ['Digital signature cloned with identical pixel entropy']
    },
    {
      id: 'stamp-1',
      label: 'Govt Stamp: TN Revenue #88219',
      type: 'stamp',
      properties: { denomination: 100, issued: 'Pollachi Treasury' },
      flagged: false,
    },
    {
      id: 'stamp-2',
      label: 'Govt Stamp: UP Non-Judicial #9411',
      type: 'stamp',
      properties: { denomination: 500, issued: 'Lucknow Treasury' },
      flagged: true,
      flag_reasons: ['Reused serial number already redeemed in 2023']
    }
  ],
  edges: [
    {
      id: 'e-1',
      source: 'inst-1',
      target: 'fac-1',
      type: 'employs',
      label: 'Employs (Claimed Full-Time)',
      flagged: true,
      flag_reason: 'Concurrent employment conflict with BIT Bangalore',
      confidence: 0.98
    },
    {
      id: 'e-2',
      source: 'inst-2',
      target: 'fac-1',
      type: 'employs',
      label: 'Employs (Active on Payroll)',
      flagged: true,
      flag_reason: 'Concurrent employment conflict with SKCET Coimbatore',
      confidence: 0.98
    },
    {
      id: 'e-3',
      source: 'inst-1',
      target: 'fac-2',
      type: 'employs',
      label: 'Employs (Verified)',
      flagged: false,
    },
    {
      id: 'e-4',
      source: 'inst-3',
      target: 'fac-3',
      type: 'employs',
      label: 'Principal Appointee',
      flagged: true,
      flag_reason: 'Concurrent administrative duties in unapproved off-campus unit',
      confidence: 0.92
    },
    {
      id: 'e-5',
      source: 'inst-1',
      target: 'land-1',
      type: 'owns',
      label: 'Campus Land Site',
      flagged: true,
      flag_reason: 'Deed ELA variance in Survey No. 412/A-1',
      confidence: 0.94
    },
    {
      id: 'e-6',
      source: 'trust-1',
      target: 'inst-1',
      type: 'trustee_of',
      label: 'Operating Sponsoring Trust',
      flagged: false,
    },
    {
      id: 'e-7',
      source: 'trust-2',
      target: 'inst-3',
      type: 'trustee_of',
      label: 'Operating Sponsoring Trust',
      flagged: true,
      flag_reason: 'Cross-ownership with blacklisted UP polytechnic',
      confidence: 0.89
    },
    {
      id: 'e-8',
      source: 'inst-3',
      target: 'sig-2',
      type: 'signed_by',
      label: 'Cloned Signatures on Affidavits',
      flagged: true,
      flag_reason: 'Identical signature bounding boxes detected across 4 documents',
      confidence: 0.96
    },
    {
      id: 'e-9',
      source: 'inst-3',
      target: 'stamp-2',
      type: 'stamped_with',
      label: 'Redeemed Stamp Paper',
      flagged: true,
      flag_reason: 'Stamp serial re-use violation',
      confidence: 0.99
    }
  ]
};

export const mockEvaluationResult: EvaluationResult = {
  id: 'eval-2025-01',
  test_set_name: 'AICTE Synthetic & Benchmarked Verification Dataset v2.4 (250 Documents)',
  total_samples: 250,
  accuracy: 94.8,
  precision: 93.6,
  recall: 96.2,
  f1_score: 94.9,
  execution_time_ms: 1840,
  evaluated_at: '2025-02-25T14:30:00Z',
  detailed_checks: [
    {
      check_name: 'Error Level Analysis (ELA) Tampering Detection',
      precision: 95.2,
      recall: 94.0,
      f1: 94.6,
      sample_count: 50,
      status: 'pass'
    },
    {
      check_name: 'Cross-Institution Faculty Duplicate Detection',
      precision: 98.8,
      recall: 99.1,
      f1: 98.9,
      sample_count: 50,
      status: 'pass'
    },
    {
      check_name: 'Land Area & DTCP Survey Bounds Verification',
      precision: 92.0,
      recall: 95.5,
      f1: 93.7,
      sample_count: 50,
      status: 'pass'
    },
    {
      check_name: 'Architectural Built-up Area & CAD Compliance',
      precision: 91.5,
      recall: 93.2,
      f1: 92.3,
      sample_count: 50,
      status: 'pass'
    },
    {
      check_name: 'PII Identification & Sensitive Aadhaar Masking',
      precision: 98.0,
      recall: 99.5,
      f1: 98.7,
      sample_count: 50,
      status: 'pass'
    }
  ]
};

export const mockAlerts: Alert[] = [
  {
    id: 'alt-001',
    category: 'anomalies',
    severity: 'critical',
    title: 'Photoshop ELA Tampering Flagged in Land Title',
    description: 'Deed survey number 412/A-1 shows high frequency localized compression artifacting.',
    application_id: 'app-001',
    application_number: 'AICTE/SRO/2025/0842',
    institution_name: 'Sri Krishna College of Engineering & Tech',
    created_at: '2025-02-15T11:00:00Z',
    is_resolved: false
  },
  {
    id: 'alt-002',
    category: 'unresolved',
    severity: 'critical',
    title: 'Dual Active Faculty Payroll Claim',
    description: 'Prof. Ramesh Babu (PAN ABCPR4928L) claimed concurrently in Tamil Nadu and Karnataka.',
    application_id: 'app-001',
    application_number: 'AICTE/SRO/2025/0842',
    institution_name: 'Sri Krishna College of Engineering & Tech',
    created_at: '2025-02-15T11:05:00Z',
    is_resolved: false
  },
  {
    id: 'alt-003',
    category: 'missing_docs',
    severity: 'high',
    title: 'Mandatory Anti-Ragging Affidavit Missing',
    description: 'Non-judicial stamp paper affidavit missing from submitted package.',
    application_id: 'app-001',
    application_number: 'AICTE/SRO/2025/0842',
    institution_name: 'Sri Krishna College of Engineering & Tech',
    created_at: '2025-02-15T11:08:00Z',
    is_resolved: false
  },
  {
    id: 'alt-004',
    category: 'expired',
    severity: 'high',
    title: 'Fire Safety NOC Validity Expired',
    description: 'Fire certificate expired on Jan 15, 2025 without updated renewal receipt.',
    application_id: 'app-003',
    application_number: 'AICTE/WRO/2025/0955',
    institution_name: 'Vellore Academy of Technical Studies',
    created_at: '2025-02-05T08:20:00Z',
    is_resolved: false
  },
  {
    id: 'alt-005',
    category: 'pending_verification',
    severity: 'medium',
    title: 'State Kaveri Land Database API Timeout',
    description: 'Automated survey registry verification timed out; scheduled for retry.',
    application_id: 'app-004',
    application_number: 'AICTE/NRO/2025/0412',
    institution_name: 'Royal College of Technology & Management',
    created_at: '2025-02-25T09:12:00Z',
    is_resolved: false
  }
];

export const mockDeficiencyLetter: DeficiencyLetter = {
  id: 'let-001',
  application_id: 'app-001',
  application_number: 'AICTE/SRO/2025/0842',
  institution_name: 'Sri Krishna College of Engineering & Tech',
  academic_year: '2025-2026',
  date: '26th February 2025',
  language: 'en',
  subject: 'Deficiency Notice Regarding Application for Extension of Approval (EoA) / Additional Course Intake for AY 2025-26',
  body_content: `To,
The Principal / Chairman,
Sri Krishna College of Engineering & Tech,
Coimbatore, Tamil Nadu - 641042.

Sir/Madam,

This has reference to your online application submitted under AICTE Approval Process Handbook (APH) 2025-26 for the grant of Extension of Approval (EoA) and Increase in Intake in undergraduate engineering courses.

Upon automated verification and scrutiny by the Scrutiny Committee, certain substantial discrepancies, compliance gaps, and forensic inconsistencies have been observed as tabulated below.

You are hereby requested to submit your compliance / clarification along with original supporting records before the Scrutiny Committee within fifteen (15) working days from the date of issuance of this letter.`,
  deficiency_items: [
    {
      rule_id: 'RULE_APH_LAND_AUTHENTICITY',
      deficiency: 'Discrepancy and digital tampering artifacts observed in Survey Number 412/A-1 in the registered Land Title Deed.',
      action_required: 'Produce original registered title deed along with Patta/Chitta and DTCP approval order issued by the competent revenue authority.',
      deadline_days: 15
    },
    {
      rule_id: 'RULE_FACULTY_CONCURRENT_EMPLOYMENT',
      deficiency: 'Concurrent full-time faculty enrollment detected for Prof. Ramesh Babu (PAN: ABCPR4928L) with an institution in Karnataka.',
      action_required: 'Furnish Form 16, Bank statements showing monthly salary credit via ECS/PFMS, and Relieving Order if applicable.',
      deadline_days: 15
    },
    {
      rule_id: 'RULE_APH_CAD_LAB_CARPET_AREA',
      deficiency: 'Carpet area of CAD/CAM laboratory (120 sq.m) is deficient against the required norm (180 sq.m) for the proposed intake.',
      action_required: 'Submit architect-certified revised floor layout indicating dedicated laboratory space meeting minimum carpet area requirements.',
      deadline_days: 15
    }
  ],
  status: 'draft',
  gemini_improved: false
};

export const mockAnalyticsSummary: AnalyticsSummary = {
  total_applications: 18,
  pending_review: 6,
  approved_applications: 6,
  rejected_applications: 2,
  flags_by_severity: {
    info: 412,
    low: 320,
    medium: 215,
    high: 148,
    critical: 76
  },
  flags_by_type: [
    { type: 'Forensic Tampering', count: 182 },
    { type: 'Duplicate Faculty', count: 145 },
    { type: 'Land Area Discrepancy', count: 98 },
    { type: 'CAD / Lab Infrastructure', count: 120 },
    { type: 'Expired Certificates', count: 85 },
    { type: 'PII Exposure', count: 210 }
  ],
  verification_outcomes: [
    { name: 'Verified Authentic', value: 78, color: '#10b981' },
    { name: 'Discrepancies / Gaps', value: 14, color: '#f59e0b' },
    { name: 'Tampered / Invalid', value: 5, color: '#ef4444' },
    { name: 'Registry Unreachable', value: 3, color: '#6b7280' }
  ],
  applications_by_status: [
    { status: 'Approved', count: 940 },
    { status: 'Under Review', count: 184 },
    { status: 'Deficiency Issued', count: 92 },
    { status: 'Rejected', count: 24 }
  ],
  processing_times_trend: [
    { week: 'Week 1', avg_days: 14.2 },
    { week: 'Week 2', avg_days: 11.5 },
    { week: 'Week 3', avg_days: 8.4 },
    { week: 'Week 4', avg_days: 5.1 },
    { week: 'Week 5', avg_days: 3.2 }
  ],
  average_risk_score: 34.6,
  chain_integrity_status: 'verified'
};
