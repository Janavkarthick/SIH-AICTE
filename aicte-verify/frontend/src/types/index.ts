export type UserRole = 'officer' | 'scrutiny_admin' | 'college_user' | 'admin';

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  region?: string;
  institution_name?: string;
  institution_id?: string;
  phone?: string;
  created_at: string;
}

export type ApplicationStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'verified'
  | 'deficiency_issued'
  | 'approved'
  | 'rejected';

export type RiskLevel = 'low' | 'medium' | 'high';

export interface RiskBreakdown {
  composite_score: number;
  land_risk: number;
  faculty_risk: number;
  forensic_risk: number;
  regulatory_risk: number;
  primary_concerns: string[];
}

export interface Application {
  id: string;
  application_number: string;
  institution_name: string;
  institution_type: string;
  academic_year: string;
  status: ApplicationStatus;
  risk_level: RiskLevel;
  risk_score: number;
  region: string;
  state: string;
  applied_intake: number;
  approved_intake?: number;
  created_at: string;
  updated_at: string;
  total_flags_count: number;
  critical_flags_count: number;
  submission_version: number;
  submitted_by?: string;
  risk_breakdown?: RiskBreakdown;
  summary?: string;
}

export type DocumentType =
  | 'land_title'
  | 'building_plan'
  | 'fd_receipt'
  | 'faculty_list'
  | 'fire_safety_cert'
  | 'aicte_approval'
  | 'affidavit'
  | 'society_trust_cert'
  | 'other';

export type DocumentStatus = 'pending' | 'processing' | 'verified' | 'flagged' | 'rejected';

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  label?: string;
  confidence?: number;
}

export interface ForensicReport {
  tampering_score: number; // 0 - 100
  ela_heatmap_url?: string;
  cloned_regions_detected: boolean;
  font_inconsistencies: boolean;
  metadata_anomalies: string[];
  compression_artifacts: boolean;
  pii_detected?: {
    type: string;
    masked_value: string;
    raw_value: string;
    page: number;
  }[];
  analysis_summary: string;
}

export interface Document {
  id: string;
  application_id: string;
  document_type: DocumentType;
  filename: string;
  file_size: number;
  mime_type: string;
  file_url: string;
  page_count: number;
  status: DocumentStatus;
  version: number;
  uploaded_at: string;
  extracted_fields: Record<string, any>;
  forensic_report?: ForensicReport;
  flags?: Flag[];
}

export type FlagSeverity = 'info' | 'low' | 'medium' | 'high' | 'critical';
export type FlagStatus = 'open' | 'resolved' | 'dismissed';

export interface EvidenceLink {
  document_id: string;
  document_name?: string;
  page: number;
  bounding_boxes: BoundingBox[];
  overlay_type: 'original' | 'ela' | 'annotations';
  preview_url?: string;
}

export interface Flag {
  id: string;
  application_id: string;
  document_id?: string;
  code: string;
  rule_id: string;
  title: string;
  reason: string;
  severity: FlagSeverity;
  confidence: number; // 0-100%
  evidence_link?: EvidenceLink;
  status: FlagStatus;
  resolved_by?: string;
  resolved_at?: string;
  resolution_notes?: string;
  created_at: string;
  is_simulated?: boolean;
}

export type VerificationCheckType =
  | 'pan_verification'
  | 'land_registry'
  | 'faculty_duplicate'
  | 'fire_safety_portal'
  | 'university_affiliation';

export type VerificationStatus = 'verified' | 'failed' | 'mismatch' | 'unreachable';

export interface VerificationResult {
  id: string;
  application_id: string;
  document_id?: string;
  check_type: VerificationCheckType;
  check_name: string;
  target_identifier: string;
  status: VerificationStatus;
  response_data: Record<string, any>;
  source_authority: string;
  verified_at: string;
  is_simulated?: boolean;
}

export type ComplianceCategory =
  | 'land_area'
  | 'built_up_area'
  | 'faculty_student_ratio'
  | 'cad_labs'
  | 'library_titles'
  | 'fire_safety';

export type ComplianceStatus = 'pass' | 'gap' | 'needs_evidence' | 'needs_inspection';

export interface ComplianceResult {
  id: string;
  application_id: string;
  category: ComplianceCategory;
  item_name: string;
  rule_reference: string;
  declared_value: number | string;
  required_value: number | string;
  unit: string;
  status: ComplianceStatus;
  deficiency_description?: string;
  intake_impact?: number;
}

export interface CapacityCalculation {
  built_up_area_sqm: number;
  required_sqm_per_student: number;
  faculty_count: number;
  faculty_ratio_required: number;
  max_capacity_infrastructure: number;
  max_capacity_faculty: number;
  bottleneck_factor: 'infrastructure' | 'faculty' | 'balanced';
  applied_intake: number;
  suggested_approved_intake: number;
  explanation: string;
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  actor_id: string;
  actor_name: string;
  actor_role: string;
  action: string;
  entity_type: string;
  entity_id: string;
  details: string;
  prev_hash: string;
  curr_hash: string;
  ip_address: string;
  is_tampered?: boolean;
}

export type GraphNodeType = 'institution' | 'faculty' | 'land' | 'trust' | 'signatory' | 'stamp';

export interface GraphEntity {
  id: string;
  label: string;
  type: GraphNodeType;
  properties: Record<string, any>;
  flagged: boolean;
  flag_reasons?: string[];
}

export interface GraphRelation {
  id: string;
  source: string;
  target: string;
  type: string;
  label: string;
  flagged: boolean;
  flag_reason?: string;
  confidence?: number;
}

export interface GraphData {
  nodes: GraphEntity[];
  edges: GraphRelation[];
}

export interface ValidationInconsistency {
  field: string;
  source_a: string;
  val_a: string;
  source_b: string;
  val_b: string;
  severity: FlagSeverity;
}

export interface ValidationReport {
  application_id: string;
  total_rules_evaluated: number;
  passed_rules: number;
  failed_rules: number;
  missing_mandatory_documents: string[];
  inconsistencies: ValidationInconsistency[];
  recommendations: string[];
}

export interface TimelineEvent {
  id: string;
  application_id: string;
  timestamp: string;
  title: string;
  description: string;
  actor: string;
  type: 'status_change' | 'document_uploaded' | 'flag_raised' | 'flag_resolved' | 'deficiency_issued' | 'approved';
}

export interface ResubmissionDiff {
  previous_version: number;
  current_version: number;
  added_documents: string[];
  removed_documents: string[];
  modified_documents: string[];
  changed_fields: {
    field: string;
    old_value: any;
    new_value: any;
  }[];
}

export interface EvaluationCheckMetric {
  check_name: string;
  precision: number;
  recall: number;
  f1: number;
  sample_count: number;
  status: 'pass' | 'fail' | 'PASS' | 'NOT RUN' | 'REVIEW' | string;
}

export interface EvaluationResult {
  id: string;
  test_set_name: string;
  total_samples: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  execution_time_ms: number;
  evaluated_at: string;
  detailed_checks: EvaluationCheckMetric[];
}

export type AlertCategory =
  | 'missing_docs'
  | 'expired'
  | 'pending_verification'
  | 'anomalies'
  | 'unresolved';

export interface Alert {
  id: string;
  category: AlertCategory;
  severity: FlagSeverity;
  title: string;
  description: string;
  application_id: string;
  application_number: string;
  institution_name: string;
  created_at: string;
  is_resolved: boolean;
}

export interface DeficiencyItem {
  rule_id: string;
  deficiency: string;
  action_required: string;
  deadline_days: number;
}

export interface DeficiencyLetter {
  id: string;
  application_id: string;
  application_number: string;
  institution_name: string;
  academic_year: string;
  date: string;
  language: 'en' | 'ta' | 'hi';
  subject: string;
  body_content: string;
  deficiency_items: DeficiencyItem[];
  status: 'draft' | 'approved' | 'sent';
  approved_by?: string;
  approved_at?: string;
  gemini_improved?: boolean;
}

export interface AnalyticsSummary {
  total_applications: number;
  pending_review: number;
  approved_applications: number;
  rejected_applications: number;
  flags_by_severity: {
    info: number;
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  flags_by_type: { type: string; count: number }[];
  verification_outcomes: { name: string; value: number; color: string }[];
  applications_by_status: { status: string; count: number }[];
  processing_times_trend: { week: string; avg_days: number }[];
  average_risk_score: number;
  chain_integrity_status: 'verified' | 'compromised';
}
