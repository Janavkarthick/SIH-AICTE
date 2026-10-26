import React, { useState } from 'react';
import { Flag, FlagSeverity } from '../types';
import AdvisoryBadge from './AdvisoryBadge';
import ConfirmModal from './ConfirmModal';

interface FlagCardProps {
  flag: Flag;
  onViewEvidence?: (flag: Flag) => void;
  onResolve?: (flagId: string, notes: string) => Promise<void>;
  userRole?: string;
}

export const FlagCard: React.FC<FlagCardProps> = ({
  flag,
  onViewEvidence,
  onResolve,
  userRole = 'officer',
}) => {
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [isResolving, setIsResolving] = useState(false);

  const severityBorderColors: Record<FlagSeverity, string> = {
    info: 'border-l-4 border-l-blue-500 bg-blue-50/30',
    low: 'border-l-4 border-l-emerald-500 bg-emerald-50/30',
    medium: 'border-l-4 border-l-yellow-500 bg-yellow-50/30',
    high: 'border-l-4 border-l-orange-500 bg-orange-50/30',
    critical: 'border-l-4 border-l-rose-600 bg-rose-50/40',
  };

  const severityBadgeColors: Record<FlagSeverity, string> = {
    info: 'bg-blue-100 text-blue-800 border-blue-200',
    low: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    critical: 'bg-rose-100 text-rose-800 border-rose-300 font-bold animate-pulse',
  };

  const canResolve =
    (userRole === 'officer' || userRole === 'scrutiny_admin' || userRole === 'admin') &&
    flag.status === 'open';

  const handleConfirmResolve = async (notes?: string) => {
    if (!onResolve) return;
    setIsResolving(true);
    try {
      await onResolve(flag.id, notes || 'Resolved upon scrutiny verification');
      setShowResolveModal(false);
    } catch {
      // error handled in caller
    } finally {
      setIsResolving(false);
    }
  };

  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md ${
        severityBorderColors[flag.severity]
      }`}
    >
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className={`px-2 py-0.5 rounded text-xs uppercase font-semibold border ${
              severityBadgeColors[flag.severity]
            }`}
          >
            {flag.severity}
          </span>
          <span className="font-mono text-xs font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
            {flag.code}
          </span>
          <AdvisoryBadge />
          {flag.is_simulated && (
            <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded border border-purple-300">
              SIMULATED
            </span>
          )}
          {flag.status === 'resolved' && (
            <span className="text-xs font-medium text-emerald-700 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded-full flex items-center gap-1">
              ✓ Resolved
            </span>
          )}
        </div>

        {/* Confidence & Rule info */}
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-700">
            Rule: {flag.rule_id}
          </span>
          <span className="font-semibold text-slate-700 bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-200">
            Confidence: {flag.confidence}%
          </span>
        </div>
      </div>

      {/* Main Body */}
      <div className="mt-3">
        <h4 className="text-base font-bold text-slate-900">{flag.title}</h4>
        <p className="mt-1 text-sm text-slate-700 leading-relaxed">{flag.reason}</p>

        {flag.resolution_notes && (
          <div className="mt-3 p-2.5 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-900">
            <span className="font-bold">Resolution Notes ({flag.resolved_by}):</span>{' '}
            {flag.resolution_notes}
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
        <span className="text-xs text-slate-400">
          Raised: {new Date(flag.created_at).toLocaleString()}
        </span>

        <div className="flex items-center gap-2">
          {flag.evidence_link && onViewEvidence && (
            <button
              type="button"
              onClick={() => onViewEvidence(flag)}
              className="px-3 py-1.5 text-xs font-semibold text-aicte-700 bg-aicte-50 hover:bg-aicte-100 border border-aicte-200 rounded-lg flex items-center gap-1.5 transition"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
              View Evidence
            </button>
          )}

          {canResolve && (
            <button
              type="button"
              onClick={() => setShowResolveModal(true)}
              className="px-3 py-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg flex items-center gap-1 transition"
            >
              Resolve Flag
            </button>
          )}
        </div>
      </div>

      <ConfirmModal
        isOpen={showResolveModal}
        title="Resolve Regulatory Flag"
        message={`Are you sure you want to resolve flag "${flag.code}: ${flag.title}"? Please state whether clarification was provided or error was corrected.`}
        confirmLabel="Confirm Resolution"
        confirmVariant="primary"
        requiresNotes={true}
        notesPlaceholder="Provide reasons for resolving this flag (e.g., Original deed inspected and verified)..."
        isLoading={isResolving}
        onConfirm={handleConfirmResolve}
        onClose={() => setShowResolveModal(false)}
      />
    </div>
  );
};

export default FlagCard;
