import React, { useEffect, useState } from 'react';
import { EvaluationResult } from '../types';
import { evaluationApi } from '../api/evaluation';
import AdvisoryBadge from '../components/AdvisoryBadge';

export const EvaluationPage: React.FC = () => {
  const [evalResult, setEvalResult] = useState<EvaluationResult | null>(null);
  const [isRunningBenchmark, setIsRunningBenchmark] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const fetchEval = async () => {
    setIsLoading(true);
    try {
      const data = await evaluationApi.getEvaluationResults();
      setEvalResult(data);
    } catch (err) {
      console.error('Failed to load evaluation metrics', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEval();
  }, []);

  const handleRunBenchmark = async () => {
    setIsRunningBenchmark(true);
    try {
      const updated = await evaluationApi.runBenchmark();
      setEvalResult(updated);
    } catch (err) {
      console.error('Benchmark execution failed', err);
    } finally {
      setIsRunningBenchmark(false);
    }
  };

  if (isLoading || !evalResult) {
    return (
      <div className="py-20 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aicte-600 border-t-transparent" />
        <p className="mt-2 text-xs text-slate-500 font-semibold">Loading Benchmark Metrics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">
            Model Evaluation & Benchmark Performance
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Validation of OCR pipelines, forensic ELA heuristics, and cross-registry deduplication against ground-truth datasets
          </p>
        </div>
        <div className="flex items-center gap-3">
          <AdvisoryBadge size="md" />
          <button
            type="button"
            onClick={handleRunBenchmark}
            disabled={isRunningBenchmark}
            className="px-4 py-2 bg-aicte-600 hover:bg-aicte-700 text-white rounded-lg text-xs font-semibold shadow-sm transition flex items-center gap-2"
          >
            {isRunningBenchmark && (
              <svg className="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            )}
            {isRunningBenchmark ? 'Running 250 Tests...' : 'Run Benchmark Suite ⚡'}
          </button>
        </div>
      </div>

      {/* Mandatory Synthetic Evaluation Methodology Banner */}
      <div className="p-4 bg-amber-50 border-l-4 border-amber-500 rounded-r-xl text-xs text-amber-950 shadow-sm space-y-1">
        <p className="font-bold">Synthetic Benchmark Methodology — Not Real-World Accuracy</p>
        <p className="text-amber-900 leading-relaxed">
          Clean and faulty documents were produced by the same synthetic generator, so these results are not real-world accuracy.
          All tests use neutral filenames (<code>DOC_0001.pdf</code>..<code>DOC_0295.jpg</code>) with zero hints.
        </p>
        <div className="pt-1 text-[11px] text-amber-800 flex flex-wrap gap-4 font-mono">
          <span>• Host: Windows 11 / Python 3.14.6</span>
          <span>• PyMuPDF Native: Not Available (reports <code>not_run</code>)</span>
          <span>• Docker Production: Linux Debian 12 / PyMuPDF 1.24.10</span>
        </div>
      </div>

      {/* Detailed Checks Breakdown Table (Primary View: Per-Check Metrics) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <span className="text-xs font-bold uppercase text-slate-700 tracking-wider">
            Per-Check Performance Metrics Breakdown (16 Specialized Checks)
          </span>
          <span className="text-xs text-slate-500">Threshold: F1 ≥ 90.0% for Statutory Benchmark</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-100 text-slate-700 font-semibold uppercase text-[11px]">
                <th className="py-3 px-4">Verification Check Pipeline</th>
                <th className="py-3 px-4">Test Samples</th>
                <th className="py-3 px-4">Precision</th>
                <th className="py-3 px-4">Recall</th>
                <th className="py-3 px-4">F1 Score</th>
                <th className="py-3 px-4 text-right">Validation Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {evalResult.detailed_checks.map((check, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition">
                  <td className="py-3.5 px-4 font-sans font-bold text-slate-900">{check.check_name}</td>
                  <td className="py-3.5 px-4 text-slate-600">{check.sample_count} Docs</td>
                  <td className="py-3.5 px-4 font-semibold text-blue-700">
                    {check.status === 'NOT RUN' ? 'N/A' : `${check.precision.toFixed(1)}%`}
                  </td>
                  <td className="py-3.5 px-4 font-semibold text-indigo-700">
                    {check.status === 'NOT RUN' ? 'N/A' : `${check.recall.toFixed(1)}%`}
                  </td>
                  <td className="py-3.5 px-4 font-bold text-slate-900">
                    {check.status === 'NOT RUN' ? 'N/A' : `${check.f1.toFixed(1)}%`}
                  </td>
                  <td className="py-3.5 px-4 text-right font-sans">
                    {check.status === 'NOT RUN' ? (
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-300">
                        ○ NOT RUN
                      </span>
                    ) : check.status === 'REVIEW' ? (
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300">
                        ⚠ REVIEW
                      </span>
                    ) : (
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                        ✓ PASS
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dataset & Overall KPI Strip (Synthetic benchmark, not real-world accuracy) */}
      <div className="space-y-2">
        <p className="text-xs font-bold uppercase text-slate-500 tracking-wider">
          Synthetic Benchmark Aggregate Metrics (Synthetic benchmark, not real-world accuracy)
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <p className="text-xs font-bold uppercase text-slate-400">Benchmark Accuracy</p>
            <h3 className="text-3xl font-black text-emerald-600 mt-1">{evalResult.accuracy}%</h3>
            <p className="text-[10px] text-slate-500 mt-1">{evalResult.total_samples} Synthetic Test Docs</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <p className="text-xs font-bold uppercase text-slate-400">Benchmark Precision</p>
            <h3 className="text-3xl font-black text-blue-600 mt-1">{evalResult.precision}%</h3>
            <p className="text-[10px] text-slate-500 mt-1">Synthetic fault specificity</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <p className="text-xs font-bold uppercase text-slate-400">Benchmark Recall</p>
            <h3 className="text-3xl font-black text-indigo-600 mt-1">{evalResult.recall}%</h3>
            <p className="text-[10px] text-slate-500 mt-1">Planted defect sensitivity</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <p className="text-xs font-bold uppercase text-slate-400">Benchmark F1-Score</p>
            <h3 className="text-3xl font-black text-purple-600 mt-1">{evalResult.f1_score}%</h3>
            <p className="text-[10px] text-slate-500 mt-1">Harmonic mean balance</p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <p className="text-xs font-bold uppercase text-slate-400">Pipeline Latency</p>
            <h3 className="text-3xl font-black text-slate-800 mt-1 font-mono">
              {evalResult.execution_time_ms} ms
            </h3>
            <p className="text-[10px] text-slate-500 mt-1">Avg 7.3ms per check</p>
          </div>
        </div>
      </div>

      {/* Dataset Details Callout */}
      <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs flex flex-wrap items-center justify-between gap-3">
        <div>
          <span className="font-bold text-slate-700">Test Benchmark Dataset:</span>{' '}
          <span className="text-slate-600 font-mono">{evalResult.test_set_name}</span>
        </div>
        <div className="text-slate-500 font-mono text-[11px]">
          Last Evaluated: {new Date(evalResult.evaluated_at).toLocaleString()}
        </div>
      </div>
    </div>
  );
};

export default EvaluationPage;
