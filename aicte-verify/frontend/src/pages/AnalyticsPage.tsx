import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { AnalyticsSummary } from '../types';
import { analyticsApi } from '../api/analytics';
import AdvisoryBadge from '../components/AdvisoryBadge';

export const AnalyticsPage: React.FC = () => {
  const [stats, setStats] = useState<AnalyticsSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const data = await analyticsApi.getSummary();
        setStats(data);
      } catch (err) {
        console.error('Failed to load analytics', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (isLoading || !stats) {
    return (
      <div className="py-20 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aicte-600 border-t-transparent" />
        <p className="mt-2 text-xs text-slate-500 font-semibold">Generating Scrutiny Analytics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">
            Scrutiny & Affiliation Analytics Hub
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Statistical distribution of regulatory flags, forensic anomalies, and verification turnaround trends
          </p>
        </div>
        <AdvisoryBadge size="md" />
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold uppercase text-slate-400">Total Scrutiny Applications</p>
          <h3 className="text-2xl font-black text-slate-900 mt-1">
            {stats.total_applications.toLocaleString()}
          </h3>
          <p className="text-[11px] text-slate-500 mt-1">Across Southern, Northern & Western SROs</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold uppercase text-slate-400">Approval Rate</p>
          <h3 className="text-2xl font-black text-emerald-600 mt-1">
            {((stats.approved_applications / stats.total_applications) * 100).toFixed(1)}%
          </h3>
          <p className="text-[11px] text-slate-500 mt-1">
            {stats.approved_applications} granted Extension of Approval
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold uppercase text-slate-400">Deficiency Rate</p>
          <h3 className="text-2xl font-black text-amber-600 mt-1">
            {(((stats.total_applications - stats.approved_applications) / stats.total_applications) * 100).toFixed(1)}%
          </h3>
          <p className="text-[11px] text-slate-500 mt-1">Flags or compliance gaps requiring hearing</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold uppercase text-slate-400">Avg Turnaround Time</p>
          <h3 className="text-2xl font-black text-indigo-700 mt-1">3.2 Days</h3>
          <p className="text-[11px] text-emerald-600 font-medium">↓ 77% faster via AI OCR pipeline</p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Flags by Regulatory Type */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-1">
            Distribution of Flags by Infraction Type
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            Most frequent triggers identified during automated cross-document verification
          </p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.flags_by_type}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="type" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" height={50} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Statutory Verification Outcomes (Pie Chart) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-1">
            Registry Verification Outcomes
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            NSDL PAN, State Land, and National Faculty Registry validation breakdown
          </p>
          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.verification_outcomes}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={45}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {stats.verification_outcomes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend verticalAlign="bottom" height={36} iconSize={10} wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Scrutiny Turnaround Trend (Line Chart) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-1">
            Average Processing Time per Application (Days)
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            Turnaround speed acceleration as automated pipelines index local registry tables
          </p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats.processing_times_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="week" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} unit=" d" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                />
                <Line
                  type="monotone"
                  dataKey="avg_days"
                  name="Avg Processing Days"
                  stroke="#10b981"
                  strokeWidth={3}
                  dot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Applications by Status (Bar Chart) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-1">
            Applications by Current Statutory Status
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            Workflow pipeline distribution across all active institutional cases
          </p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.applications_by_status} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis dataKey="status" type="category" tick={{ fontSize: 11 }} width={110} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
