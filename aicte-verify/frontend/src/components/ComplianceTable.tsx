import React from 'react';
import { ComplianceResult, ComplianceStatus } from '../types';
import AdvisoryBadge from './AdvisoryBadge';

interface ComplianceTableProps {
  results: ComplianceResult[];
  className?: string;
}

export const ComplianceTable: React.FC<ComplianceTableProps> = ({ results, className = '' }) => {
  const getStatusBadge = (status: ComplianceStatus) => {
    switch (status) {
      case 'pass':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
            ✓ Pass
          </span>
        );
      case 'gap':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-300">
            ✕ Deficit Gap
          </span>
        );
      case 'needs_evidence':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300">
            ⏳ Needs Evidence
          </span>
        );
      case 'needs_inspection':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-300">
            🔍 Physical Inspection
          </span>
        );
    }
  };

  return (
    <div className={`overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}>
      <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-slate-800">
            APH 2025 Norms Compliance Matrix
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Evaluated against AICTE Approval Process Handbook dimensional standards
          </p>
        </div>
        <AdvisoryBadge />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-100/70 border-b border-slate-200 text-slate-700 font-semibold uppercase tracking-wider text-[11px]">
              <th className="py-3 px-4">APH Parameter</th>
              <th className="py-3 px-4">Rule Ref</th>
              <th className="py-3 px-4">Declared Value</th>
              <th className="py-3 px-4">Mandated Norm</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Remarks & Deficit Notes</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {results.map((item) => (
              <tr key={item.id} className="hover:bg-slate-50/80 transition">
                <td className="py-3.5 px-4 font-bold text-slate-900">
                  {item.item_name}
                  <span className="block text-[10px] text-slate-400 capitalize font-normal">
                    {item.category.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="py-3.5 px-4 font-mono text-slate-600">
                  {item.rule_reference}
                </td>
                <td className="py-3.5 px-4 font-mono font-semibold text-slate-800">
                  {item.declared_value} {item.unit}
                </td>
                <td className="py-3.5 px-4 font-mono font-semibold text-slate-800">
                  {item.required_value} {item.unit}
                </td>
                <td className="py-3.5 px-4 whitespace-nowrap">
                  {getStatusBadge(item.status)}
                </td>
                <td className="py-3.5 px-4 text-slate-600 max-w-xs">
                  {item.deficiency_description || '—'}
                  {item.intake_impact && (
                    <span className="block mt-1 text-[11px] font-semibold text-rose-700">
                      Potential Intake Reduction Impact: -{item.intake_impact} seats
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ComplianceTable;
