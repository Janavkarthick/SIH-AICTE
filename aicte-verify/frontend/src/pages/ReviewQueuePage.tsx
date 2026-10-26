import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Application } from '../types';
import { applicationsApi } from '../api/applications';
import RiskBadge from '../components/RiskBadge';
import StatusBadge from '../components/StatusBadge';
import AdvisoryBadge from '../components/AdvisoryBadge';
import ConfirmModal from '../components/ConfirmModal';

export const ReviewQueuePage: React.FC = () => {
  const [queue, setQueue] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAppForReview, setSelectedAppForReview] = useState<Application | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const loadQueue = async () => {
    setIsLoading(true);
    try {
      const apps = await applicationsApi.getApplications();
      // Filter items requiring review (under_review, submitted, deficiency_issued) sorted by risk descending
      const pending = apps
        .filter((a) => a.status === 'under_review' || a.status === 'submitted' || a.status === 'deficiency_issued')
        .sort((a, b) => b.risk_score - a.risk_score);
      setQueue(pending);
    } catch (err) {
      console.error('Error fetching review queue', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const handleMarkReviewed = async (notes?: string) => {
    if (!selectedAppForReview) return;
    setIsProcessing(true);
    try {
      await applicationsApi.updateStatus(
        selectedAppForReview.id,
        'verified',
        notes || 'Officer completed manual scrutiny review.'
      );
      setSelectedAppForReview(null);
      await loadQueue();
    } catch (err) {
      console.error('Failed to mark reviewed', err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">Officer Manual Scrutiny Queue</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Prioritized backlog of pending institutional applications ranked by composite risk score
          </p>
        </div>
        <AdvisoryBadge size="md" />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <span className="text-xs font-bold uppercase text-slate-700 tracking-wider">
            Pending Queue Items ({queue.length})
          </span>
          <span className="text-xs text-slate-500">Sorted by Severity & Risk Index</span>
        </div>

        {isLoading ? (
          <div className="py-16 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aicte-600 border-t-transparent" />
            <p className="mt-2 text-xs text-slate-500 font-semibold">Loading Queue...</p>
          </div>
        ) : queue.length === 0 ? (
          <div className="py-16 text-center">
            <p className="text-sm font-semibold text-slate-600">
              🎉 No applications currently awaiting manual review.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {queue.map((app) => (
              <div
                key={app.id}
                className="p-5 hover:bg-slate-50/80 transition flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono text-xs font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded">
                      {app.application_number}
                    </span>
                    <StatusBadge status={app.status} type="application" />
                    <RiskBadge level={app.risk_level} score={app.risk_score} />
                    {app.critical_flags_count > 0 && (
                      <span className="text-xs font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                        {app.critical_flags_count} Critical Flags
                      </span>
                    )}
                  </div>

                  <h3 className="text-sm font-bold text-slate-900">{app.institution_name}</h3>
                  <p className="text-xs text-slate-500">
                    {app.institution_type} • {app.region} Region • Applied: {app.applied_intake} seats
                  </p>

                  {app.summary && (
                    <p className="text-xs text-slate-600 line-clamp-1 italic">
                      "{app.summary}"
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <Link
                    to={`/applications/${app.id}`}
                    className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold rounded-lg transition"
                  >
                    View File
                  </Link>

                  <button
                    type="button"
                    onClick={() => setSelectedAppForReview(app)}
                    className="px-3.5 py-1.5 bg-aicte-600 hover:bg-aicte-700 text-white text-xs font-semibold rounded-lg shadow-sm transition"
                  >
                    Mark Reviewed ✓
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <ConfirmModal
        isOpen={!!selectedAppForReview}
        title="Mark Application as Scrutiny Reviewed"
        message={`Confirm that you have examined all evidentiary documents and flagged items for ${selectedAppForReview?.institution_name}?`}
        confirmLabel="Verify and Mark Reviewed"
        requiresNotes={true}
        notesPlaceholder="Officer remarks regarding scrutiny review clearance..."
        isLoading={isProcessing}
        onConfirm={handleMarkReviewed}
        onClose={() => setSelectedAppForReview(null)}
      />
    </div>
  );
};

export default ReviewQueuePage;
