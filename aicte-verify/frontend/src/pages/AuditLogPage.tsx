import React, { useEffect, useState } from 'react';
import { AuditEntry } from '../types';
import { auditApi, ChainVerificationResult } from '../api/audit';
import AdvisoryBadge from '../components/AdvisoryBadge';

export const AuditLogPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [actorFilter, setActorFilter] = useState('');
  const [actionFilter, setActionFilter] = useState('');

  const [verificationResult, setVerificationResult] = useState<ChainVerificationResult | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [tamperMessage, setTamperMessage] = useState<string | null>(null);

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      const data = await auditApi.getAuditLogs({
        actor: actorFilter || undefined,
        action: actionFilter || undefined,
      });
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  const handleVerifyChain = async () => {
    setIsVerifying(true);
    try {
      const result = await auditApi.verifyChainIntegrity();
      setVerificationResult(result);
    } catch (err) {
      console.error('Chain verification failed', err);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleSimulateTamper = async () => {
    try {
      const res = await auditApi.simulateTamper(2);
      setTamperMessage(res.message);
      await fetchLogs();
      await handleVerifyChain();
    } catch (err) {
      console.error('Simulation failed', err);
    }
  };

  const handleResetTamper = async () => {
    try {
      await auditApi.resetTamper();
      setTamperMessage(null);
      await fetchLogs();
      await handleVerifyChain();
    } catch (err) {
      console.error('Reset failed', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">
            Immutable Audit Trail & Cryptographic Chain
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            SHA-256 hash-linked ledger recording every scrutiny decision, flag resolution, and PII reveal
          </p>
        </div>
        <AdvisoryBadge size="md" />
      </div>

      {/* Chain Integrity Control Strip */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div
            className={`w-4 h-4 rounded-full ${
              verificationResult?.is_valid === false
                ? 'bg-rose-500 animate-ping'
                : 'bg-emerald-500'
            }`}
          />
          <div>
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Cryptographic Ledger Status
            </h4>
            <p className="text-xs text-slate-500">
              {verificationResult
                ? verificationResult.is_valid
                  ? `✓ All ${verificationResult.total_blocks} blocks verified. PrevHash to CurrHash matches exactly.`
                  : `⚠️ ${verificationResult.error_message}`
                : 'Ledger active. Click "Verify Chain Integrity" to perform mathematical hash verification.'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            type="button"
            onClick={handleVerifyChain}
            disabled={isVerifying}
            className="px-4 py-2 bg-aicte-600 hover:bg-aicte-700 text-white font-semibold text-xs rounded-lg shadow-sm transition flex items-center gap-1.5"
          >
            {isVerifying ? (
              'Verifying Hashes...'
            ) : (
              <>
                <span>🔗</span> Verify Chain Integrity
              </>
            )}
          </button>

          {/* Dev Mode Tamper Simulator Button */}
          <button
            type="button"
            onClick={handleSimulateTamper}
            className="px-3 py-2 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-300 font-bold text-xs rounded-lg transition"
            title="Demonstrate tamper-evident defense by altering Block #2"
          >
            Simulate Tamper (Dev)
          </button>

          {tamperMessage && (
            <button
              type="button"
              onClick={handleResetTamper}
              className="px-3 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold text-xs rounded-lg transition"
            >
              Reset Ledger
            </button>
          )}
        </div>
      </div>

      {tamperMessage && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800">
          <strong>Tamper Simulation Active:</strong> {tamperMessage}
        </div>
      )}

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center gap-3">
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="Filter by Actor name or email..."
            value={actorFilter}
            onChange={(e) => setActorFilter(e.target.value)}
            className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg outline-none"
          />
        </div>

        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="text-xs border border-slate-300 rounded-lg p-2 bg-slate-50 outline-none"
        >
          <option value="">All Action Types</option>
          <option value="APPLICATION_SUBMITTED">APPLICATION_SUBMITTED</option>
          <option value="FLAG_GENERATED">FLAG_GENERATED</option>
          <option value="FLAG_RESOLVED">FLAG_RESOLVED</option>
          <option value="PII_REVEAL_VIEWED">PII_REVEAL_VIEWED</option>
          <option value="STATUS_UPDATED">STATUS_UPDATED</option>
        </select>

        <button
          type="button"
          onClick={fetchLogs}
          className="px-3 py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold"
        >
          Apply Filters
        </button>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="py-16 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aicte-600 border-t-transparent" />
            <p className="mt-2 text-xs text-slate-500 font-semibold">Loading Audit Blocks...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="py-16 text-center text-xs text-slate-500">No audit entries found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-100 text-slate-700 font-semibold uppercase text-[11px]">
                  <th className="py-3 px-4">Block / Time</th>
                  <th className="py-3 px-4">Actor</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Entity</th>
                  <th className="py-3 px-4">Details</th>
                  <th className="py-3 px-4">Chain Hash (Prev → Curr)</th>
                  <th className="py-3 px-4">Integrity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {logs.map((entry, idx) => (
                  <tr
                    key={entry.id}
                    className={`hover:bg-slate-50 transition ${
                      entry.is_tampered ? 'bg-rose-50/70 border-l-4 border-l-rose-600' : ''
                    }`}
                  >
                    <td className="py-3.5 px-4 font-sans whitespace-nowrap">
                      <span className="font-bold text-slate-900 block font-mono">#{idx + 1}</span>
                      <span className="text-[10px] text-slate-400">
                        {new Date(entry.timestamp).toLocaleString()}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-sans whitespace-nowrap">
                      <span className="font-semibold text-slate-800 block">{entry.actor_name}</span>
                      <span className="text-[10px] text-slate-400 capitalize">{entry.actor_role}</span>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className="font-bold px-2 py-0.5 rounded text-[10px] bg-slate-100 text-slate-800 border border-slate-200">
                        {entry.action}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap font-sans text-slate-600">
                      {entry.entity_type}: <span className="font-mono text-slate-800">{entry.entity_id}</span>
                    </td>
                    <td className="py-3.5 px-4 font-sans text-slate-700 max-w-xs truncate">
                      {entry.details}
                    </td>
                    <td className="py-3.5 px-4 text-[10px] text-slate-500 max-w-[200px]">
                      <div className="truncate text-slate-400" title={`Prev: ${entry.prev_hash}`}>
                        P: {entry.prev_hash.substring(0, 16)}...
                      </div>
                      <div className="truncate font-bold text-indigo-700" title={`Curr: ${entry.curr_hash}`}>
                        C: {entry.curr_hash.substring(0, 16)}...
                      </div>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {entry.is_tampered ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-600 text-white uppercase">
                          TAMPERED!
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                          VALID HASH
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLogPage;
