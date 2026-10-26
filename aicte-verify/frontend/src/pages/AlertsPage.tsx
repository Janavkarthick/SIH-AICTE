import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Alert, AlertCategory, FlagSeverity } from '../types';
import { analyticsApi } from '../api/analytics';
import AdvisoryBadge from '../components/AdvisoryBadge';

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const data = await analyticsApi.getAlerts(categoryFilter || undefined, severityFilter || undefined);
      setAlerts(data);
    } catch (err) {
      console.error('Failed to load alerts', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [categoryFilter, severityFilter]);

  const handleDismiss = async (alertId: string) => {
    try {
      await analyticsApi.dismissAlert(alertId);
      setAlerts((prev) => prev.filter((a) => a.id !== alertId));
    } catch (err) {
      console.error('Failed to dismiss alert', err);
    }
  };

  const getCategoryBadge = (cat: AlertCategory) => {
    switch (cat) {
      case 'anomalies':
        return <span className="bg-rose-100 text-rose-800 text-[10px] font-bold px-2 py-0.5 rounded">Forensic Anomaly</span>;
      case 'unresolved':
        return <span className="bg-orange-100 text-orange-800 text-[10px] font-bold px-2 py-0.5 rounded">Unresolved Conflict</span>;
      case 'missing_docs':
        return <span className="bg-amber-100 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded">Missing Statutory Doc</span>;
      case 'expired':
        return <span className="bg-purple-100 text-purple-800 text-[10px] font-bold px-2 py-0.5 rounded">Expired Certificate</span>;
      case 'pending_verification':
        return <span className="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded">Pending Registry Check</span>;
    }
  };

  const getSeverityBadge = (sev: FlagSeverity) => {
    switch (sev) {
      case 'critical':
        return <span className="bg-rose-600 text-white text-[10px] font-bold px-2 py-0.5 rounded animate-pulse">CRITICAL</span>;
      case 'high':
        return <span className="bg-orange-500 text-white text-[10px] font-bold px-2 py-0.5 rounded">HIGH</span>;
      case 'medium':
        return <span className="bg-amber-500 text-white text-[10px] font-bold px-2 py-0.5 rounded">MEDIUM</span>;
      case 'low':
      case 'info':
        return <span className="bg-blue-500 text-white text-[10px] font-bold px-2 py-0.5 rounded">LOW</span>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Statutory Alerts & Discrepancies</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Automated notifications regarding missing proofs, expired certifications, and forensic anomalies
          </p>
        </div>
        <AdvisoryBadge size="md" />
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center gap-3">
        <span className="text-xs font-bold text-slate-700">Filter By:</span>

        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="text-xs border border-slate-300 rounded-lg p-2 bg-slate-50 outline-none"
        >
          <option value="">All Categories</option>
          <option value="anomalies">Forensic Anomalies</option>
          <option value="unresolved">Unresolved Conflicts</option>
          <option value="missing_docs">Missing Statutory Documents</option>
          <option value="expired">Expired Certificates</option>
          <option value="pending_verification">Pending Gateway Verification</option>
        </select>

        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="text-xs border border-slate-300 rounded-lg p-2 bg-slate-50 outline-none"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Alerts List */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="py-16 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aicte-600 border-t-transparent" />
            <p className="mt-2 text-xs text-slate-500 font-semibold">Loading Alerts...</p>
          </div>
        ) : alerts.length === 0 ? (
          <div className="py-16 text-center text-slate-500 text-xs font-semibold">
            No active statutory alerts found.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {alerts.map((alert) => (
              <div key={alert.id} className="p-5 hover:bg-slate-50 transition flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    {getSeverityBadge(alert.severity)}
                    {getCategoryBadge(alert.category)}
                    <span className="font-mono text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                      {alert.application_number}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-900 mt-1">{alert.title}</h3>
                  <p className="text-xs text-slate-600">{alert.description}</p>
                  <p className="text-[11px] text-slate-400">
                    Institution: <strong className="text-slate-700">{alert.institution_name}</strong> •{' '}
                    {new Date(alert.created_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <Link
                    to={`/applications/${alert.application_id}`}
                    className="px-3 py-1.5 bg-aicte-50 hover:bg-aicte-100 text-aicte-700 font-semibold text-xs rounded-lg border border-aicte-200"
                  >
                    Investigate
                  </Link>

                  <button
                    type="button"
                    onClick={() => handleDismiss(alert.id)}
                    className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 font-semibold text-xs rounded-lg"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertsPage;
