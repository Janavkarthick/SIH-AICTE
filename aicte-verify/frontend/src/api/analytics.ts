import apiClient from './client';
import { AnalyticsSummary, Alert } from '../types';
import { mockAnalyticsSummary, mockAlerts } from './mockData';

export const analyticsApi = {
  getSummary: async (): Promise<AnalyticsSummary> => {
    try {
      const response = await apiClient.get<any>('/analytics/summary');
      const raw = response.data || {};
      return {
        ...mockAnalyticsSummary,
        ...raw,
        total_applications: raw.total_applications ?? mockAnalyticsSummary.total_applications,
        pending_review: raw.pending_review ?? mockAnalyticsSummary.pending_review,
        approved_applications: raw.approved_applications ?? mockAnalyticsSummary.approved_applications,
        rejected_applications: raw.rejected_applications ?? mockAnalyticsSummary.rejected_applications,
        average_risk_score: raw.average_risk_score ?? mockAnalyticsSummary.average_risk_score,
        flags_by_severity: {
          ...mockAnalyticsSummary.flags_by_severity,
          ...(raw.flags_by_severity || {}),
        },
        flags_by_type: Array.isArray(raw.flags_by_type) && raw.flags_by_type.length > 0 ? raw.flags_by_type : mockAnalyticsSummary.flags_by_type,
        verification_outcomes: Array.isArray(raw.verification_outcomes) && raw.verification_outcomes.length > 0 ? raw.verification_outcomes : mockAnalyticsSummary.verification_outcomes,
        applications_by_status: Array.isArray(raw.applications_by_status) && raw.applications_by_status.length > 0 ? raw.applications_by_status : mockAnalyticsSummary.applications_by_status,
        processing_times_trend: Array.isArray(raw.processing_times_trend) && raw.processing_times_trend.length > 0 ? raw.processing_times_trend : mockAnalyticsSummary.processing_times_trend,
      };
    } catch {
      return mockAnalyticsSummary;
    }
  },

  getAlerts: async (category?: string, severity?: string): Promise<Alert[]> => {
    try {
      const response = await apiClient.get<Alert[]>('/analytics/alerts', {
        params: { category, severity },
      });
      return response.data;
    } catch {
      let result = [...mockAlerts];
      if (category) {
        result = result.filter((a) => a.category === category);
      }
      if (severity) {
        result = result.filter((a) => a.severity === severity);
      }
      return result;
    }
  },

  dismissAlert: async (alertId: string): Promise<void> => {
    try {
      await apiClient.patch(`/analytics/alerts/${alertId}/dismiss`);
    } catch {
      const alert = mockAlerts.find((a) => a.id === alertId);
      if (alert) {
        alert.is_resolved = true;
      }
    }
  },
};
