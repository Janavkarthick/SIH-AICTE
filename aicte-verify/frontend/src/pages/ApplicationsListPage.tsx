import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Application, User } from '../types';
import { applicationsApi } from '../api/applications';
import RiskBadge from '../components/RiskBadge';
import StatusBadge from '../components/StatusBadge';
import AdvisoryBadge from '../components/AdvisoryBadge';
import { NewApplicationModal } from '../components/NewApplicationModal';

export const ApplicationsListPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [regionFilter, setRegionFilter] = useState('');
  const [sortBy, setSortBy] = useState<'risk_desc' | 'risk_asc' | 'date_desc' | 'date_asc'>('risk_desc');
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

  const fetchApplications = async () => {
    setIsLoading(true);
    try {
      const data = await applicationsApi.getApplications({
        status: statusFilter || undefined,
        risk_level: riskFilter || undefined,
        region: regionFilter || undefined,
        search: searchTerm || undefined,
      });
      setApplications(data);
    } catch (err) {
      console.error('Failed to load applications', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, [statusFilter, riskFilter, regionFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchApplications();
  };

  // Sorting
  const sortedApplications = [...applications].sort((a, b) => {
    if (sortBy === 'risk_desc') return b.risk_score - a.risk_score;
    if (sortBy === 'risk_asc') return a.risk_score - b.risk_score;
    if (sortBy === 'date_desc')
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    if (sortBy === 'date_asc')
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
    return 0;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">
            {isCollege
              ? 'My Institution Applications'
              : isOfficer
              ? `Regional Applications (${user?.region || 'Regional'} Jurisdiction)`
              : 'Affiliation & Approval Applications (National)'}
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            {isCollege
              ? 'Official AICTE Extension of Approval records for your institution'
              : isOfficer
              ? `Applications under scrutiny within ${user?.region || 'Regional'} territory`
              : 'Comprehensive repository of AICTE institutional applications across all regional jurisdictions'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <AdvisoryBadge size="md" />
          {isCollege && (
            <Link
              to="/apply"
              className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-sm flex items-center gap-1.5 transition"
            >
              <span>➕</span> Apply for Approval / EoA
            </Link>
          )}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
        <form onSubmit={handleSearch} className="flex flex-wrap items-center gap-3">
          {/* Search Box */}
          <div className="flex-1 min-w-[260px] relative">
            <input
              type="text"
              placeholder="Search by Institution, Application No, or State..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full text-xs pl-8 pr-3 py-2 border border-slate-300 rounded-lg focus:ring-1 focus:ring-aicte-500 outline-none"
            />
            <span className="absolute left-2.5 top-2.5 text-slate-400 text-xs">🔍</span>
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg p-2 bg-slate-50 outline-none"
          >
            <option value="">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="submitted">Submitted</option>
            <option value="under_review">Under Review</option>
            <option value="verified">Verified</option>
            <option value="deficiency_issued">Deficiency Issued</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>

          {/* Risk Level Filter */}
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg p-2 bg-slate-50 outline-none"
          >
            <option value="">All Risk Levels</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>

          {/* Region Filter (Admin Only) */}
          {isAdmin && (
            <select
              value={regionFilter}
              onChange={(e) => setRegionFilter(e.target.value)}
              className="text-xs border border-slate-300 rounded-lg p-2 bg-slate-50 outline-none"
            >
              <option value="">All Regions</option>
              <option value="Southern">Southern</option>
              <option value="Western">Western</option>
              <option value="Northern">Northern</option>
              <option value="Eastern">Eastern</option>
              <option value="Central">Central</option>
            </select>
          )}

          {/* Sort By */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="text-xs border border-slate-300 rounded-lg p-2 bg-slate-50 outline-none font-medium"
          >
            <option value="risk_desc">Sort: Risk Score (High → Low)</option>
            <option value="risk_asc">Sort: Risk Score (Low → High)</option>
            <option value="date_desc">Sort: Date (Newest First)</option>
            <option value="date_asc">Sort: Date (Oldest First)</option>
          </select>

          <button
            type="submit"
            className="px-4 py-2 bg-aicte-600 hover:bg-aicte-700 text-white font-semibold text-xs rounded-lg shadow-sm"
          >
            Search
          </button>
        </form>
      </div>

      {/* Applications Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="py-16 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aicte-600 border-t-transparent" />
            <p className="mt-2 text-xs text-slate-500 font-semibold">Filtering Applications...</p>
          </div>
        ) : sortedApplications.length === 0 ? (
          <div className="py-16 text-center">
            <p className="text-sm font-semibold text-slate-600">No applications found matching criteria.</p>
            <button
              onClick={() => {
                setSearchTerm('');
                setStatusFilter('');
                setRiskFilter('');
                setRegionFilter('');
              }}
              className="mt-3 text-xs text-aicte-600 hover:underline font-medium"
            >
              Reset all filters
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase text-[11px]">
                  <th className="py-3 px-4">Application Number</th>
                  <th className="py-3 px-4">Institution Name</th>
                  <th className="py-3 px-4">Region / State</th>
                  <th className="py-3 px-4">Applied Intake</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Risk Evaluation</th>
                  <th className="py-3 px-4">Flags</th>
                  <th className="py-3 px-4">Submitted At</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sortedApplications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50 transition">
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-900">
                      <Link to={`/applications/${app.id}`} className="text-aicte-600 hover:underline">
                        {app.application_number}
                      </Link>
                      <span className="block text-[10px] text-slate-400 font-normal">v{app.submission_version}</span>
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-800 max-w-sm">
                      <div className="truncate">{app.institution_name}</div>
                      <span className="text-[10px] text-slate-500 font-normal">{app.institution_type}</span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 whitespace-nowrap">
                      {app.region} • {app.state}
                    </td>
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-800">
                      {app.applied_intake} seats
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <StatusBadge status={app.status} type="application" />
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <RiskBadge level={app.risk_level} score={app.risk_score} />
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
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
                    <td className="py-3.5 px-4 text-slate-500 whitespace-nowrap text-[11px]">
                      {new Date(app.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      <Link
                        to={`/applications/${app.id}`}
                        className="px-3 py-1.5 bg-aicte-600 hover:bg-aicte-700 text-white font-semibold rounded text-xs shadow-sm transition"
                      >
                        Review
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <NewApplicationModal
        isOpen={showApplyModal}
        onClose={() => setShowApplyModal(false)}
        institutionName={applications[0]?.institution_name || user?.full_name}
        institutionId={user?.institution_id}
        onCreated={(newApp) => {
          setApplications((prev) => [newApp, ...prev]);
        }}
      />
    </div>
  );
};

export default ApplicationsListPage;
