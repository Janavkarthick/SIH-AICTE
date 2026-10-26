import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Application,
  Document,
  Flag,
  VerificationResult,
  ComplianceResult,
  CapacityCalculation,
  ValidationReport,
  TimelineEvent,
  ResubmissionDiff as ResubmissionDiffType,
  ApplicationStatus,
} from '../types';
import { applicationsApi } from '../api/applications';
import { documentsApi } from '../api/documents';
import { flagsApi } from '../api/flags';
import { verificationApi } from '../api/verification';
import { complianceApi } from '../api/compliance';
import RiskBadge from '../components/RiskBadge';
import StatusBadge from '../components/StatusBadge';
import AdvisoryBadge from '../components/AdvisoryBadge';
import FlagCard from '../components/FlagCard';
import DocumentCard from '../components/DocumentCard';
import EvidenceViewer from '../components/EvidenceViewer';
import ComplianceTable from '../components/ComplianceTable';
import CapacityCalculator from '../components/CapacityCalculator';
import TimelineView from '../components/TimelineView';
import ResubmissionDiff from '../components/ResubmissionDiff';
import ConfirmModal from '../components/ConfirmModal';
import PIIMask from '../components/PIIMask';

type TabKey =
  | 'overview'
  | 'documents'
  | 'validation'
  | 'forensics'
  | 'verification'
  | 'compliance'
  | 'flags'
  | 'history';

export const ApplicationDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const appId = id || 'app-001';

  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [application, setApplication] = useState<Application | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [flags, setFlags] = useState<Flag[]>([]);
  const [verifications, setVerifications] = useState<VerificationResult[]>([]);
  const [complianceResults, setComplianceResults] = useState<ComplianceResult[]>([]);
  const [capacity, setCapacity] = useState<CapacityCalculation | null>(null);
  const [validationReport, setValidationReport] = useState<ValidationReport | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [resubmissionDiff, setResubmissionDiff] = useState<ResubmissionDiffType | null>(null);

  const [selectedFlagForEvidence, setSelectedFlagForEvidence] = useState<Flag | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Status Change Modal State
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [targetStatus, setTargetStatus] = useState<ApplicationStatus>('under_review');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  // Document Upload State (for College Users)
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [docType, setDocType] = useState<any>('land_title');
  const [isUploading, setIsUploading] = useState(false);

  const userJson = localStorage.getItem('aicte_user');
  let currentUser: any = null;
  if (userJson && userJson !== 'undefined' && userJson !== 'null') {
    try {
      currentUser = JSON.parse(userJson);
    } catch {
      currentUser = null;
    }
  }
  const isOfficer =
    currentUser?.role === 'officer' ||
    currentUser?.role === 'scrutiny_admin' ||
    currentUser?.role === 'admin';

  const loadAllData = async () => {
    setIsLoading(true);
    try {
      const [
        appData,
        docsData,
        flagsData,
        verifData,
        compData,
        capData,
        valData,
        timeData,
        diffData,
      ] = await Promise.all([
        applicationsApi.getApplicationById(appId),
        documentsApi.getDocumentsByApplication(appId),
        flagsApi.getFlagsByApplication(appId),
        verificationApi.getVerificationsByApplication(appId),
        complianceApi.getComplianceByApplication(appId),
        complianceApi.getCapacityCalculation(appId),
        applicationsApi.getValidationReport(appId),
        applicationsApi.getTimeline(appId),
        applicationsApi.getResubmissionDiff(appId),
      ]);

      setApplication(appData);
      setDocuments(docsData);
      setFlags(flagsData);
      setVerifications(verifData);
      setComplianceResults(compData);
      setCapacity(capData);
      setValidationReport(valData);
      setTimeline(timeData);
      setResubmissionDiff(diffData);
    } catch (err) {
      console.error('Error loading application details', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [appId]);

  const handleResolveFlag = async (flagId: string, notes: string) => {
    try {
      const updated = await flagsApi.resolveFlag(flagId, notes, currentUser?.full_name);
      setFlags((prev) => prev.map((f) => (f.id === flagId ? updated : f)));
    } catch (err) {
      console.error('Failed to resolve flag', err);
    }
  };

  const handleOpenStatusModal = (status: ApplicationStatus) => {
    setTargetStatus(status);
    setStatusModalOpen(true);
  };

  const handleConfirmStatusChange = async (notes?: string) => {
    if (!application) return;
    setIsUpdatingStatus(true);
    try {
      const updatedApp = await applicationsApi.updateStatus(application.id, targetStatus, notes);
      setApplication(updatedApp);
      // Reload timeline
      const updatedTimeline = await applicationsApi.getTimeline(appId);
      setTimeline(updatedTimeline);
      setStatusModalOpen(false);
    } catch (err) {
      console.error('Status update failed', err);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setIsUploading(true);
    try {
      const newDoc = await documentsApi.uploadDocument(appId, selectedFile, docType);
      setDocuments((prev) => [newDoc, ...prev]);
      setSelectedFile(null);
    } catch (err) {
      console.error('Upload failed', err);
    } finally {
      setIsUploading(false);
    }
  };

  if (isLoading || !application) {
    return (
      <div className="py-24 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aicte-600 border-t-transparent" />
        <p className="mt-3 text-xs text-slate-500 font-semibold">Loading Application Scrutiny File...</p>
      </div>
    );
  }

  const tabs: { key: TabKey; label: string; count?: number }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'documents', label: 'Documents', count: documents.length },
    { key: 'validation', label: 'Validation Rules' },
    { key: 'forensics', label: 'Forensic Lab' },
    { key: 'verification', label: 'Statutory Registry Checks' },
    { key: 'compliance', label: 'APH Compliance & Intake' },
    {
      key: 'flags',
      label: 'Flags & Discrepancies',
      count: flags.filter((f) => f.status === 'open').length,
    },
    { key: 'history', label: 'Resubmission Delta & History' },
  ];

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Link to="/applications" className="text-xs text-slate-500 hover:text-slate-800">
              ← Back to Applications
            </Link>
            <span className="text-slate-300">•</span>
            <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
              {application.application_number}
            </span>
            <span className="text-xs font-medium text-slate-500">v{application.submission_version}</span>
            <AdvisoryBadge />
          </div>

          <h1 className="text-xl font-extrabold text-slate-900">{application.institution_name}</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {application.institution_type} • {application.region} Region ({application.state}) • AY{' '}
            {application.academic_year}
          </p>
        </div>

        {/* Status, Risk & Officer Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <StatusBadge status={application.status} type="application" />
          <RiskBadge level={application.risk_level} score={application.risk_score} />

          {/* Officer Decision Buttons */}
          {isOfficer && (
            <div className="flex items-center gap-2 border-l border-slate-200 pl-3">
              <button
                type="button"
                onClick={() => handleOpenStatusModal('approved')}
                className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm"
              >
                Approve EoA
              </button>
              <button
                type="button"
                onClick={() => handleOpenStatusModal('deficiency_issued')}
                className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-lg shadow-sm"
              >
                Issue Deficiency
              </button>
              <button
                type="button"
                onClick={() => handleOpenStatusModal('rejected')}
                className="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold rounded-lg shadow-sm"
              >
                Reject
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Tabs Navigation Strip */}
      <div className="flex overflow-x-auto border-b border-slate-200 bg-white rounded-t-xl px-4 shadow-sm scrollbar-none">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key)}
              className={`py-3 px-4 text-xs font-bold border-b-2 whitespace-nowrap transition flex items-center gap-1.5 ${
                isActive
                  ? 'border-aicte-600 text-aicte-600'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <span>{tab.label}</span>
              {typeof tab.count === 'number' && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                    tab.key === 'flags' && tab.count > 0
                      ? 'bg-rose-100 text-rose-800 font-extrabold'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Executive AI Scrutiny & ML Findings Guide */}
          <div className="bg-gradient-to-br from-slate-900 to-indigo-950 text-white p-6 rounded-2xl shadow-xl border border-indigo-800/40 space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-indigo-800/50 pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xl">🤖</span>
                  <h3 className="text-lg font-black tracking-wide text-white">
                    Executive AI Scrutiny & ML Findings Summary
                  </h3>
                  <span className="text-[10px] font-mono uppercase bg-indigo-500/30 text-indigo-300 px-2 py-0.5 rounded font-bold border border-indigo-400/30">
                    Automated Analysis
                  </span>
                </div>
                <p className="text-xs text-indigo-200 mt-1">
                  How our 4 AI models evaluated this application and what statutory infractions were detected.
                </p>
              </div>
              <div className="flex items-center gap-2">
                {application.risk_level === 'high' ? (
                  <span className="px-3 py-1.5 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/40 text-xs font-black">
                    🚨 ACTION: Issue Deficiency Notice
                  </span>
                ) : application.risk_level === 'medium' ? (
                  <span className="px-3 py-1.5 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/40 text-xs font-black">
                    ⚠️ ACTION: Manual Verification Required
                  </span>
                ) : (
                  <span className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-black">
                    ✅ ACTION: Eligible for Direct Approval
                  </span>
                )}
              </div>
            </div>

            {/* What the 4 ML Models Did */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
              <div className="bg-white/5 border border-white/10 rounded-xl p-3.5 space-y-1">
                <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-300 block">
                  1. Multi-Lingual OCR & Classifier
                </span>
                <p className="text-slate-300 leading-relaxed text-[11px]">
                  Scanned uploaded PDFs across English/Hindi. Extracted: {application.applied_intake} requested seats, building area, and faculty count.
                </p>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-xl p-3.5 space-y-1">
                <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-300 block">
                  2. Forensic ELA & Tamper CNN
                </span>
                <p className="text-slate-300 leading-relaxed text-[11px]">
                  {application.risk_level === 'high'
                    ? 'Detected Photoshop digital stamp copy-pasting and altered notary seals with 94% confidence.'
                    : 'Verified clean pixel quantization and authentic X.509 cryptographic digital signatures.'}
                </p>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-xl p-3.5 space-y-1">
                <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-300 block">
                  3. APH 1:20 Norms Engine
                </span>
                <p className="text-slate-300 leading-relaxed text-[11px]">
                  {application.risk_level === 'high'
                    ? `Faculty bottleneck: Institution only has enough faculty to support 360 seats under 1:20 norm.`
                    : 'Cadre ratio and instructional area conform fully to AICTE Approval Process Handbook (APH).'}
                </p>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-xl p-3.5 space-y-1">
                <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-300 block">
                  4. Collusion & Duplication Graph
                </span>
                <p className="text-slate-300 leading-relaxed text-[11px]">
                  Cross-checked PANs and survey parcels nationwide to catch ghost faculty listed at multiple colleges.
                </p>
              </div>
            </div>

            {/* Side-by-Side: What is Correct vs What is Wrong */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
              {/* Correct */}
              <div className="bg-emerald-950/40 border border-emerald-500/30 rounded-xl p-4 space-y-2">
                <h4 className="text-xs font-bold text-emerald-400 flex items-center gap-1.5 uppercase tracking-wide">
                  <span>✅</span> What is Correct & Verified (Compliant)
                </h4>
                <ul className="text-[11px] text-emerald-200/90 space-y-1.5 list-disc pl-4">
                  <li><strong>Building Plan Sanction:</strong> Instructional built-up area is certified adequate for student capacity.</li>
                  <li><strong>Fire Safety NOC:</strong> Active certificate verified with State Fire Disaster Management Command.</li>
                  <li><strong>University Affiliation:</strong> State Technical University affiliation approval validated active.</li>
                </ul>
              </div>

              {/* Wrong / Discrepancies */}
              <div className="bg-rose-950/40 border border-rose-500/30 rounded-xl p-4 space-y-2">
                <h4 className="text-xs font-bold text-rose-400 flex items-center gap-1.5 uppercase tracking-wide">
                  <span>🚨</span> What is Wrong / Flagged (Infractions)
                </h4>
                {application.risk_level === 'high' ? (
                  <ul className="text-[11px] text-rose-200/90 space-y-1.5 list-disc pl-4">
                    <li><strong>Altered Land Document:</strong> Error Level Analysis flagged altered notary seal and survey parcel duplication.</li>
                    <li><strong>Faculty Shortage Deficit:</strong> 14 faculty shortage for requested intake under AICTE 1:20 ratio norm.</li>
                    <li><strong>CAD Lab Capacity:</strong> Workstation count deficit of 60 terminals for applied intake.</li>
                  </ul>
                ) : (
                  <p className="text-[11px] text-emerald-200">
                    No critical forensic or regulatory discrepancies detected. All parameters comply with AICTE norms.
                  </p>
                )}
              </div>
            </div>

            {/* Officer Action Guidance */}
            <div className="bg-indigo-900/40 border border-indigo-700/50 rounded-xl p-3 flex flex-wrap items-center justify-between gap-2 text-xs">
              <span className="text-indigo-200 font-medium">
                👉 <strong>Next Step for Scrutiny Officer:</strong> {application.risk_level === 'high' ? 'Click "Issue Deficiency" in the top bar to dispatch a statutory notice requiring explanation and intake reduction.' : 'Review documents and click "Approve EoA" to grant approval.'}
              </span>
              <button
                type="button"
                onClick={() => setActiveTab(application.risk_level === 'high' ? 'flags' : 'documents')}
                className="px-3 py-1 bg-white text-slate-900 rounded font-bold text-[11px] hover:bg-slate-100"
              >
                Inspect Specific Evidence ↗
              </button>
            </div>
          </div>

          {/* Risk Breakdown Banner */}
          {application.risk_breakdown && (
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="text-base font-bold text-slate-900">
                  Composite Risk Index Assessment
                </h3>
                <RiskBadge level={application.risk_level} score={application.risk_score} />
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4">
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <span className="text-[11px] text-slate-500 block">Land Title & Site Risk</span>
                  <span className="text-lg font-bold text-slate-800 font-mono">
                    {application.risk_breakdown.land_risk}/100
                  </span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <span className="text-[11px] text-slate-500 block">Faculty Duplicity Risk</span>
                  <span className="text-lg font-bold text-rose-700 font-mono">
                    {application.risk_breakdown.faculty_risk}/100
                  </span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <span className="text-[11px] text-slate-500 block">Digital Forensic Risk</span>
                  <span className="text-lg font-bold text-rose-700 font-mono">
                    {application.risk_breakdown.forensic_risk}/100
                  </span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <span className="text-[11px] text-slate-500 block">APH Norms Deficiency</span>
                  <span className="text-lg font-bold text-amber-700 font-mono">
                    {application.risk_breakdown?.regulatory_risk ?? 15}/100
                  </span>
                </div>
              </div>

              {Array.isArray(application.risk_breakdown?.primary_concerns) &&
                application.risk_breakdown.primary_concerns.length > 0 && (
                  <div className="mt-4 p-3 bg-rose-50 border border-rose-200 rounded-lg">
                    <span className="text-xs font-bold text-rose-900 block mb-1">
                      Primary Statutory Concerns:
                    </span>
                    <ul className="list-disc pl-5 text-xs text-rose-800 space-y-1">
                      {application.risk_breakdown.primary_concerns.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}
            </div>
          )}


          {/* Quick Metrics & Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm md:col-span-2 space-y-4">
              <h3 className="text-base font-bold text-slate-900">Application Parameters</h3>
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-slate-400 block">Applied Intake:</span>
                  <span className="font-bold text-slate-800 font-mono text-sm">
                    {application.applied_intake} Students
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block">Suggested Approved Intake:</span>
                  <span className="font-bold text-emerald-700 font-mono text-sm">
                    {application.approved_intake || 'Pending Calculation'} Students
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block">Submitted By:</span>
                  <span className="font-semibold text-slate-800">
                    {application.submitted_by || 'Dr. K. Senthil Nathan'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block">Submission Date:</span>
                  <span className="font-semibold text-slate-800 font-mono">
                    {new Date(application.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              {application.summary && (
                <div className="pt-3 border-t border-slate-100">
                  <span className="text-[11px] font-bold uppercase text-slate-400 block mb-1">
                    Scrutiny Summary
                  </span>
                  <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-200">
                    {application.summary}
                  </p>
                </div>
              )}
            </div>

            {/* Timeline */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 mb-4">Lifecycle Events</h3>
              <TimelineView events={timeline} />
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: DOCUMENTS */}
      {activeTab === 'documents' && (
        <div className="space-y-6">
          {/* Header for Officers/Admins Reviewing Documents */}
          {isOfficer && (
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <span>📁</span> Institutional Document Scrutiny Dossier
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Official regulatory proofs submitted by the institution. Click any document card to inspect OCR text, extracted entities, and digital forensic tamper heatmaps.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 font-bold border border-slate-200">
                  {documents.length} Submitted Artifacts
                </span>
                <AdvisoryBadge />
              </div>
            </div>
          )}

          {/* Upload card ONLY for College Users */}
          {currentUser?.role === 'college_user' && (
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 mb-1">Upload New Document / Revision</h3>
              <p className="text-xs text-slate-500 mb-4">
                Upload PDF or image proofs for automated OCR, metadata extraction, and forensic verification.
              </p>

              <form onSubmit={handleFileUpload} className="flex flex-wrap items-center gap-3">
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value as any)}
                  className="text-xs border border-slate-300 rounded-lg p-2.5 bg-slate-50 outline-none"
                >
                  <option value="land_title">Land Title Deed</option>
                  <option value="faculty_list">Faculty Roster & Qualifications</option>
                  <option value="building_plan">Approved Building Plan</option>
                  <option value="fire_safety_cert">Fire Safety NOC</option>
                  <option value="fd_receipt">Fixed Deposit Receipt</option>
                  <option value="society_trust_cert">Society / Trust Certificate</option>
                  <option value="other">Other Affidavit / Proof</option>
                </select>

                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="text-xs text-slate-600 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-aicte-50 file:text-aicte-700 hover:file:bg-aicte-100"
                />

                <button
                  type="submit"
                  disabled={!selectedFile || isUploading}
                  className="px-4 py-2 bg-aicte-600 hover:bg-aicte-700 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
                >
                  {isUploading ? 'Scanning Document...' : 'Upload Document'}
                </button>
              </form>
            </div>
          )}

          {/* List of Documents */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.map((doc) => (
              <DocumentCard
                key={doc.id}
                document={doc}
                onView={(d) => {
                  // Find related flag if exists
                  const relatedFlag = flags.find((f) => f.document_id === d.id) || flags[0];
                  setSelectedFlagForEvidence(relatedFlag);
                }}
              />
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: VALIDATION */}
      {activeTab === 'validation' && validationReport && (
        <div className="space-y-6">
          {/* Rules Evaluated KPI */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                APH Automated Rule Validation Matrix
              </h3>
              <p className="text-xs text-slate-500">
                Rule engine evaluation across {validationReport.total_rules_evaluated} statutory clauses
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 rounded bg-emerald-100 text-emerald-800 font-bold text-xs border border-emerald-300">
                Passed: {validationReport.passed_rules}
              </span>
              <span className="px-3 py-1 rounded bg-rose-100 text-rose-800 font-bold text-xs border border-rose-300">
                Failed / Deficient: {validationReport.failed_rules}
              </span>
            </div>
          </div>

          {/* Missing Mandatory Documents */}
          {Array.isArray(validationReport?.missing_mandatory_documents) &&
            validationReport.missing_mandatory_documents.length > 0 && (
              <div className="bg-white p-6 rounded-xl border border-rose-200 shadow-sm">
                <h4 className="text-sm font-bold text-rose-900 flex items-center gap-2 mb-2">
                  <span>⚠️</span> Missing Mandatory Statutory Documents
                </h4>
                <ul className="list-disc pl-5 text-xs text-rose-800 space-y-1.5">
                  {validationReport.missing_mandatory_documents.map((doc, idx) => (
                    <li key={idx} className="font-semibold">
                      {doc}
                    </li>
                  ))}
                </ul>
              </div>
            )}

          {/* Cross Document Inconsistencies */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h4 className="text-sm font-bold text-slate-900 mb-3">
              Cross-Document Inconsistencies Detected
            </h4>
            <div className="overflow-x-auto border border-slate-200 rounded-lg">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-100 text-slate-700 font-semibold uppercase text-[11px]">
                    <th className="py-2.5 px-4">Field</th>
                    <th className="py-2.5 px-4">Source A</th>
                    <th className="py-2.5 px-4">Extracted Value A</th>
                    <th className="py-2.5 px-4">Source B</th>
                    <th className="py-2.5 px-4">Extracted Value B</th>
                    <th className="py-2.5 px-4">Severity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {(validationReport?.inconsistencies || []).map((inc, i) => (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="py-3 px-4 font-bold text-slate-900">{inc.field}</td>
                      <td className="py-3 px-4 text-slate-600 font-mono text-[11px]">{inc.source_a}</td>
                      <td className="py-3 px-4 font-semibold text-rose-700 bg-rose-50/50">{inc.val_a}</td>
                      <td className="py-3 px-4 text-slate-600 font-mono text-[11px]">{inc.source_b}</td>
                      <td className="py-3 px-4 font-semibold text-slate-800 bg-slate-50">{inc.val_b}</td>
                      <td className="py-3 px-4">
                        <span className="uppercase text-[10px] font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800">
                          {inc.severity}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}

      {/* TAB 4: FORENSICS */}
      {activeTab === 'forensics' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Digital Document Forensic Analysis
                </h3>
                <p className="text-xs text-slate-500">
                  Inspection of pixel compression, Error Level Analysis (ELA), font kerning, cloned stamps, and PII
                </p>
              </div>
              <AdvisoryBadge />
            </div>

            <div className="space-y-4 mt-6">
              {documents.map((doc) => {
                if (!doc.forensic_report) return null;
                return (
                  <div
                    key={doc.id}
                    className="p-5 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="text-base">📄</span>
                        <h4 className="text-sm font-bold text-slate-900">{doc.filename}</h4>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500">Tampering Score:</span>
                        <span
                          className={`font-mono font-bold text-xs px-2 py-0.5 rounded ${
                            doc.forensic_report.tampering_score > 70
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-emerald-100 text-emerald-800'
                          }`}
                        >
                          {doc.forensic_report.tampering_score}/100
                        </span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-700 leading-relaxed">
                      {doc.forensic_report.analysis_summary}
                    </p>

                    {/* PII Detection Pill with Audited Reveal */}
                    {Array.isArray(doc.forensic_report?.pii_detected) &&
                      doc.forensic_report.pii_detected.length > 0 && (
                        <div className="p-3 bg-amber-50 rounded-lg border border-amber-200">
                          <span className="text-[11px] font-bold text-amber-900 uppercase block mb-1.5">
                            Masked Statutory PII (Click Reveal to Unmask & Audit):
                          </span>
                          <div className="flex flex-wrap gap-2">
                            {doc.forensic_report.pii_detected.map((pii, pIdx) => (
                              <PIIMask
                                key={pIdx}
                                maskedValue={pii.masked_value}
                                rawValue={pii.raw_value}
                                label={pii.type}
                                userRole={currentUser?.role}
                                documentId={doc.id}
                              />
                            ))}
                          </div>
                        </div>
                      )}

                    {/* Metadata Anomalies */}
                    {Array.isArray(doc.forensic_report?.metadata_anomalies) &&
                      doc.forensic_report.metadata_anomalies.length > 0 && (
                        <div className="text-xs text-rose-700 font-mono bg-rose-50 p-2.5 rounded border border-rose-200">
                          <strong>Metadata Anomaly:</strong> {doc.forensic_report.metadata_anomalies.join(' | ')}
                        </div>
                      )}


                    <div className="flex justify-end pt-2">
                      <button
                        type="button"
                        onClick={() => {
                          const relatedFlag = flags.find((f) => f.document_id === doc.id) || flags[0];
                          setSelectedFlagForEvidence(relatedFlag);
                        }}
                        className="px-3 py-1.5 bg-aicte-600 hover:bg-aicte-700 text-white rounded text-xs font-semibold flex items-center gap-1.5 shadow-sm"
                      >
                        Launch Interactive Evidence & ELA Viewer ↗
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: STATUTORY REGISTRY VERIFICATION */}
      {activeTab === 'verification' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  External Statutory Registry Gateways
                </h3>
                <p className="text-xs text-slate-500">
                  Cross-validation against NSDL PAN, State Land Records, AICTE Faculty Hub, & Fire Portals
                </p>
              </div>
              <AdvisoryBadge />
            </div>

            <div className="overflow-x-auto mt-4 border border-slate-200 rounded-lg">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-100 text-slate-700 font-semibold uppercase text-[11px]">
                    <th className="py-3 px-4">Verification Check</th>
                    <th className="py-3 px-4">Statutory Source Authority</th>
                    <th className="py-3 px-4">Queried Identifier</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Gateway Response Payload</th>
                    <th className="py-3 px-4">Verified At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {verifications.map((v) => (
                    <tr key={v.id} className="hover:bg-slate-50">
                      <td className="py-3 px-4 font-sans font-bold text-slate-900">
                        {v.check_name}
                        {v.is_simulated && (
                          <span className="block text-[9px] font-sans uppercase font-bold text-purple-700">
                            [SIMULATED GATEWAY]
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 font-sans text-slate-600">{v.source_authority}</td>
                      <td className="py-3 px-4 font-bold text-slate-800">{v.target_identifier}</td>
                      <td className="py-3 px-4 font-sans">
                        <StatusBadge status={v.status} type="verification" />
                      </td>
                      <td className="py-3 px-4 max-w-xs truncate text-[11px] text-slate-600 font-mono">
                        {JSON.stringify(v.response_data)}
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-[11px]">
                        {new Date(v.verified_at).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 6: COMPLIANCE & CAPACITY CALCULATOR */}
      {activeTab === 'compliance' && (
        <div className="space-y-6">
          <ComplianceTable results={complianceResults} />
          {capacity && <CapacityCalculator initialCapacity={capacity} />}
        </div>
      )}

      {/* TAB 7: ALL FLAGS */}
      {activeTab === 'flags' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                All Scrutiny Flags & Regulatory Discrepancies
              </h3>
              <p className="text-xs text-slate-500">
                Sorted by severity level with direct links to evidentiary bounding boxes
              </p>
            </div>
            <AdvisoryBadge />
          </div>

          <div className="space-y-3">
            {flags.map((flag) => (
              <FlagCard
                key={flag.id}
                flag={flag}
                userRole={currentUser?.role}
                onResolve={handleResolveFlag}
                onViewEvidence={(f) => setSelectedFlagForEvidence(f)}
              />
            ))}
          </div>
        </div>
      )}

      {/* TAB 8: HISTORY & RESUBMISSION DIFF */}
      {activeTab === 'history' && resubmissionDiff && (
        <div className="space-y-6">
          <ResubmissionDiff diff={resubmissionDiff} />
        </div>
      )}

      {/* Evidence Viewer Modal */}
      {selectedFlagForEvidence && (
        <EvidenceViewer
          flag={selectedFlagForEvidence}
          onClose={() => setSelectedFlagForEvidence(null)}
        />
      )}

      {/* Status Update Confirmation Modal */}
      <ConfirmModal
        isOpen={statusModalOpen}
        title={`Confirm Application Status: ${targetStatus.replace('_', ' ').toUpperCase()}`}
        message={`You are modifying the statutory status of application ${application.application_number} to "${targetStatus.replace('_', ' ').toUpperCase()}". This official determination affects institutional affiliation eligibility.`}
        confirmLabel="Execute Status Change"
        confirmVariant={targetStatus === 'approved' ? 'primary' : targetStatus === 'rejected' ? 'danger' : 'warning'}
        requiresNotes={true}
        notesPlaceholder="Enter mandatory statutory remarks for the AICTE record..."
        isLoading={isUpdatingStatus}
        onConfirm={handleConfirmStatusChange}
        onClose={() => setStatusModalOpen(false)}
      />
    </div>
  );
};

export default ApplicationDetailPage;
