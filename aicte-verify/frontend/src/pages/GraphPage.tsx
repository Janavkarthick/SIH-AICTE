import React, { useEffect, useRef, useState } from 'react';
import cytoscape, { Core } from 'cytoscape';
import { GraphData, GraphEntity, GraphRelation, GraphNodeType } from '../types';
import { graphApi } from '../api/graph';
import AdvisoryBadge from '../components/AdvisoryBadge';

export const GraphPage: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<GraphEntity | null>(null);
  const [selectedRelation, setSelectedRelation] = useState<GraphRelation | null>(null);

  const [filterType, setFilterType] = useState<string>('all');
  const [flaggedOnly, setFlaggedOnly] = useState<boolean>(false);
  const [canvasTheme, setCanvasTheme] = useState<'light' | 'dark'>('light');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchGraph = async () => {
      setIsLoading(true);
      try {
        const data = await graphApi.getGraphData();
        setGraphData(data);
      } catch (err) {
        console.error('Failed to load graph data', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchGraph();
  }, []);

  useEffect(() => {
    if (!containerRef.current || !graphData) return;

    // Filter nodes & edges
    let visibleNodes = graphData.nodes || [];
    if (filterType !== 'all') {
      visibleNodes = visibleNodes.filter((n) => n.type === filterType);
    }
    if (flaggedOnly) {
      visibleNodes = visibleNodes.filter((n) => n.flagged);
    }

    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));
    let visibleEdges = (graphData.edges || []).filter(
      (e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target)
    );
    if (flaggedOnly) {
      visibleEdges = visibleEdges.filter((e) => e.flagged);
    }

    const elements: cytoscape.ElementDefinition[] = [
      ...visibleNodes.map((n) => ({
        data: {
          id: n.id,
          label: n.label,
          type: n.type,
          flagged: n.flagged,
          raw: n,
        },
      })),
      ...visibleEdges.map((e) => ({
        data: {
          id: e.id,
          source: e.source,
          target: e.target,
          label: e.label,
          flagged: e.flagged,
          raw: e,
        },
      })),
    ];

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const isLight = canvasTheme === 'light';

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      layout: {
        name: 'cose',
        animate: false,
        padding: 50,
        componentSpacing: 120,
        nodeOverlap: 25,
      },
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(label)',
            'font-size': '11px',
            'font-weight': 'bold',
            'font-family': 'Inter, system-ui, sans-serif',
            'text-valign': 'bottom',
            'text-margin-y': 7,
            'background-color': '#475569',
            color: isLight ? '#0f172a' : '#ffffff',
            'text-background-color': isLight ? '#ffffff' : '#0f172a',
            'text-background-opacity': 0.95,
            'text-background-padding': '3px',
            'text-background-shape': 'roundrectangle',
            'text-border-color': isLight ? '#94a3b8' : '#475569',
            'text-border-width': 1,
            'text-border-opacity': 0.9,
            'text-max-width': '140px',
            'text-wrap': 'wrap',
            width: 44,
            height: 44,
            'border-width': 3,
            'border-color': isLight ? '#ffffff' : '#1e293b',
          },
        },
        // Node Types with vibrant distinct colors
        {
          selector: 'node[type = "institution"]',
          style: { 'background-color': '#2563eb' }, // Royal Blue
        },
        {
          selector: 'node[type = "faculty"]',
          style: { 'background-color': '#10b981' }, // Vivid Emerald
        },
        {
          selector: 'node[type = "land"]',
          style: { 'background-color': '#d97706' }, // Amber Gold
        },
        {
          selector: 'node[type = "trust"]',
          style: { 'background-color': '#8b5cf6' }, // Vibrant Violet
        },
        {
          selector: 'node[type = "signatory"]',
          style: { 'background-color': '#ea580c' }, // Saffron Orange
        },
        {
          selector: 'node[type = "stamp"]',
          style: { 'background-color': '#64748b' }, // Steel Slate
        },
        // Flagged nodes
        {
          selector: 'node[?flagged]',
          style: {
            'border-color': '#dc2626',
            'border-width': 5,
            'border-opacity': 1,
            'background-color': '#ef4444',
            color: '#b91c1c',
            'text-background-color': isLight ? '#fef2f2' : '#450a0a',
            'text-border-color': '#f87171',
          },
        },
        // Edges
        {
          selector: 'edge',
          style: {
            width: 2.5,
            'line-color': isLight ? '#64748b' : '#94a3b8',
            'target-arrow-color': isLight ? '#64748b' : '#94a3b8',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            label: 'data(label)',
            'font-size': '9px',
            'font-weight': 'bold',
            'font-family': 'Inter, system-ui, sans-serif',
            'text-rotation': 'autorotate',
            'text-margin-y': -8,
            color: isLight ? '#0f172a' : '#f8fafc',
            'text-background-color': isLight ? '#ffffff' : '#0f172a',
            'text-background-opacity': 0.95,
            'text-background-padding': '2px',
            'text-background-shape': 'roundrectangle',
            'text-border-color': isLight ? '#cbd5e1' : '#475569',
            'text-border-width': 1,
          },
        },
        // Flagged edges
        {
          selector: 'edge[?flagged]',
          style: {
            width: 3.5,
            'line-color': '#dc2626',
            'target-arrow-color': '#dc2626',
            color: '#b91c1c',
            'font-weight': 'bold',
            'line-style': 'dashed',
            'text-background-color': isLight ? '#fef2f2' : '#450a0a',
            'text-border-color': '#f87171',
          },
        },
        // Selected highlight
        {
          selector: ':selected',
          style: {
            'border-color': '#f59e0b',
            'border-width': 5,
          },
        },
      ],
    });

    cy.on('tap', 'node', (evt) => {
      setSelectedRelation(null);
      setSelectedEntity(evt.target.data('raw'));
    });

    cy.on('tap', 'edge', (evt) => {
      setSelectedEntity(null);
      setSelectedRelation(evt.target.data('raw'));
    });

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedEntity(null);
        setSelectedRelation(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [graphData, filterType, flaggedOnly, canvasTheme]);

  const fitGraph = () => {
    cyRef.current?.fit();
    cyRef.current?.center();
  };

  const zoomIn = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 1.3);
      cyRef.current.center();
    }
  };

  const zoomOut = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 0.77);
      cyRef.current.center();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">
            Cross-Institutional Entity Relationship Graph
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Knowledge graph uncovering hidden multi-campus faculty duplication, shared trust assets, and reused stamps
          </p>
        </div>
        <AdvisoryBadge size="md" />
      </div>

      {/* Graph Filters & Legend Strip */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Entity Type Legend / Filter */}
        <div className="flex items-center gap-3 flex-wrap">
          <span className="font-bold text-slate-700">Filter Nodes:</span>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="border border-slate-300 rounded p-1.5 bg-slate-50 outline-none text-xs"
          >
            <option value="all">All Entity Types</option>
            <option value="institution">Institutions (Blue)</option>
            <option value="faculty">Faculty (Green)</option>
            <option value="land">Land Parcels (Brown)</option>
            <option value="trust">Operating Trusts (Purple)</option>
            <option value="signatory">Signatories & Notaries (Orange)</option>
            <option value="stamp">Treasury Stamps (Gray)</option>
          </select>

          <label className="flex items-center gap-1.5 cursor-pointer font-semibold text-rose-700">
            <input
              type="checkbox"
              checked={flaggedOnly}
              onChange={(e) => setFlaggedOnly(e.target.checked)}
              className="rounded text-rose-600 focus:ring-rose-500"
            />
            Show Flagged Infractions Only ⚠️
          </label>
        </div>

        <div className="flex items-center gap-2">
          {/* Canvas Mode Toggle */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-300">
            <button
              type="button"
              onClick={() => setCanvasTheme('light')}
              className={`px-2.5 py-1 text-xs font-semibold rounded ${
                canvasTheme === 'light'
                  ? 'bg-white text-aicte-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              ☀️ Light Canvas
            </button>
            <button
              type="button"
              onClick={() => setCanvasTheme('dark')}
              className={`px-2.5 py-1 text-xs font-semibold rounded ${
                canvasTheme === 'dark'
                  ? 'bg-slate-800 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              🌙 Dark Mode
            </button>
          </div>

          <button
            type="button"
            onClick={zoomIn}
            className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded text-xs transition"
            title="Zoom In"
          >
            ＋
          </button>
          <button
            type="button"
            onClick={zoomOut}
            className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded text-xs transition"
            title="Zoom Out"
          >
            －
          </button>
          <button
            type="button"
            onClick={fitGraph}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded text-xs transition"
          >
            Center & Fit
          </button>
        </div>
      </div>

      {/* Main Interactive Canvas & Detail Split View */}
      <div className="flex flex-col lg:flex-row gap-6 h-[640px]">
        {/* Cytoscape Canvas Container */}
        <div
          className={`flex-1 rounded-2xl border shadow-lg overflow-hidden relative transition-colors duration-300 ${
            canvasTheme === 'light'
              ? 'bg-[#f8fafc] border-slate-300'
              : 'bg-slate-950 border-slate-800'
          }`}
          style={
            canvasTheme === 'light'
              ? {
                  backgroundImage: 'radial-gradient(#cbd5e1 1.2px, transparent 1.2px)',
                  backgroundSize: '22px 22px',
                }
              : {
                  backgroundImage: 'radial-gradient(#334155 1.2px, transparent 1.2px)',
                  backgroundSize: '22px 22px',
                }
          }
        >
          <div ref={containerRef} className="w-full h-full" />

          {isLoading && (
            <div
              className={`absolute inset-0 flex items-center justify-center ${
                canvasTheme === 'light' ? 'bg-slate-50/80 text-slate-800' : 'bg-slate-950/85 text-white'
              }`}
            >
              <div className="text-center text-xs font-semibold">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aicte-600 border-t-transparent mb-2" />
                <p>Constructing Cross-Institutional Network...</p>
              </div>
            </div>
          )}

          {/* Canvas Floating Legend */}
          <div
            className={`absolute bottom-4 left-4 p-3 rounded-xl text-xs space-y-1.5 select-none pointer-events-none border shadow-md ${
              canvasTheme === 'light'
                ? 'bg-white/95 border-slate-200 text-slate-800'
                : 'bg-slate-900/95 border-slate-800 text-slate-200'
            }`}
          >
            <div className="flex items-center gap-3 font-medium">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-blue-600 border border-white" /> Institution
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-emerald-500 border border-white" /> Faculty
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-amber-600 border border-white" /> Land Site
              </span>
            </div>
            <div className="flex items-center gap-3 font-medium">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-purple-600 border border-white" /> Trust
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-orange-500 border border-white" /> Signatory
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-slate-500 border border-white" /> Stamp Paper
              </span>
            </div>
            <div className="text-rose-600 font-bold text-[11px] pt-0.5 border-t border-slate-200/60 mt-1">
              ⚠️ Red borders / dashed lines: Multi-campus duplication fraud ring
            </div>
          </div>
        </div>

        {/* Selected Entity / Edge Inspector Panel */}
        <div className="w-full lg:w-80 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm overflow-y-auto flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider pb-3 border-b border-slate-100 mb-4">
              Entity Inspector
            </h3>

            {selectedEntity ? (
              <div className="space-y-4">
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                    Entity Type
                  </span>
                  <span className="px-2.5 py-0.5 rounded text-xs font-bold uppercase bg-slate-100 text-slate-800 border border-slate-200">
                    {selectedEntity.type}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                    Label / Name
                  </span>
                  <p className="text-sm font-bold text-slate-900 leading-snug">
                    {selectedEntity.label}
                  </p>
                </div>

                {selectedEntity.flagged && (
                  <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg">
                    <span className="text-xs font-bold text-rose-900 block mb-1">
                      ⚠️ Active Infraction Flags:
                    </span>
                    <ul className="list-disc pl-4 text-xs text-rose-800 space-y-1">
                      {selectedEntity.flag_reasons?.map((r, i) => (
                        <li key={i}>{r}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                    Extracted Attributes
                  </span>
                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-1 font-mono">
                    {Object.entries(selectedEntity.properties).map(([k, v]) => (
                      <div key={k} className="flex justify-between">
                        <span className="text-slate-500 font-sans">{k}:</span>
                        <span className="font-bold text-slate-800">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : selectedRelation ? (
              <div className="space-y-4">
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                    Relationship Link
                  </span>
                  <span className="px-2.5 py-0.5 rounded text-xs font-bold uppercase bg-slate-100 text-slate-800 border border-slate-200">
                    {selectedRelation.type}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                    Relation Description
                  </span>
                  <p className="text-sm font-bold text-slate-900 leading-snug">
                    {selectedRelation.label}
                  </p>
                </div>

                {selectedRelation.flagged && (
                  <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg">
                    <span className="text-xs font-bold text-rose-900 block mb-1">
                      ⚠️ Flagged Conflict:
                    </span>
                    <p className="text-xs text-rose-800">{selectedRelation.flag_reason}</p>
                    {selectedRelation.confidence && (
                      <p className="mt-1 text-[11px] font-mono text-rose-700">
                        Confidence: {(selectedRelation.confidence * 100).toFixed(0)}%
                      </p>
                    )}
                  </div>
                )}

                <div className="text-xs text-slate-500">
                  <p>Source Entity ID: <strong className="text-slate-700 font-mono">{selectedRelation.source}</strong></p>
                  <p>Target Entity ID: <strong className="text-slate-700 font-mono">{selectedRelation.target}</strong></p>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-slate-400 italic">
                Click any node or relationship link on the graph to inspect detailed attributes and conflict reasoning.
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-slate-100">
            <AdvisoryBadge size="sm" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default GraphPage;
