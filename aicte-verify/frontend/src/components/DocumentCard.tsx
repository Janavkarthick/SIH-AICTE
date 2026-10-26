import React, { useState } from 'react';
import { Document } from '../types';
import StatusBadge from './StatusBadge';

interface DocumentCardProps {
  document: Document;
  onView?: (doc: Document) => void;
  onProcess?: (docId: string) => void;
  canProcess?: boolean;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({
  document,
  onView,
  onProcess,
  canProcess = false,
}) => {
  const [showFields, setShowFields] = useState(false);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  };

  const getDocTypeLabel = (type: string) => {
    return type
      .split('_')
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ');
  };

  const isForensicFlagged =
    document.forensic_report && document.forensic_report.tampering_score > 50;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition">
      <div className="flex items-start justify-between gap-3">
        {/* Document Icon & Title */}
        <div className="flex items-start gap-3">
          <div
            className={`p-3 rounded-lg flex-shrink-0 ${
              isForensicFlagged
                ? 'bg-rose-100 text-rose-700'
                : 'bg-indigo-50 text-indigo-700'
            }`}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>

          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="text-sm font-bold text-slate-900 break-all">{document.filename}</h4>
              <StatusBadge status={document.status} type="document" />
              <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                v{document.version}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Type: <strong className="text-slate-700">{getDocTypeLabel(document.document_type)}</strong> •{' '}
              {formatFileSize(document.file_size)} • {document.page_count} Pages
            </p>
          </div>
        </div>

        {/* Action button */}
        <div className="flex items-center gap-1.5 flex-shrink-0">
          {onView && (
            <button
              type="button"
              onClick={() => onView(document)}
              className="px-2.5 py-1.5 text-xs font-semibold text-aicte-700 bg-aicte-50 hover:bg-aicte-100 rounded-lg border border-aicte-200"
            >
              Examine
            </button>
          )}
          {canProcess && document.status === 'processing' && onProcess && (
            <button
              type="button"
              onClick={() => onProcess(document.id)}
              className="px-2.5 py-1.5 text-xs font-semibold text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg border border-purple-200"
            >
              Re-scan
            </button>
          )}
        </div>
      </div>

      {/* Forensic Quick Stats */}
      {document.forensic_report && (
        <div className="mt-3.5 p-3 rounded-lg bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-2">
            <span className="text-slate-500">Tampering Risk:</span>
            <span
              className={`font-bold px-1.5 py-0.5 rounded ${
                document.forensic_report.tampering_score > 70
                  ? 'bg-rose-100 text-rose-800'
                  : document.forensic_report.tampering_score > 30
                  ? 'bg-amber-100 text-amber-800'
                  : 'bg-emerald-100 text-emerald-800'
              }`}
            >
              {document.forensic_report.tampering_score}/100
            </span>
          </div>

          <div className="flex items-center gap-3 text-slate-600">
            {document.forensic_report.cloned_regions_detected && (
              <span className="text-rose-600 font-semibold flex items-center gap-1">
                ⚠️ Clones Detected
              </span>
            )}
            {document.forensic_report.font_inconsistencies && (
              <span className="text-amber-700 font-semibold flex items-center gap-1">
                ⚠️ Font Anomaly
              </span>
            )}
            {document.forensic_report.pii_detected &&
              document.forensic_report.pii_detected.length > 0 && (
                <span className="text-indigo-600 font-medium">
                  🔒 {document.forensic_report.pii_detected.length} PII Masked
                </span>
              )}
          </div>
        </div>
      )}

      {/* Extracted Fields Toggle */}
      {document.extracted_fields && Object.keys(document.extracted_fields).length > 0 && (
        <div className="mt-3">
          <button
            type="button"
            onClick={() => setShowFields(!showFields)}
            className="text-xs font-semibold text-slate-500 hover:text-slate-800 flex items-center gap-1"
          >
            <span>{showFields ? '▼ Hide' : '▶ Show'} Extracted Fields ({Object.keys(document.extracted_fields).length})</span>
          </button>

          {showFields && (
            <div className="mt-2 grid grid-cols-2 gap-2 p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs">
              {Object.entries(document.extracted_fields).map(([k, v]) => (
                <div key={k} className="overflow-hidden">
                  <span className="text-slate-500 block truncate font-medium">
                    {k.replace(/_/g, ' ')}:
                  </span>
                  <span className="font-semibold text-slate-800 truncate block">
                    {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentCard;
