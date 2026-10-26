import React, { useState } from 'react';
import { Application } from '../types';
import { applicationsApi } from '../api/applications';

interface NewApplicationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: (newApp: Application) => void;
  institutionName?: string;
  institutionId?: string | number;
}

export const NewApplicationModal: React.FC<NewApplicationModalProps> = ({
  isOpen,
  onClose,
  onCreated,
  institutionName = 'My Technical Institution',
  institutionId,
}) => {
  const [academicYear, setAcademicYear] = useState('2026-2027');
  const [category, setCategory] = useState('extension_of_approval');
  const [appliedIntake, setAppliedIntake] = useState(480);
  const [currentIntake, setCurrentIntake] = useState(420);
  const [declaration, setDeclaration] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!declaration) {
      setErrorMsg('You must certify the statutory declaration before submitting.');
      return;
    }
    setErrorMsg('');
    setIsSubmitting(true);

    try {
      const payload: any = {
        institution_id: institutionId ? Number(institutionId) : undefined,
        institution_name: institutionName,
        academic_year: academicYear,
        category,
        intake_applied: appliedIntake,
        current_intake: currentIntake,
        applied_intake: appliedIntake,
        approved_intake: currentIntake,
      };

      const created = await applicationsApi.createApplication(payload);
      onCreated(created);
      onClose();
    } catch (err: any) {
      console.error('Failed to submit application', err);
      setErrorMsg(err?.response?.data?.detail || 'Failed to submit application. Please retry.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="bg-gradient-to-r from-aicte-700 to-indigo-800 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-[10px] font-mono tracking-widest uppercase bg-white/20 px-2 py-0.5 rounded text-white font-bold">
                AICTE Regulatory Portal
              </span>
              <h3 className="text-lg font-black mt-1">Submit New EoA Regulatory Application</h3>
              <p className="text-xs text-white/80 mt-0.5">
                {institutionName}
              </p>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="text-white/70 hover:text-white text-xl font-bold p-1 leading-none"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {errorMsg && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-xs font-semibold">
              ⚠️ {errorMsg}
            </div>
          )}

          {/* Academic Year & Category */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Target Academic Year
              </label>
              <select
                value={academicYear}
                onChange={(e) => setAcademicYear(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-slate-50 outline-none focus:border-aicte-500 font-semibold"
              >
                <option value="2026-2027">AY 2026-2027 (Next Cycle)</option>
                <option value="2025-2026">AY 2025-2026 (Current Cycle)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Application Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 bg-slate-50 outline-none focus:border-aicte-500 font-semibold"
              >
                <option value="extension_of_approval">Extension of Approval (EoA)</option>
                <option value="increase_of_intake">Increase in Intake</option>
                <option value="new_course">Addition of New Course / Division</option>
                <option value="nri_quota">Supernumerary Seats (FN/PIO/NRI)</option>
              </select>
            </div>
          </div>

          {/* Intakes */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Requested Applied Intake (Seats)
              </label>
              <input
                type="number"
                min="60"
                step="30"
                value={appliedIntake}
                onChange={(e) => setAppliedIntake(Number(e.target.value))}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 font-mono font-bold text-slate-800 outline-none focus:border-aicte-500"
                required
              />
              <span className="text-[10px] text-slate-400">Under 1:20 teacher-student norm</span>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Current Approved Intake (Seats)
              </label>
              <input
                type="number"
                min="0"
                step="30"
                value={currentIntake}
                onChange={(e) => setCurrentIntake(Number(e.target.value))}
                className="w-full text-xs border border-slate-300 rounded-lg p-2.5 font-mono font-bold text-slate-800 outline-none focus:border-aicte-500"
                required
              />
              <span className="text-[10px] text-slate-400">Previous approved sanction</span>
            </div>
          </div>

          {/* Declaration */}
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
            <label className="flex items-start gap-2.5 cursor-pointer text-xs text-slate-700 leading-snug">
              <input
                type="checkbox"
                checked={declaration}
                onChange={(e) => setDeclaration(e.target.checked)}
                className="mt-0.5 rounded text-aicte-600 focus:ring-0"
              />
              <span>
                <strong>Statutory Undertaking:</strong> I declare that all institutional land, faculty qualifications, built-up areas, and safety clearances submitted in this dossier conform to the AICTE Approval Process Handbook (APH) norms.
              </span>
            </label>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-300 text-slate-600 rounded-lg text-xs font-semibold hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 bg-aicte-600 hover:bg-aicte-700 text-white rounded-lg text-xs font-bold shadow transition disabled:opacity-50 flex items-center gap-1.5"
            >
              {isSubmitting ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Submitting to Scrutiny Pipeline...</span>
                </>
              ) : (
                'Submit Application & Upload Documents →'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
