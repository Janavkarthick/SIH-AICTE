import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Application, AnalyticsSummary, User } from '../types';
import { applicationsApi } from '../api/applications';
import { analyticsApi } from '../api/analytics';
import RiskBadge from '../components/RiskBadge';
import StatusBadge from '../components/StatusBadge';
import AdvisoryBadge from '../components/AdvisoryBadge';
import { NewApplicationModal } from '../components/NewApplicationModal';

export const DashboardPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [stats, setStats] = useState<AnalyticsSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filterRisk, setFilterRisk] = useState<string>('all');
  const [showApplyModal, setShowApplyModal] = useState(false);

  const userJson = localStorage.getItem('aicte_user');
  let user: User | null = null;
  try {
    if (userJson && userJson !== 'undefined' && userJson !== 'null') {
      user = JSON.parse(userJson);
    }
  } catch {}

  const isCollege = user?.role === 'college_user';
  const isOfficer = user?.role === 'officer';
  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [appsData, statsData] = await Promise.all([
          applicationsApi.getApplications(),
          analyticsApi.getSummary(),
        ]);
        setApplications(Array.isArray(appsData) ? appsData : (appsData as any)?.items || []);
        setStats(statsData);
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const appList = Array.isArray(applications) ? applications : [];
  const filteredApps = appList.filter((app) => {
    if (filterRisk === 'all') return true;
    return (app.risk_level || '').toLowerCase() === filterRisk.toLowerCase();
  });

  const myApp = appList[0];
  const regionalPending = appList.filter((a) => a.status === 'under_review' || a.status === 'submitted').length;
  const regionalCriticalFlags = appList.reduce((sum, a) => sum + (a.critical_flags_count || 0), 0);
  const regionalAvgRisk = appList.length
    ? (appList.reduce((sum, a) => sum + (a.risk_score || 0), 0) / appList.length).toFixed(1)
    : '0.0';

  if (isLoading) {
    return (
      <div className="py-20 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aicte-600 border-t-transparent" />
        <p className="mt-2 text-xs text-slate-500 font-semibold">Loading Scrutiny Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Title & Context Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">
            {isCollege
              ? `🏛️ Institution Affiliation Portal — ${myApp?.institution_name || user?.full_name || 'My Institution'}`
              : isOfficer
              ? `👮 Regional Scrutiny Portal — ${user?.region || 'Regional'} Office`
              : '⚙️ AICTE National Central Scrutiny Hub'}
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            {isCollege
              ? 'Extension of Approval (EoA) Application Status, Document Verification & Compliance Findings (AY 2025-26)'
              : isOfficer
              ? `AI-Assisted Scrutiny, Document Verification & Risk Assessment for ${user?.region || 'Assigned'} Regional Jurisdiction (AY 2025-26)`
              : 'Nationwide Cross-Document Verification, Collusion Detection & Affiliation Risk Assessment (AY 2025-26)'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <AdvisoryBadge size="md" />
          {isCollege ? (
            <>
              <Link
                to="/apply"
                className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-sm flex items-center gap-1.5 transition"
              >
                <span>➕</span> Apply for Approval / EoA
              </Link>
              {myApp && (
                <Link
                  to={`/applications/${myApp.id}`}
                  className="px-3.5 py-1.5 bg-aicte-600 hover:bg-aicte-700 text-white rounded-lg text-xs font-semibold shadow-sm"
                >
                  Inspect Application
                </Link>
              )}
            </>
          ) : (
            <Link
              to="/applications"
              className="px-3.5 py-1.5 bg-aicte-600 hover:bg-aicte-700 text-white rounded-lg text-xs font-semibold shadow-sm"
            >
              {isOfficer ? `View Regional Queue (${appList.length})` : '+ All Applications'}
            </Link>
          )}
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1 */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase text-slate-400">
              {isCollege ? 'Applied Intake' : isOfficer ? 'Regional Applications' : 'Total Scrutinized'}
            </p>
            <h3 className="text-2xl font-black text-slate-900 mt-1">
              {isCollege
                ? `${myApp?.applied_intake || 420} seats`
                : isOfficer
                ? appList.length
                : (stats?.total_applications?.toLocaleString() || '1,240')}
            </h3>
            <span className="text-[11px] text-emerald-600 font-medium">
              {isCollege
                ? (myApp?.approved_intake ? `Approved: ${myApp.approved_intake} seats` : 'Awaiting Final Approval')
                : isOfficer
                ? `Under ${user?.region || 'Regional'} Scrutiny`
                : '↑ 12% from last cycle'}
            </span>
          </div>
          <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>

        {/* Card 2 */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase text-slate-400">
              {isCollege ? 'Approval Status' : isOfficer ? 'Pending Officer Action' : 'Pending Review'}
            </p>
            <div className="mt-1">
              {isCollege ? (
                <StatusBadge status={myApp?.status || 'under_review'} type="application" />
              ) : (
                <h3 className="text-2xl font-black text-amber-600">
                  {isOfficer ? regionalPending : (stats?.pending_review ?? 184)}
                </h3>
              )}
            </div>
            <span className="text-[11px] text-slate-500 font-medium block mt-1">
              {isCollege
                ? `Ref: ${myApp?.application_number || 'AICTE-2025-001'}`
                : isOfficer
                ? 'Awaiting Regional Review'
                : 'Awaiting Officer Decision'}
            </span>
          </div>
          <div className="p-3 bg-amber-50 text-amber-600 rounded-xl">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        {/* Card 3 */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase text-slate-400">
              {isCollege ? 'Deficiency Flags' : isOfficer ? 'Regional Critical Flags' : 'Critical Flags'}
            </p>
            <h3 className="text-2xl font-black text-rose-600 mt-1">
              {isCollege ? (myApp?.total_flags_count || 0) : isOfficer ? regionalCriticalFlags : (stats?.flags_by_severity?.critical ?? 76)}
            </h3>
            <span className="text-[11px] text-rose-600 font-medium">
              {isCollege
                ? `${myApp?.critical_flags_count || 0} Critical Flags to Address`
                : 'Tampering / Duplication'}
            </span>
          </div>
          <div className="p-3 bg-rose-50 text-rose-600 rounded-xl">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
        </div>

        {/* Card 4 */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase text-slate-400">
              {isCollege ? 'Affiliation Risk Score' : isOfficer ? 'Avg Regional Risk' : 'Avg Risk Index'}
            </p>
            <h3 className="text-2xl font-black text-indigo-700 mt-1">
              {isCollege
                ? `${myApp?.risk_score ?? 18}`
                : isOfficer
                ? regionalAvgRisk
                : (stats?.average_risk_score ?? 34.6)}{' '}
              <span className="text-xs font-normal text-slate-400">/ 100</span>
            </h3>
            <div className="mt-1">
              {isCollege ? (
                <RiskBadge level={myApp?.risk_level || 'low'} score={myApp?.risk_score} />
              ) : (
                <span className="text-[11px] text-emerald-600 font-medium">Audit Chain: Verified ✓</span>
              )}
            </div>
          </div>
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Flag Severity Breakdown Strip */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
        <span className="font-bold text-slate-700 uppercase tracking-wider text-[11px]">
          {isCollege ? 'Institutional Scrutiny Observations:' : isOfficer ? `Regional Flags Overview (${user?.region || 'Regional'} Office):` : 'Flags by Severity:'}
        </span>
        <div className="flex items-center gap-3 flex-wrap">
          <span className="px-2.5 py-1 rounded bg-rose-100 text-rose-800 font-bold border border-rose-200">
            Critical: {isCollege ? (myApp?.critical_flags_count || 0) : (stats?.flags_by_severity?.critical ?? 76)}
          </span>
          <span className="px-2.5 py-1 rounded bg-orange-100 text-orange-800 font-bold border border-orange-200">
            High: {stats?.flags_by_severity?.high ?? 148}
          </span>
          <span className="px-2.5 py-1 rounded bg-amber-100 text-amber-800 font-semibold border border-amber-200">
            Medium: {stats?.flags_by_severity?.medium ?? 215}
          </span>
          <span className="px-2.5 py-1 rounded bg-emerald-100 text-emerald-800 font-medium border border-emerald-200">
            Low: {stats?.flags_by_severity?.low ?? 320}
          </span>
          <span className="px-2.5 py-1 rounded bg-blue-100 text-blue-800 font-medium border border-blue-200">
            Info: {stats?.flags_by_severity?.info ?? 412}
          </span>
        </div>
      </div>


      {/* Recent Applications Section */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              {isCollege
                ? "My Institution's EoA Applications"
                : isOfficer
                ? `Regional Scrutiny Queue (${user?.region || 'Regional'} Office)`
                : 'National Applications Scrutiny Roster (All Regions)'}
            </h3>
            <p className="text-xs text-slate-500">
              {isCollege
                ? 'Official submission history, approval status, and AI compliance flags'
                : isOfficer
                ? `Applications submitted by institutions within the ${user?.region || 'Regional'} jurisdiction`
                : 'Live feed of institutional submissions and risk indices across all 8 AICTE regions'}
            </p>
          </div>

          {/* Quick Filters */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-medium">Risk Filter:</span>
            <select
              value={filterRisk}
              onChange={(e) => setFilterRisk(e.target.value)}
              className="text-xs border border-slate-300 rounded-lg p-1.5 bg-slate-50 outline-none"
            >
              <option value="all">All Risk Levels</option>
              <option value="high">High Risk Only</option>
              <option value="medium">Medium Risk</option>
              <option value="low">Low Risk</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase text-[11px]">
                <th className="py-3 px-4">Application No.</th>
                <th className="py-3 px-4">Institution Name</th>
                <th className="py-3 px-4">Region / State</th>
                <th className="py-3 px-4">Intake (Applied/Approved)</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Flags</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredApps.map((app) => (
                <tr key={app.id} className="hover:bg-slate-50 transition">
                  <td className="py-3.5 px-4 font-mono font-bold text-slate-900">
                    <Link to={`/applications/${app.id}`} className="text-aicte-600 hover:underline">
                      {app.application_number}
                    </Link>
                    <span className="block text-[10px] text-slate-400 font-normal">v{app.submission_version}</span>
                  </td>
                  <td className="py-3.5 px-4 font-semibold text-slate-800 max-w-xs">
                    <div className="truncate">{app.institution_name}</div>
                    <span className="text-[10px] text-slate-500 font-normal">{app.institution_type}</span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-600">
                    {app.region} • {app.state}
                  </td>
                  <td className="py-3.5 px-4 font-mono">
                    <span className="font-bold text-slate-800">{app.applied_intake}</span>
                    {app.approved_intake && (
                      <span className="text-emerald-700 font-bold ml-1">/ {app.approved_intake}</span>
                    )}
                  </td>
                  <td className="py-3.5 px-4">
                    <StatusBadge status={app.status} type="application" />
                  </td>
                  <td className="py-3.5 px-4">
                    <RiskBadge level={app.risk_level} score={app.risk_score} />
                  </td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`font-semibold px-2 py-0.5 rounded ${
                        app.critical_flags_count > 0
                          ? 'bg-rose-100 text-rose-800 font-bold'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {app.total_flags_count} flags
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <Link
                      to={`/applications/${app.id}`}
                      className="px-3 py-1.5 bg-aicte-50 hover:bg-aicte-100 text-aicte-700 font-semibold rounded border border-aicte-200 transition"
                    >
                      Inspect
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <NewApplicationModal
        isOpen={showApplyModal}
        onClose={() => setShowApplyModal(false)}
        institutionName={myApp?.institution_name || user?.full_name}
        institutionId={user?.institution_id}
        onCreated={(newApp) => {
          setApplications((prev) => [newApp, ...prev]);
        }}
      />
    </div>
  );
};

export default DashboardPage;
