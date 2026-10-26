import React from 'react';
import { ResubmissionDiff as ResubmissionDiffType } from '../types';
import AdvisoryBadge from './AdvisoryBadge';

interface ResubmissionDiffProps {
  diff: ResubmissionDiffType;
  className?: string;
}

export const ResubmissionDiff: React.FC<ResubmissionDiffProps> = ({ diff, className = '' }) => {
  return (
    <div className={`rounded-xl border border-slate-200 bg-white p-6 shadow-sm ${className}`}>
      <div className="flex items-center justify-between border-b border-slate-200 pb-4 mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-800">
            Resubmission Delta: Version {diff.previous_version} → Version {diff.current_version}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Automated change detection tracking newly uploaded, removed, and modified materials
          </p>
        </div>
        <AdvisoryBadge />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Added documents */}
        <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-200">
          <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-800 uppercase tracking-wide mb-2">
            <span>+</span> Added Documents ({diff.added_documents.length})
          </div>
          {diff.added_documents.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No new files added</p>
          ) : (
            <ul className="space-y-1 text-xs text-emerald-950 font-medium">
              {diff.added_documents.map((doc, i) => (
                <li key={i} className="flex items-center gap-1">
                  <span>📄</span> {doc}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Removed documents */}
        <div className="p-4 rounded-lg bg-rose-50 border border-rose-200">
          <div className="flex items-center gap-1.5 text-xs font-bold text-rose-800 uppercase tracking-wide mb-2">
            <span>−</span> Removed / Superseded ({diff.removed_documents.length})
          </div>
          {diff.removed_documents.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No files removed</p>
          ) : (
            <ul className="space-y-1 text-xs text-rose-950 font-medium">
              {diff.removed_documents.map((doc, i) => (
                <li key={i} className="flex items-center gap-1 line-through opacity-75">
                  <span>🗑️</span> {doc}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Modified documents */}
        <div className="p-4 rounded-lg bg-amber-50 border border-amber-200">
          <div className="flex items-center gap-1.5 text-xs font-bold text-amber-800 uppercase tracking-wide mb-2">
            <span>~</span> Modified / Re-scanned ({diff.modified_documents.length})
          </div>
          {diff.modified_documents.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No files modified</p>
          ) : (
            <ul className="space-y-1 text-xs text-amber-950 font-medium">
              {diff.modified_documents.map((doc, i) => (
                <li key={i} className="flex items-center gap-1">
                  <span>🔄</span> {doc}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Changed fields comparison table */}
      <div>
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
          Extracted Field Revisions
        </h4>
        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-100 text-slate-700 font-semibold uppercase text-[11px]">
                <th className="py-2.5 px-4">Field Attribute</th>
                <th className="py-2.5 px-4">Previous Value (v{diff.previous_version})</th>
                <th className="py-2.5 px-4">Revised Value (v{diff.current_version})</th>
                <th className="py-2.5 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {diff.changed_fields.map((f, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="py-2.5 px-4 font-sans font-semibold text-slate-800">{f.field}</td>
                  <td className="py-2.5 px-4 text-rose-600 bg-rose-50/50">{String(f.old_value)}</td>
                  <td className="py-2.5 px-4 text-emerald-600 bg-emerald-50/50 font-bold">{String(f.new_value)}</td>
                  <td className="py-2.5 px-4">
                    <span className="text-[10px] font-sans font-semibold uppercase px-2 py-0.5 rounded bg-yellow-100 text-yellow-800 border border-yellow-300">
                      Modified
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ResubmissionDiff;
