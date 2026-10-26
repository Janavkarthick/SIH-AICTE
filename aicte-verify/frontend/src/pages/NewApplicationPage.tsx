import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Application, DocumentType } from '../types';
import { applicationsApi } from '../api/applications';
import { documentsApi } from '../api/documents';
import AdvisoryBadge from '../components/AdvisoryBadge';

interface UploadItem {
  id: string;
  label: string;
  docType: DocumentType;
  annexureRef: string;
  mandatory: boolean;
  description: string;
  file: File | null;
  uploaded: boolean;
}

export const NewApplicationPage: React.FC = () => {
  const navigate = useNavigate();

  const userJson = localStorage.getItem('aicte_user');
  let user: User | null = null;
  try {
    if (userJson && userJson !== 'undefined' && userJson !== 'null') {
      user = JSON.parse(userJson);
    }
  } catch {}

  const [currentStep, setCurrentStep] = useState<number>(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  // Step 1: Category & Institution
  const [approvalType, setApprovalType] = useState('extension_of_approval');
  const [academicYear, setAcademicYear] = useState('2025-2026');
  const [institutionName, setInstitutionName] = useState(user?.institution_name || (user?.id === '4' ? 'Apex Institute of Technology' : user?.id === '5' ? 'Zenith College of Engineering' : user?.id === '6' ? 'Northern Polytechnic Institute' : 'Eastern Academy of Science & Technology'));
  const [aictePermanentId, setAictePermanentId] = useState('1-100' + (user?.institution_id ? String(user.institution_id).padStart(3, '0') : '234'));
  const [institutionType, setInstitutionType] = useState('Private Self-Financing');
  const [trustName, setTrustName] = useState('Sri Krishna Educational & Charitable Trust');
  const [trustRegNo, setTrustRegNo] = useState('TR-TN-2004-981');
  const [campusAddress, setCampusAddress] = useState('45 Knowledge Park, OMR Highway');
  const [stateName, setStateName] = useState(user?.region === 'Northern' ? 'Uttar Pradesh' : user?.region === 'Western' ? 'Maharashtra' : user?.region === 'Eastern' ? 'West Bengal' : 'Tamil Nadu');
  const [district, setDistrict] = useState(user?.region === 'Northern' ? 'Lucknow' : user?.region === 'Western' ? 'Pune' : user?.region === 'Eastern' ? 'Kolkata' : 'Chennai');
  const [gpsCoordinates, setGpsCoordinates] = useState('12.9234° N, 80.1982° E');
  const [affiliatingUniversity, setAffiliatingUniversity] = useState(user?.region === 'Northern' ? 'Dr. A.P.J. Abdul Kalam Technical University (AKTU)' : user?.region === 'Western' ? 'Savitribai Phule Pune University (SPPU)' : user?.region === 'Eastern' ? 'Maulana Abul Kalam Azad University of Tech (MAKAUT)' : 'Anna University, Chennai');
  const [headOfInstitute, setHeadOfInstitute] = useState('Dr. S. Ranganathan, M.E., Ph.D.');

  // Step 2: Programme & Intake
  const [programme, setProgramme] = useState('Engineering & Technology');
  const [courseName, setCourseName] = useState('Computer Science and Engineering');
  const [educationLevel, setEducationLevel] = useState('Undergraduate (B.E. / B.Tech)');
  const [existingApprovedIntake, setExistingApprovedIntake] = useState(420);
  const [requestedIntake, setRequestedIntake] = useState(480);
  const [divisionsCount, setDivisionsCount] = useState(8);

  // Step 3: Infrastructure & Faculty
  const [totalLandAcres, setTotalLandAcres] = useState(7.5);
  const [landCategory, setLandCategory] = useState('Rural / Other Areas (Min 7.5 Acres)');
  const [builtUpAreaSqm, setBuiltUpAreaSqm] = useState(11200);
  const [classroomsCount, setClassroomsCount] = useState(24);
  const [cadWorkstations, setCadWorkstations] = useState(240);
  const [facultyCount, setFacultyCount] = useState(64);
  const [libraryTitles, setLibraryTitles] = useState(3200);
  const [libraryVolumes, setLibraryVolumes] = useState(15000);

  // Step 4: Statutory Document Uploads Checklist
  const [documentsList, setDocumentsList] = useState<UploadItem[]>([
    {
      id: 'doc-affidavit',
      label: 'Affidavit 2 (Notarized & Digitally Signed)',
      docType: 'affidavit',
      annexureRef: '[Reference - verify against Approval Process Handbook] (illustrative)',
      mandatory: true,
      description: 'Prescribed affidavit on non-judicial stamp paper attested by Executive Magistrate or Notary Public with QR/digital stamp.',
      file: null,
      uploaded: false,
    },
    {
      id: 'doc-fire-noc',
      label: 'Fire Safety Certificate & NOC',
      docType: 'fire_safety_cert',
      annexureRef: '[Reference - verify against Approval Process Handbook] (illustrative)',
      mandatory: true,
      description: 'Valid certificate issued by the competent State Fire and Disaster Management Command.',
      file: null,
      uploaded: false,
    },
    {
      id: 'doc-occupancy',
      label: 'Occupancy / Building Completion Certificate (Form D)',
      docType: 'building_plan',
      annexureRef: '[Reference - verify against Approval Process Handbook] (illustrative)',
      mandatory: true,
      description: 'Valid building licence, occupancy permit, or Form D from Municipal Corporation / Town Planning authority.',
      file: null,
      uploaded: false,
    },
    {
      id: 'doc-land-deed',
      label: 'Land Title & Ownership Conversion Deed',
      docType: 'land_title',
      annexureRef: '[Reference - verify against Approval Process Handbook] (illustrative)',
      mandatory: true,
      description: 'Registered sale deed, gift deed, or government lease agreement establishing unencumbered contiguous plot.',
      file: null,
      uploaded: false,
    },
    {
      id: 'doc-faculty-roster',
      label: 'Faculty Cadre Roster & Qualification Proofs',
      docType: 'faculty_list',
      annexureRef: '[Reference - verify against Approval Process Handbook] (illustrative)',
      mandatory: true,
      description: 'Signed cadre roster with Professor, Associate, and Assistant Professor cadre ratios including PAN/Aadhaar hashes.',
      file: null,
      uploaded: false,
    },
    {
      id: 'doc-satellite-map',
      label: 'Geo-Tagged Satellite Entrance Map',
      docType: 'other',
      annexureRef: '[Reference - verify against Approval Process Handbook] (illustrative)',
      mandatory: true,
      description: 'Satellite map showing the campus location, approach road, and latitude/longitude at the main entrance.',
      file: null,
      uploaded: false,
    },
    {
      id: 'doc-audited-financials',
      label: 'Audited Financial Statements (Previous FY)',
      docType: 'fd_receipt',
      annexureRef: '[Reference - verify against Approval Process Handbook] (illustrative)',
      mandatory: false,
      description: 'Chartered Accountant certified balance sheet and income/expenditure statement of the applicant trust/society.',
      file: null,
      uploaded: false,
    },
  ]);

  // Step 5: Statutory Undertaking
  const [statutoryDeclaration, setStatutoryDeclaration] = useState(false);

  const handleFileChange = (docId: string, file: File | null) => {
    setDocumentsList((prev) =>
      prev.map((item) => (item.id === docId ? { ...item, file, uploaded: !!file } : item))
    );
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!statutoryDeclaration) {
      setSubmitError('You must formally affirm the statutory undertaking before final submission.');
      return;
    }
    setSubmitError('');
    setIsSubmitting(true);

    try {
      // 1. Create Application
      const payload: any = {
        institution_id: user?.institution_id ? Number(user.institution_id) : 1,
        institution_name: institutionName,
        category: approvalType,
        academic_year: academicYear,
        intake_applied: requestedIntake,
        current_intake: existingApprovedIntake,
        applied_intake: requestedIntake,
        approved_intake: existingApprovedIntake,
        summary: `APH 2024-27 Application for ${approvalType.replace('_', ' ').toUpperCase()} in ${programme} (${courseName}). Declared land: ${totalLandAcres} acres, Built-up: ${builtUpAreaSqm} sqm, Faculty: ${facultyCount}.`,
      };

      const createdApp = await applicationsApi.createApplication(payload);

      // 2. Upload any attached files to this application
      for (const doc of documentsList) {
        if (doc.file) {
          try {
            await documentsApi.uploadDocument(createdApp.id, doc.file, doc.docType);
          } catch (uploadErr) {
            console.warn(`Could not upload ${doc.label}:`, uploadErr);
          }
        }
      }

      // 3. Redirect directly to the newly submitted application dossier
      navigate(`/applications/${createdApp.id}`);
    } catch (err: any) {
      console.error('Failed to submit application', err);
      setSubmitError(err?.response?.data?.detail || 'Application submission failed. Please verify fields and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const steps = [
    { num: 1, title: 'Category & Institution' },
    { num: 2, title: 'Programmes & Intake' },
    { num: 3, title: 'Infrastructure & Faculty' },
    { num: 4, title: 'Document Uploads Checklist' },
    { num: 5, title: 'Review & Undertaking' },
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Official Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-5">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-aicte-600 to-indigo-800 text-white flex items-center justify-center font-extrabold text-lg shadow-sm">
              AICTE
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-black text-slate-900 tracking-tight">
                  Approval Process System (APH 2024–25 to 2026–27)
                </h1>
                <AdvisoryBadge size="sm" />
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                All India Council for Technical Education • Statutory Online Regulatory Affiliation Dossier
              </p>
            </div>
          </div>
          <Link
            to="/applications"
            className="text-xs font-semibold text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 transition"
          >
            ← View My Submissions
          </Link>
        </div>

        {/* Step Progress Bar */}
        <div className="mt-6">
          <div className="grid grid-cols-5 gap-2">
            {steps.map((s) => (
              <button
                key={s.num}
                type="button"
                onClick={() => setCurrentStep(s.num)}
                className={`text-left p-3 rounded-xl border transition ${
                  currentStep === s.num
                    ? 'border-aicte-600 bg-aicte-50/60 ring-2 ring-aicte-600/20'
                    : currentStep > s.num
                    ? 'border-emerald-300 bg-emerald-50/40 text-emerald-800'
                    : 'border-slate-200 bg-slate-50 text-slate-400'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold ${
                      currentStep === s.num
                        ? 'bg-aicte-600 text-white'
                        : currentStep > s.num
                        ? 'bg-emerald-600 text-white'
                        : 'bg-slate-200 text-slate-600'
                    }`}
                  >
                    {currentStep > s.num ? '✓' : s.num}
                  </span>
                  <span className="text-xs font-bold truncate">{s.title}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Form Content */}
      <form onSubmit={handleFormSubmit} className="space-y-6">
        {submitError && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs font-semibold flex items-center gap-2">
            <span>⚠️</span> {submitError}
          </div>
        )}

        {/* STEP 1: CATEGORY & INSTITUTION DETAILS */}
        {currentStep === 1 && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-6">
            <div className="border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-900">
                1. What Approval is the College Applying For?
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Select the regulatory category defined under the AICTE Approval Process Handbook (APH)
              </p>
            </div>

            {/* Application Category Radio Selector */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {[
                {
                  id: 'extension_of_approval',
                  title: '1. Extension of Approval (EoA)',
                  desc: 'Annual renewal for existing technical institutions to continue offering AICTE-regulated programmes.',
                  badge: 'Existing Colleges',
                },
                {
                  id: 'increase_of_intake',
                  title: '2. Increasing or Changing Student Intake',
                  desc: 'Approval for additional seats, new divisions, or revised intake in existing approved programmes.',
                  badge: 'Expansion',
                },
                {
                  id: 'new_course',
                  title: '3. Starting a New Course or Programme',
                  desc: 'Introduction of emerging programmes (e.g., Artificial Intelligence, Cybersecurity, Robotics).',
                  badge: 'New Division',
                },
                {
                  id: 'new_institution',
                  title: '4. Approval for a New Institution',
                  desc: 'Initial establishment and statutory permission for newly founded technical campuses.',
                  badge: 'Initial Setup',
                },
              ].map((cat) => (
                <label
                  key={cat.id}
                  className={`p-4 rounded-xl border cursor-pointer transition flex items-start gap-3 ${
                    approvalType === cat.id
                      ? 'border-aicte-600 bg-aicte-50/40 ring-1 ring-aicte-600'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="approvalCategory"
                    value={cat.id}
                    checked={approvalType === cat.id}
                    onChange={(e) => setApprovalType(e.target.value)}
                    className="mt-1 text-aicte-600 focus:ring-0"
                  />
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-900">{cat.title}</span>
                      <span className="text-[10px] font-semibold bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                        {cat.badge}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 leading-relaxed">{cat.desc}</p>
                  </div>
                </label>
              ))}
            </div>

            <div className="border-t border-slate-100 pt-5">
              <h3 className="text-sm font-bold text-slate-900 mb-3">
                A. Institution Identification & Campus Particulars
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">AICTE Permanent ID (PID)</label>
                  <input
                    type="text"
                    value={aictePermanentId}
                    onChange={(e) => setAictePermanentId(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-2.5 font-mono font-bold bg-slate-50 text-slate-800"
                    required
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block font-bold text-slate-700 mb-1">Official Name of Institution</label>
                  <input
                    type="text"
                    value={institutionName}
                    onChange={(e) => setInstitutionName(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-2.5 font-bold text-slate-800"
                    required
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 mb-1">Institution Category / Type</label>
                  <select
                    value={institutionType}
                    onChange={(e) => setInstitutionType(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-2.5 bg-slate-50"
                  >
                    <option value="Private Self-Financing">Private Self-Financing</option>
                    <option value="Government / State University">Government / State University</option>
                    <option value="Govt-Aided Technical Campus">Govt-Aided Technical Campus</option>
                    <option value="Deemed University Institute">Deemed University Institute</option>
                  </select>
                </div>

                <div>
                  <label className="block font-bold text-slate-700 mb-1">Target Academic Year</label>
                  <select
                    value={academicYear}
                    onChange={(e) => setAcademicYear(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-2.5 bg-slate-50 font-bold"
                  >
                    <option value="2025-2026">AY 2025-2026 (Current Review Cycle)</option>
                    <option value="2026-2027">AY 2026-2027 (Next Advance Cycle)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-bold text-slate-700 mb-1">Sponsoring Trust / Society</label>
                  <input
                    type="text"
                    value={trustName}
                    onChange={(e) => setTrustName(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-2.5"
                    required
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block font-bold text-slate-700 mb-1">Full Campus Postal Address</label>
                  <input
                    type="text"
                    value={campusAddress}
                    onChange={(e) => setCampusAddress(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-2.5"
                    required
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 mb-1">State & Region</label>
                  <input
                    type="text"
                    value={`${stateName} (${user?.region || 'Regional'} Office)`}
                    readOnly
                    className="w-full border border-slate-200 rounded-lg p-2.5 bg-slate-100 text-slate-600 font-semibold cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 mb-1">Geographical GPS Coordinates</label>
                  <input
                    type="text"
                    value={gpsCoordinates}
                    onChange={(e) => setGpsCoordinates(e.target.value)}
                    placeholder="e.g. 12.9234° N, 80.1982° E"
                    className="w-full border border-slate-300 rounded-lg p-2.5 font-mono"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block font-bold text-slate-700 mb-1">Affiliating University / Examining Board</label>
                  <input
                    type="text"
                    value={affiliatingUniversity}
                    onChange={(e) => setAffiliatingUniversity(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-2.5 font-semibold text-slate-800"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCurrentStep(2)}
                className="px-5 py-2.5 bg-aicte-600 hover:bg-aicte-700 text-white rounded-lg text-xs font-bold shadow transition flex items-center gap-1.5"
              >
                Proceed to Programmes & Intake →
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: PROGRAMMES & INTAKE */}
        {currentStep === 2 && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-6">
            <div className="border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-900">
                2. Programme, Course & Student Intake Declaration
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Which programmes does the college offer, and how many student seats are requested?
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Programme Name</label>
                <select
                  value={programme}
                  onChange={(e) => setProgramme(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2.5 bg-slate-50 font-semibold"
                >
                  <option value="Engineering & Technology">Engineering & Technology</option>
                  <option value="Management (MBA / PGDM)">Management (MBA / PGDM)</option>
                  <option value="Computer Applications (MCA)">Computer Applications (MCA)</option>
                  <option value="Pharmacy">Pharmacy</option>
                  <option value="Architecture & Planning">Architecture & Planning</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Primary Branch / Course Name</label>
                <input
                  type="text"
                  value={courseName}
                  onChange={(e) => setCourseName(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2.5 font-bold"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Education Level</label>
                <select
                  value={educationLevel}
                  onChange={(e) => setEducationLevel(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2.5 bg-slate-50"
                >
                  <option value="Undergraduate (B.E. / B.Tech)">Undergraduate (B.E. / B.Tech)</option>
                  <option value="Postgraduate (M.E. / M.Tech)">Postgraduate (M.E. / M.Tech)</option>
                  <option value="Diploma in Engineering">Diploma in Engineering</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Number of Approved Divisions</label>
                <input
                  type="number"
                  min="1"
                  max="12"
                  value={divisionsCount}
                  onChange={(e) => setDivisionsCount(Number(e.target.value))}
                  className="w-full border border-slate-300 rounded-lg p-2.5 font-mono"
                />
              </div>

              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                <label className="block font-bold text-slate-700 mb-1">Existing Approved Intake (Seats)</label>
                <input
                  type="number"
                  min="60"
                  step="30"
                  value={existingApprovedIntake}
                  onChange={(e) => setExistingApprovedIntake(Number(e.target.value))}
                  className="w-full border border-slate-300 rounded-lg p-2.5 font-mono font-bold text-slate-800 text-sm"
                  required
                />
                <span className="text-[11px] text-slate-400 mt-1 block">Sanctioned in previous AICTE EoA order</span>
              </div>

              <div className="p-4 bg-indigo-50/50 rounded-xl border border-indigo-200">
                <label className="block font-bold text-indigo-950 mb-1">Requested Intake for AY {academicYear} (Seats)</label>
                <input
                  type="number"
                  min="60"
                  step="30"
                  value={requestedIntake}
                  onChange={(e) => setRequestedIntake(Number(e.target.value))}
                  className="w-full border border-indigo-300 rounded-lg p-2.5 font-mono font-black text-indigo-700 text-sm"
                  required
                />
                <span className="text-[11px] text-indigo-600 mt-1 block">
                  Delta: {requestedIntake > existingApprovedIntake ? `+${requestedIntake - existingApprovedIntake} additional seats requested` : 'Renewal of existing capacity'}
                </span>
              </div>
            </div>

            <div className="flex justify-between pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCurrentStep(1)}
                className="px-4 py-2 border border-slate-300 text-slate-600 rounded-lg text-xs font-semibold hover:bg-slate-50"
              >
                ← Back
              </button>
              <button
                type="button"
                onClick={() => setCurrentStep(3)}
                className="px-5 py-2.5 bg-aicte-600 hover:bg-aicte-700 text-white rounded-lg text-xs font-bold shadow transition flex items-center gap-1.5"
              >
                Proceed to Infrastructure & Faculty →
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: INFRASTRUCTURE & FACULTY */}
        {currentStep === 3 && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-6">
            <div className="border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-900">
                3. Physical Infrastructure & Teaching Faculty Declaration
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                AICTE Approval Process Handbook (APH) dimensional checks & statutory cadre ratios
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Total Contiguous Land Area (Acres)</label>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  value={totalLandAcres}
                  onChange={(e) => setTotalLandAcres(Number(e.target.value))}
                  className="w-full border border-slate-300 rounded-lg p-2.5 font-mono font-bold"
                  required
                />
                <span className="text-[10px] text-slate-400 mt-0.5 block">Rural: Min 7.5 acres | Urban: Min 5.0 acres</span>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Land Category</label>
                <select
                  value={landCategory}
                  onChange={(e) => setLandCategory(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2.5 bg-slate-50"
                >
                  <option value="Rural / Other Areas (Min 7.5 Acres)">Rural / Other Areas (Min 7.5 Acres)</option>
                  <option value="Urban / District Headquarter (Min 5.0 Acres)">Urban / District HQ (Min 5.0 Acres)</option>
                  <option value="Mega / Metro Cities (Min 2.5 Acres)">Mega / Metro Cities (Min 2.5 Acres)</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Instructional Built-up Area (sq.m)</label>
                <input
                  type="number"
                  step="100"
                  value={builtUpAreaSqm}
                  onChange={(e) => setBuiltUpAreaSqm(Number(e.target.value))}
                  className="w-full border border-slate-300 rounded-lg p-2.5 font-mono font-bold"
                  required
                />
                <span className="text-[10px] text-emerald-600 mt-0.5 block">
                  Capacity Ceiling: {Math.floor(builtUpAreaSqm / 8.5)} seats @ 8.5 m²/student
                </span>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Number of Classrooms</label>
                <input
                  type="number"
                  value={classroomsCount}
                  onChange={(e) => setClassroomsCount(Number(e.target.value))}
                  className="w-full border border-slate-300 rounded-lg p-2.5 font-mono"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">CAD & Computing Workstations</label>
                <input
                  type="number"
                  value={cadWorkstations}
                  onChange={(e) => setCadWorkstations(Number(e.target.value))}
                  className="w-full border border-slate-300 rounded-lg p-2.5 font-mono font-bold"
                  required
                />
                <span className="text-[10px] text-slate-400 mt-0.5 block">Mandatory 1:4 terminal ratio</span>
              </div>

              <div className="bg-amber-50/60 p-3 rounded-xl border border-amber-200">
                <label className="block font-bold text-amber-950 mb-1">Full-Time Teaching Faculty Count</label>
                <input
                  type="number"
                  value={facultyCount}
                  onChange={(e) => setFacultyCount(Number(e.target.value))}
                  className="w-full border border-amber-300 rounded-lg p-2.5 font-mono font-black text-amber-800 text-sm"
                  required
                />
                <span className="text-[10px] text-amber-700 mt-0.5 block">
                  Teacher-Student Norm Ceiling: {facultyCount * 20} students max (Requires {Math.ceil(requestedIntake / 20)} staff for {requestedIntake} intake) [Reference - verify against Approval Process Handbook] (illustrative)
                </span>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Library Unique Book Titles</label>
                <input
                  type="number"
                  value={libraryTitles}
                  onChange={(e) => setLibraryTitles(Number(e.target.value))}
                  className="w-full border border-slate-300 rounded-lg p-2.5 font-mono"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Library Total Book Volumes</label>
                <input
                  type="number"
                  value={libraryVolumes}
                  onChange={(e) => setLibraryVolumes(Number(e.target.value))}
                  className="w-full border border-slate-300 rounded-lg p-2.5 font-mono"
                />
              </div>
            </div>

            <div className="flex justify-between pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCurrentStep(2)}
                className="px-4 py-2 border border-slate-300 text-slate-600 rounded-lg text-xs font-semibold hover:bg-slate-50"
              >
                ← Back
              </button>
              <button
                type="button"
                onClick={() => setCurrentStep(4)}
                className="px-5 py-2.5 bg-aicte-600 hover:bg-aicte-700 text-white rounded-lg text-xs font-bold shadow transition flex items-center gap-1.5"
              >
                Proceed to Document Uploads Checklist →
              </button>
            </div>
          </div>
        )}

        {/* STEP 4: DOCUMENT UPLOADS */}
        {currentStep === 4 && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-6">
            <div className="border-b border-slate-100 pb-3 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-bold text-slate-900">
                  4. Statutory Document Uploads — Regulatory Checklist
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Official statutory files required for self-disclosure verification, OCR parsing, and forensic tamper analysis.
                </p>
              </div>
              <span className="text-xs px-2.5 py-1 bg-indigo-50 text-indigo-700 font-bold rounded-lg border border-indigo-200">
                Document Checklist
              </span>
            </div>

            <div className="space-y-4">
              {documentsList.map((doc, idx) => (
                <div
                  key={doc.id}
                  className={`p-4 rounded-xl border transition ${
                    doc.uploaded
                      ? 'border-emerald-300 bg-emerald-50/20'
                      : doc.mandatory
                      ? 'border-slate-200 bg-slate-50/40'
                      : 'border-slate-200 bg-white'
                  }`}
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="space-y-1 max-w-xl">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-black text-slate-900">{idx + 1}. {doc.label}</span>
                        {doc.mandatory ? (
                          <span className="text-[10px] font-bold bg-rose-100 text-rose-800 px-2 py-0.2 rounded uppercase">
                            Mandatory
                          </span>
                        ) : (
                          <span className="text-[10px] font-medium bg-slate-100 text-slate-600 px-2 py-0.2 rounded">
                            Optional / Where Applicable
                          </span>
                        )}
                        <span className="text-[10px] font-mono text-indigo-600 font-semibold">{doc.annexureRef}</span>
                      </div>
                      <p className="text-xs text-slate-500 leading-relaxed">{doc.description}</p>
                    </div>

                    <div className="flex items-center gap-2">
                      <label className="cursor-pointer px-3.5 py-1.5 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-bold rounded-lg shadow-sm transition flex items-center gap-1.5">
                        <span>📎</span>
                        <span>{doc.uploaded ? 'Change File' : 'Upload PDF'}</span>
                        <input
                          type="file"
                          accept=".pdf,.png,.jpg,.jpeg"
                          onChange={(e) => handleFileChange(doc.id, e.target.files?.[0] || null)}
                          className="hidden"
                        />
                      </label>
                      {doc.uploaded && (
                        <span className="text-xs text-emerald-700 font-bold flex items-center gap-1 bg-emerald-100 px-2 py-1 rounded">
                          ✓ Attached: {doc.file?.name}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-between pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCurrentStep(3)}
                className="px-4 py-2 border border-slate-300 text-slate-600 rounded-lg text-xs font-semibold hover:bg-slate-50"
              >
                ← Back
              </button>
              <button
                type="button"
                onClick={() => setCurrentStep(5)}
                className="px-5 py-2.5 bg-aicte-600 hover:bg-aicte-700 text-white rounded-lg text-xs font-bold shadow transition flex items-center gap-1.5"
              >
                Proceed to Review & Final Submission →
              </button>
            </div>
          </div>
        )}

        {/* STEP 5: REVIEW & UNDERTAKING */}
        {currentStep === 5 && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-6">
            <div className="border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-900">
                5. Comprehensive Review & Statutory Institutional Undertaking
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Final verification of declared parameters before ingestion into AICTE Scrutiny Engine
              </p>
            </div>

            {/* Summary Review Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
                  Institution & Programme Summary
                </span>
                <p><strong>PID:</strong> {aictePermanentId} • <strong>Type:</strong> {institutionType}</p>
                <p><strong>Institution:</strong> {institutionName}</p>
                <p><strong>Trust:</strong> {trustName} ({trustRegNo})</p>
                <p><strong>Affiliated University:</strong> {affiliatingUniversity}</p>
                <p><strong>Programme:</strong> {programme} ({courseName})</p>
                <p><strong>Intake Requested:</strong> <span className="font-mono font-bold text-aicte-600">{requestedIntake} seats</span> (Previous approved: {existingApprovedIntake})</p>
              </div>

              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
                  Infrastructure & Faculty Disclosure
                </span>
                <p><strong>Land Area:</strong> {totalLandAcres} Acres ({landCategory})</p>
                <p><strong>Instructional Area:</strong> {builtUpAreaSqm} sq.m ({classroomsCount} classrooms)</p>
                <p><strong>CAD Terminals:</strong> {cadWorkstations} Workstations</p>
                <p><strong>Teaching Faculty:</strong> {facultyCount} Faculty Members</p>
                <p><strong>Library Volumes:</strong> {libraryVolumes.toLocaleString()} Volumes ({libraryTitles.toLocaleString()} titles)</p>
                <p><strong>Attached Artifacts:</strong> {documentsList.filter((d) => d.uploaded).length} files attached</p>
              </div>
            </div>

            {/* Statutory Undertaking Box */}
            <div className="p-5 bg-indigo-50/70 border border-indigo-200 rounded-xl space-y-3">
              <label className="flex items-start gap-3 cursor-pointer text-xs text-slate-800 leading-relaxed">
                <input
                  type="checkbox"
                  checked={statutoryDeclaration}
                  onChange={(e) => setStatutoryDeclaration(e.target.checked)}
                  className="mt-1 rounded text-aicte-600 focus:ring-0"
                />
                <span>
                  <strong>Formal Statutory Undertaking (AICTE APH 2024–27):</strong> I hereby solemnly certify and declare that the information furnished in this online regulatory application and the attached documents are true and complete. I confirm that our institution satisfies all norms relating to land ownership, instructional built-up space, faculty-to-student cadre ratios [Reference - verify against Approval Process Handbook] (illustrative), fire safety clearances, and laboratory facilities under the AICTE Approval Process Handbook. I acknowledge that any falsification or document alteration identified during multi-lingual OCR or digital forensic scrutiny will attract immediate punitive rejection and withdrawal of approval.
                </span>
              </label>
            </div>

            <div className="flex justify-between pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCurrentStep(4)}
                className="px-4 py-2 border border-slate-300 text-slate-600 rounded-lg text-xs font-semibold hover:bg-slate-50"
              >
                ← Back to Uploads
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-6 py-2.5 bg-aicte-600 hover:bg-aicte-700 text-white rounded-lg text-xs font-bold shadow-md transition disabled:opacity-50 flex items-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Ingesting Application into AICTE Scrutiny Pipeline...</span>
                  </>
                ) : (
                  'Submit Regulatory Dossier to AICTE →'
                )}
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default NewApplicationPage;
