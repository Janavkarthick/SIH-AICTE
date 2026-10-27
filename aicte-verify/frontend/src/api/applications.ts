import apiClient, { setOfflineFallback } from './client';
import {
  Application,
  ApplicationStatus,
  ValidationReport,
  TimelineEvent,
  ResubmissionDiff
} from '../types';
import {
  mockApplications,
  mockValidationReport,
  mockTimelineEvents,
  mockResubmissionDiff
} from './mockData';

export const applicationsApi = {
  getApplications: async (filters?: {
    status?: string;
    risk_level?: string;
    search?: string;
    region?: string;
  }): Promise<Application[]> => {
    try {
      const response = await apiClient.get<any>('/applications', { params: filters });
      const raw = response.data;
      const list = Array.isArray(raw) ? raw : (raw && Array.isArray(raw.items) ? raw.items : []);
      return list.map((item: any) => ({
        ...item,
        id: String(item.id),
        application_number: item.application_number || `AICTE/RO/2025/${String(item.id).padStart(4, '0')}`,
        institution_name: item.institution_name || (item.institution?.name) || `AICTE Institution #${item.institution_id || item.id}`,
        institution_type: item.institution_type || 'Technical Campus',
        academic_year: item.academic_year || '2025-2026',
        status: item.status || 'submitted',
        risk_level: (item.risk_level || 'low').toLowerCase(),
        risk_score: item.risk_score ?? 25,
        region: item.region || (item.institution?.region) || 'Southern',
        state: item.state || (item.institution?.state) || 'Tamil Nadu',
        applied_intake: item.applied_intake ?? item.intake_applied ?? 300,
        approved_intake: item.approved_intake ?? item.current_intake ?? 300,
        total_flags_count: item.total_flags_count ?? (item.flags ? item.flags.length : 0),
        critical_flags_count: item.critical_flags_count ?? (item.flags ? item.flags.filter((f: any) => (f.severity || '').toLowerCase() === 'critical').length : 0),
        submission_version: item.submission_version || 1,
        created_at: item.created_at || new Date().toISOString(),
        updated_at: item.updated_at || new Date().toISOString(),
      }));
    } catch {
      setOfflineFallback(true);
      let filtered = [...mockApplications];
      if (filters?.status) {
        filtered = filtered.filter((a) => a.status === filters.status);
      }
      if (filters?.risk_level) {
        filtered = filtered.filter((a) => a.risk_level === filters.risk_level);
      }
      if (filters?.region) {
        filtered = filtered.filter((a) => a.region.toLowerCase().includes(filters.region!.toLowerCase()));
      }
      if (filters?.search) {
        const q = filters.search.toLowerCase();
        filtered = filtered.filter(
          (a) =>
            a.institution_name.toLowerCase().includes(q) ||
            a.application_number.toLowerCase().includes(q) ||
            a.state.toLowerCase().includes(q)
        );
      }
      return filtered;
    }
  },

  getApplicationById: async (id: string): Promise<Application> => {
    try {
      const response = await apiClient.get<any>(`/applications/${id}`);
      const item = response.data;
      let rb = item.risk_breakdown;
      if (typeof rb === 'string') {
        try {
          rb = JSON.parse(rb);
        } catch {
          rb = null;
        }
      }
      const safeRiskBreakdown = {
        composite_score: rb?.composite_score ?? rb?.risk_score ?? item.risk_score ?? 25,
        land_risk: rb?.land_risk ?? 15,
        faculty_risk: rb?.faculty_risk ?? 20,
        forensic_risk: rb?.forensic_risk ?? 10,
        regulatory_risk: rb?.regulatory_risk ?? 15,
        primary_concerns: Array.isArray(rb?.primary_concerns)
          ? rb.primary_concerns
          : (Array.isArray(rb?.contributions) ? rb.contributions.map((c: any) => c.title || c.flag_code) : ['Cross-institution faculty duplicity check pending']),
      };

      return {
        ...item,
        id: String(item.id),
        application_number: item.application_number || `AICTE/RO/2025/${String(item.id).padStart(4, '0')}`,
        institution_name: item.institution_name || (item.institution?.name) || `AICTE Institution #${item.institution_id || item.id}`,
        institution_type: item.institution_type || 'Technical Campus',
        academic_year: item.academic_year || '2025-2026',
        status: item.status || 'submitted',
        risk_level: (item.risk_level || 'low').toLowerCase(),
        risk_score: item.risk_score ?? 25,
        risk_breakdown: safeRiskBreakdown,
        region: item.region || (item.institution?.region) || 'Southern',
        state: item.state || (item.institution?.state) || 'Tamil Nadu',
        applied_intake: item.applied_intake ?? item.intake_applied ?? 300,
        approved_intake: item.approved_intake ?? item.current_intake ?? 300,
        total_flags_count: item.total_flags_count ?? (item.flags ? item.flags.length : 0),
        critical_flags_count: item.critical_flags_count ?? (item.flags ? item.flags.filter((f: any) => (f.severity || '').toLowerCase() === 'critical').length : 0),
        submission_version: item.submission_version || 1,
        created_at: item.created_at || new Date().toISOString(),
        updated_at: item.updated_at || new Date().toISOString(),
      };
    } catch {
      const app = mockApplications.find((a) => a.id === id || a.application_number === id);
      if (app) return app;
      return mockApplications[0];
    }
  },

  createApplication: async (payload: Partial<Application>): Promise<Application> => {
    try {
      const response = await apiClient.post<Application>('/applications', payload);
      return response.data;
    } catch {
      const newApp: Application = {
        id: `app-${Date.now()}`,
        application_number: `AICTE/SRO/2025/${Math.floor(1000 + Math.random() * 9000)}`,
        institution_name: payload.institution_name || 'New Technical Institute',
        institution_type: payload.institution_type || 'Private Self-Financing',
        academic_year: '2025-2026',
        status: 'draft',
        risk_level: 'low',
        risk_score: 15,
        region: payload.region || 'Southern',
        state: payload.state || 'Tamil Nadu',
        applied_intake: payload.applied_intake || 300,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        total_flags_count: 0,
        critical_flags_count: 0,
        submission_version: 1,
        submitted_by: payload.submitted_by || 'Institute Administrator',
        summary: payload.summary || 'Newly submitted application pending scrutiny review.'
      };
      mockApplications.unshift(newApp);
      return newApp;
    }
  },

  updateStatus: async (
    id: string,
    status: ApplicationStatus,
    reason?: string
  ): Promise<Application> => {
    try {
      const response = await apiClient.put<Application>('/applications/' + id + '/status', {
        status,
        reason,
      });
      return response.data;
    } catch (err: any) {
      if (err.response?.data?.detail) {
        throw new Error(err.response.data.detail);
      }
      if (err.message && !err.message.includes('Network Error')) {
        throw err;
      }
      const app = mockApplications.find((a) => a.id === id);
      if (app) {
        app.status = status;
        app.updated_at = new Date().toISOString();
        mockTimelineEvents.unshift({
          id: 'evt-' + Date.now(),
          application_id: id,
          timestamp: new Date().toISOString(),
          title: 'Status Changed to ' + status.replace('_', ' ').toUpperCase(),
          description: reason || 'Application updated by officer.',
          actor: 'Authorized Officer',
          type: 'status_change'
        });
        return { ...app };
      }
      throw new Error('Application status update failed');
    }
  },

  getValidationReport: async (id: string): Promise<ValidationReport> => {
    try {
      const response = await apiClient.get<any>(`/applications/${id}/validation`);
      const raw = response.data;
      return {
        ...mockValidationReport,
        ...raw,
        application_id: String(id),
        missing_mandatory_documents: Array.isArray(raw?.missing_mandatory_documents)
          ? raw.missing_mandatory_documents
          : (Array.isArray(raw?.missing_documents) ? raw.missing_documents : mockValidationReport.missing_mandatory_documents),
        inconsistencies: Array.isArray(raw?.inconsistencies)
          ? raw.inconsistencies
          : mockValidationReport.inconsistencies,
        recommendations: Array.isArray(raw?.recommendations)
          ? raw.recommendations
          : mockValidationReport.recommendations,
      };
    } catch {
      return { ...mockValidationReport, application_id: id };
    }
  },


  getTimeline: async (id: string): Promise<TimelineEvent[]> => {
    try {
      const response = await apiClient.get<TimelineEvent[]>(`/applications/${id}/timeline`);
      return response.data;
    } catch {
      return mockTimelineEvents.filter((e) => e.application_id === id || id === 'app-001');
    }
  },

  getResubmissionDiff: async (id: string): Promise<ResubmissionDiff> => {
    try {
      const response = await apiClient.get<ResubmissionDiff>(`/applications/${id}/diff`);
      return response.data;
    } catch {
      return mockResubmissionDiff;
    }
  }
};
