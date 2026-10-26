import React, { useState } from 'react';
import { Flag, Document } from '../types';
import AdvisoryBadge from './AdvisoryBadge';

interface EvidenceViewerProps {
  flag: Flag;
  document?: Document;
  onClose: () => void;
}

export const EvidenceViewer: React.FC<EvidenceViewerProps> = ({ flag, document, onClose }) => {
  const [activeLayer, setActiveLayer] = useState<'original' | 'ela' | 'annotations'>(
    flag.evidence_link?.overlay_type || 'original'
  );
  const [zoomLevel, setZoomLevel] = useState(100);

  const pageNumber = flag.evidence_link?.page || 1;
  const boundingBoxes = flag.evidence_link?.bounding_boxes || [
    { x: 180, y: 320, width: 220, height: 48, label: 'Flagged Region', confidence: flag.confidence / 100 },
  ];

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center p-3 md:p-6 overflow-hidden">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl h-[90vh] flex flex-col border border-slate-300 overflow-hidden">
        {/* Top Header */}
        <div className="px-6 py-3.5 border-b border-slate-200 bg-slate-50 flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <span className="font-mono text-xs font-bold bg-indigo-100 text-indigo-800 px-2.5 py-1 rounded">
              {flag.code}
            </span>
            <h3 className="text-base font-bold text-slate-800">
              Evidence Viewer: {flag.title}
            </h3>
            <AdvisoryBadge size="md" />
          </div>

          <div className="flex items-center gap-4">
            {/* Zoom Controls */}
            <div className="flex items-center bg-white border border-slate-300 rounded-lg shadow-sm text-xs">
              <button
                type="button"
                onClick={() => setZoomLevel((z) => Math.max(50, z - 25))}
                className="px-2.5 py-1 hover:bg-slate-100 border-r border-slate-200 font-bold"
                title="Zoom Out"
              >
                -
              </button>
              <span className="px-2 font-mono">{zoomLevel}%</span>
              <button
                type="button"
                onClick={() => setZoomLevel((z) => Math.min(200, z + 25))}
                className="px-2.5 py-1 hover:bg-slate-100 border-l border-slate-200 font-bold"
                title="Zoom In"
              >
                +
              </button>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="text-slate-400 hover:text-slate-700 text-2xl font-bold leading-none p-1"
            >
              ×
            </button>
          </div>
        </div>

        {/* Advisory Notice Banner inside modal */}
        <div className="bg-amber-50 border-b border-amber-200 px-6 py-2 flex items-center justify-between text-xs text-amber-900">
          <div className="flex items-center gap-2">
            <span>⚠️</span>
            <span>
              <strong>Decision-support only:</strong> Algorithmic overlays and Error Level Analysis
              (ELA) are advisory. Final forensic determination rests with authorised AICTE officials.
            </span>
          </div>
          <span className="font-semibold text-slate-600">
            Document Page: <strong className="text-slate-900">{pageNumber}</strong>
          </span>
        </div>

        {/* Main Content: Split Viewer & Side Panel */}
        <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
          {/* Document Display Canvas */}
          <div className="flex-1 bg-slate-900/90 relative flex flex-col overflow-auto items-center justify-center p-6 select-none">
            {/* View Mode Switcher */}
            <div className="absolute top-4 left-6 z-20 flex bg-white/90 backdrop-blur rounded-lg p-1 shadow border border-slate-300 text-xs font-semibold">
              <button
                type="button"
                onClick={() => setActiveLayer('original')}
                className={`px-3 py-1.5 rounded-md transition ${
                  activeLayer === 'original'
                    ? 'bg-aicte-600 text-white shadow'
                    : 'text-slate-700 hover:text-slate-900'
                }`}
              >
                Original Page
              </button>
              <button
                type="button"
                onClick={() => setActiveLayer('ela')}
                className={`px-3 py-1.5 rounded-md transition ${
                  activeLayer === 'ela'
                    ? 'bg-rose-600 text-white shadow'
                    : 'text-slate-700 hover:text-slate-900'
                }`}
              >
                ELA Heatmap
              </button>
              <button
                type="button"
                onClick={() => setActiveLayer('annotations')}
                className={`px-3 py-1.5 rounded-md transition ${
                  activeLayer === 'annotations'
                    ? 'bg-amber-600 text-white shadow'
                    : 'text-slate-700 hover:text-slate-900'
                }`}
              >
                Bounding Boxes
              </button>
            </div>

            {/* Document Surface Container */}
            <div
              className="relative shadow-2xl bg-white border border-slate-300 rounded overflow-hidden transition-all duration-150"
              style={{
                width: `${600 * (zoomLevel / 100)}px`,
                height: `${800 * (zoomLevel / 100)}px`,
              }}
            >
              {/* Layer 1: Simulated High-Res Document Scan */}
              <div className="absolute inset-0 p-8 flex flex-col justify-between text-slate-800 bg-[#fdfdfc] font-serif select-none pointer-events-none">
                <div>
                  <div className="text-center border-b-2 border-slate-900 pb-4">
                    <p className="text-[10px] uppercase tracking-widest text-slate-500 font-sans">
                      Government of Tamil Nadu • Registration Department
                    </p>
                    <h2 className="text-lg font-bold uppercase mt-1">
                      Deed of Absolute Title Conveyance & Trust Endorsement
                    </h2>
                    <p className="text-xs italic mt-0.5">
                      Sub-Registrar Office, Pollachi • Document No. 8421/2018
                    </p>
                  </div>

                  <div className="mt-6 space-y-3 text-xs leading-relaxed font-mono">
                    <p>
                      THIS DEED OF CONVEYANCE made this twelfth day of June 2018 between the vendor and the
                      purchaser SRI KRISHNA EDUCATIONAL AND CHARITABLE TRUST for the dedicated purpose of
                      operating an institution of higher technical education.
                    </p>
                    <p>
                      SCHEDULE OF PROPERTY: District: Coimbatore, Taluk: Pollachi, Village: Achipatti.
                      Old Survey No. 412, Resurvey No. <span className="bg-amber-100 font-bold px-1">412/A-1</span>{' '}
                      comprising an extent of 7.50 Acres bounded on the North by S.F. No. 411 and South by Canal.
                    </p>
                    <p>
                      Encumbrance Nil. The vendor confirms uninterrupted contiguous possession and
                      DTCP educational conversion sanction.
                    </p>
                  </div>
                </div>

                <div className="border-t border-slate-400 pt-4 flex justify-between items-end text-xs font-sans">
                  <div>
                    <div className="w-24 h-12 border border-slate-400 rounded flex items-center justify-center text-[10px] text-slate-400">
                      [ Official Seal ]
                    </div>
                    <span className="text-[10px] text-slate-500 block mt-1">Registrar Stamp #88192</span>
                  </div>
                  <div className="text-right">
                    <span className="italic text-slate-600 block">Digitally Signed & Sealed</span>
                    <span className="font-bold">Sub-Registrar, Pollachi</span>
                  </div>
                </div>
              </div>

              {/* Layer 2: ELA Heatmap Layer */}
              {activeLayer === 'ela' && (
                <div className="absolute inset-0 bg-slate-950/80 mix-blend-multiply flex items-center justify-center pointer-events-none">
                  {/* Glowing localized artifact hotspot around survey number */}
                  <div
                    className="absolute rounded-lg animate-pulse"
                    style={{
                      left: '28%',
                      top: '42%',
                      width: '38%',
                      height: '8%',
                      background: 'radial-gradient(circle, rgba(244,63,94,0.85) 0%, rgba(234,88,12,0.6) 50%, transparent 80%)',
                      filter: 'blur(4px)',
                    }}
                  />
                  <div className="absolute bottom-4 left-4 bg-black/80 text-white text-[11px] font-mono px-3 py-1.5 rounded border border-rose-500">
                    ELA Heatmap: High frequency gradient detected in text baseline. Resave quantization mismatch: +42.8%
                  </div>
                </div>
              )}

              {/* Layer 3: Interactive SVG Bounding Boxes Overlay */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 600 800">
                {boundingBoxes.map((box, idx) => {
                  const isVisible = activeLayer === 'annotations' || activeLayer === 'ela';
                  if (!isVisible) return null;

                  return (
                    <g key={idx}>
                      <rect
                        x={box.x}
                        y={box.y}
                        width={box.width}
                        height={box.height}
                        fill="rgba(239, 68, 68, 0.15)"
                        stroke="#ef4444"
                        strokeWidth="2.5"
                        strokeDasharray="4 2"
                      />
                      <rect
                        x={box.x}
                        y={box.y - 24}
                        width={Math.min(box.width + 40, 260)}
                        height={22}
                        fill="#ef4444"
                        rx="4"
                      />
                      <text
                        x={box.x + 6}
                        y={box.y - 8}
                        fill="#ffffff"
                        fontSize="11"
                        fontFamily="sans-serif"
                        fontWeight="bold"
                      >
                        {box.label || 'Flagged Discrepancy'} ({(flag.confidence).toFixed(0)}%)
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>

          {/* Side Panel: Flag Details & Rule Info */}
          <div className="w-full md:w-80 lg:w-96 bg-white border-l border-slate-200 p-6 flex flex-col justify-between overflow-y-auto">
            <div className="space-y-4">
              <div>
                <span className="text-[10px] font-bold tracking-wider uppercase text-slate-400 block mb-1">
                  Regulatory Rule & Identification
                </span>
                <p className="font-mono text-xs font-bold text-slate-800 bg-slate-100 p-2 rounded border border-slate-200">
                  {flag.rule_id}
                </p>
              </div>

              <div>
                <span className="text-[10px] font-bold tracking-wider uppercase text-slate-400 block mb-1">
                  Confidence Score
                </span>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-slate-100 rounded-full h-2.5 overflow-hidden">
                    <div
                      className="bg-aicte-600 h-full rounded-full transition-all"
                      style={{ width: `${flag.confidence}%` }}
                    />
                  </div>
                  <span className="font-mono font-bold text-sm text-slate-800">
                    {flag.confidence}%
                  </span>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold tracking-wider uppercase text-slate-400 block mb-1">
                  Forensic Finding
                </span>
                <p className="text-xs text-slate-700 leading-relaxed bg-rose-50 border border-rose-200 p-3 rounded-lg">
                  {flag.reason}
                </p>
              </div>

              <div>
                <span className="text-[10px] font-bold tracking-wider uppercase text-slate-400 block mb-1">
                  Document Provenance
                </span>
                <div className="text-xs text-slate-600 space-y-1">
                  <p>
                    <strong>File:</strong> {flag.evidence_link?.document_name || document?.filename || 'Document'}
                  </p>
                  <p>
                    <strong>Page Number:</strong> {pageNumber}
                  </p>
                  <p>
                    <strong>Status:</strong>{' '}
                    <span className="capitalize font-semibold text-rose-700">{flag.status}</span>
                  </p>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200">
              <button
                type="button"
                onClick={onClose}
                className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-lg transition"
              >
                Close Viewer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvidenceViewer;
