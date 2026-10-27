import React, { useEffect, useState } from 'react';
import { DeficiencyLetter } from '../types';
import { lettersApi } from '../api/letters';
import AdvisoryBadge from '../components/AdvisoryBadge';
import ConfirmModal from '../components/ConfirmModal';

export const LettersPage: React.FC = () => {
  const [letter, setLetter] = useState<DeficiencyLetter | null>(null);
  const [language, setLanguage] = useState<'en' | 'ta' | 'hi'>('en');
  const [isLoading, setIsLoading] = useState(true);
  const [isImproving, setIsImproving] = useState(false);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [isApproving, setIsApproving] = useState(false);

  const userJson = localStorage.getItem('aicte_user');
  let user: any = null;
  try {
    if (userJson && userJson !== 'undefined' && userJson !== 'null') {
      user = JSON.parse(userJson);
    }
  } catch {}
  const isCollege = user?.role === 'college_user';

  const fetchLetter = async (lang: 'en' | 'ta' | 'hi' = language) => {
    setIsLoading(true);
    try {
      const data = await lettersApi.generateLetter('5', lang);
      setLetter(data);
    } catch (err) {
      console.error('Failed to load letter', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLetter(language);
  }, [language]);

  const handleImproveWithGemini = async () => {
    if (!letter) return;
    setIsImproving(true);
    try {
      const updated = await lettersApi.improveWordingWithGemini(letter);
      setLetter(updated);
    } catch (err) {
      console.error('Gemini improvement failed', err);
    } finally {
      setIsImproving(false);
    }
  };

  const handleConfirmApproval = async (notes?: string) => {
    if (!letter) return;
    setIsApproving(true);
    try {
      const approved = await lettersApi.approveLetter(letter.id, 'Dr. Rajesh Kumar (Regional Officer)');
      setLetter(approved);
      setShowApproveModal(false);
    } catch (err) {
      console.error('Letter approval failed', err);
    } finally {
      setIsApproving(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (isLoading || !letter) {
    return (
      <div className="py-20 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aicte-600 border-t-transparent" />
        <p className="mt-2 text-xs text-slate-500 font-semibold">Generating Deficiency Notice Letter...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Controls (Hidden during print) */}
      <div className="no-print flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">
            {isCollege
              ? 'Official Statutory Deficiency Notice & Hearing'
              : 'Official Statutory Deficiency Notice Generator'}
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            {isCollege
              ? 'Formal notice issued by the AICTE Regional Scrutiny Committee regarding your institution\'s affiliation application'
              : 'Automated compilation of observed infractions into formal AICTE Approval Process Handbook (APH) notice'}
          </p>
        </div>
        <AdvisoryBadge size="md" />
      </div>

      {/* Control Actions Bar (Hidden during print) */}
      <div className="no-print bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        {/* Language Selection */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-700">Notice Language:</span>
          <div className="flex border border-slate-300 rounded-lg overflow-hidden text-xs">
            <button
              type="button"
              onClick={() => setLanguage('en')}
              className={`px-3 py-1.5 font-medium ${
                language === 'en' ? 'bg-aicte-600 text-white font-bold' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'
              }`}
            >
              English
            </button>
            <button
              type="button"
              onClick={() => setLanguage('ta')}
              className={`px-3 py-1.5 font-medium border-l border-slate-300 ${
                language === 'ta' ? 'bg-aicte-600 text-white font-bold' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'
              }`}
            >
              தமிழ் (Tamil)
            </button>
            <button
              type="button"
              onClick={() => setLanguage('hi')}
              className={`px-3 py-1.5 font-medium border-l border-slate-300 ${
                language === 'hi' ? 'bg-aicte-600 text-white font-bold' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'
              }`}
            >
              हिन्दी (Hindi)
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Officer/Admin AI Improvement */}
          {!isCollege && (
            <button
              type="button"
              onClick={handleImproveWithGemini}
              disabled={isImproving || letter.gemini_improved}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg border transition flex items-center gap-1.5 ${
                letter.gemini_improved
                  ? 'bg-purple-50 text-purple-700 border-purple-300'
                  : 'bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border-indigo-200'
              }`}
            >
              <span>✨</span>
              {isImproving
                ? 'Refining Wording with AI...'
                : letter.gemini_improved
                ? 'Wording AI Enhanced ✓'
                : 'Improve Statutory Wording (Gemini)'}
            </button>
          )}

          {/* Print button */}
          <button
            type="button"
            onClick={handlePrint}
            className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg border border-slate-300 transition flex items-center gap-1"
          >
            <span>🖨️</span> Print / Save PDF
          </button>

          {/* Officer Approval Button (Only for scrutiny officers/admin) */}
          {!isCollege && (
            letter.status !== 'approved' ? (
              <button
                type="button"
                onClick={() => setShowApproveModal(true)}
                className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm transition"
              >
                Approve Notice & Dispatch
              </button>
            ) : (
              <span className="px-3 py-1 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-lg border border-emerald-300 flex items-center gap-1">
                ✓ Approved by {letter.approved_by}
              </span>
            )
          )}
        </div>
      </div>

      {/* Official AICTE Deficiency Letter Preview Document */}
      <div className="bg-white rounded-2xl border border-slate-300 shadow-xl p-8 md:p-14 max-w-4xl mx-auto text-slate-900 font-serif leading-relaxed">
        {/* Official Header */}
        <div className="text-center border-b-2 border-slate-900 pb-6 mb-6">
          <div className="w-14 h-14 rounded-full border-2 border-slate-900 mx-auto flex items-center justify-center font-bold text-lg font-sans mb-2">
            AICTE
          </div>
          <h1 className="text-xl font-bold uppercase tracking-wide">
            All India Council for Technical Education
          </h1>
          <p className="text-xs font-sans text-slate-600">
            (A Statutory Body of the Government of India, Ministry of Education)
          </p>
          <p className="text-xs font-sans text-slate-500 mt-1">
            Nelson Mandela Marg, Vasant Kunj, New Delhi - 110070 | Regional Office: Southern Region, Chennai
          </p>
        </div>

        {/* Ref and Date line */}
        <div className="flex justify-between text-xs font-sans mb-6 border-b border-slate-200 pb-3">
          <div>
            <strong>F.No. AICTE/SRO/APH-2025/DEF-{(letter.application_number || (letter as any).reference_number || String((letter as any).application_id || '001')).split('/').pop()}</strong>
          </div>
          <div>
            <strong>Date:</strong> {letter.date || (letter as any).date_issued || new Date().toISOString().split('T')[0]}
          </div>
        </div>

        {/* Letter Subject */}
        <div className="mb-6 font-sans text-xs">
          <p className="font-bold uppercase tracking-wide text-slate-800">
            SUBJECT: {letter.subject}
          </p>
        </div>

        {/* Body Content */}
        <div className="text-xs whitespace-pre-line mb-8 leading-relaxed font-sans text-slate-800">
          {letter.body_content}
        </div>

        {/* Deficiency Table */}
        <div className="mb-8 font-sans">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
            Table of Specific Regulatory Deficiencies & Required Rectification:
          </h4>
          <table className="w-full text-left text-xs border border-slate-400 border-collapse">
            <thead>
              <tr className="bg-slate-100 border-b border-slate-400 text-slate-800 font-bold uppercase text-[10px]">
                <th className="p-2.5 border-r border-slate-400 w-12">S.No</th>
                <th className="p-2.5 border-r border-slate-400 w-32">Rule Ref</th>
                <th className="p-2.5 border-r border-slate-400">Observed Deficiency</th>
                <th className="p-2.5 border-r border-slate-400">Mandatory Rectification Action</th>
                <th className="p-2.5 text-center w-20">Timeline</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-300">
              {(letter.deficiency_items || (letter as any).items || []).map((item: any, idx: number) => (
                <tr key={idx}>
                  <td className="p-2.5 border-r border-slate-300 text-center font-bold">{idx + 1}</td>
                  <td className="p-2.5 border-r border-slate-300 font-mono text-[11px]">{item.rule_id || item.clause_reference || 'APH-2025'}</td>
                  <td className="p-2.5 border-r border-slate-300 font-medium text-rose-900 bg-rose-50/30">
                    {item.deficiency || item.deficiency_title || item.description}
                  </td>
                  <td className="p-2.5 border-r border-slate-300 text-slate-800">{item.action_required || item.remedial_action || 'Provide certified rectification proof'}</td>
                  <td className="p-2.5 text-center font-bold text-slate-900 whitespace-nowrap">
                    {item.deadline_days || 15} Days
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Sign-off */}
        <div className="mt-12 flex justify-between items-end font-sans text-xs">
          <div>
            <p className="text-[10px] text-slate-500 uppercase">
              Copy forwarded for information to:
            </p>
            <ol className="list-decimal pl-4 text-[10px] text-slate-600 mt-1 space-y-0.5">
              <li>The Commissioner of Technical Education, Govt. of Tamil Nadu</li>
              <li>The Registrar, Affiliating University</li>
              <li>Guard File (AICTE Approval Division)</li>
            </ol>
          </div>

          <div className="text-right">
            <div className="h-10 flex items-center justify-end">
              {letter.status === 'approved' ? (
                <span className="font-serif italic text-blue-900 font-bold text-base">
                  Dr. Rajesh Kumar
                </span>
              ) : (
                <span className="text-[11px] text-slate-400 italic">[Pending Officer Signature]</span>
              )}
            </div>
            <p className="font-bold text-slate-900 mt-1">Regional Officer & Member Secretary</p>
            <p className="text-[11px] text-slate-600">AICTE Southern Regional Office</p>
          </div>
        </div>
      </div>

      <ConfirmModal
        isOpen={showApproveModal}
        title="Approve & Issue Statutory Deficiency Letter"
        message={`Are you sure you want to officially issue this Deficiency Notice to ${letter.institution_name}? Once approved, a statutory 15-day compliance window will commence.`}
        confirmLabel="Approve & Digitally Sign"
        requiresNotes={true}
        notesPlaceholder="Official remarks accompanying issuance of deficiency notice..."
        isLoading={isApproving}
        onConfirm={handleConfirmApproval}
        onClose={() => setShowApproveModal(false)}
      />
    </div>
  );
};

export default LettersPage;
