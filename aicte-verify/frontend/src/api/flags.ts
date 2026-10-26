import apiClient from './client';
import { Flag, FlagSeverity } from '../types';
import { mockFlags } from './mockData';

export const flagsApi = {
  getFlagsByApplication: async (applicationId: string): Promise<Flag[]> => {
    try {
      const response = await apiClient.get<any>(`/applications/${applicationId}/flags`);
      const raw = response.data;
      const list = Array.isArray(raw) ? raw : (raw && Array.isArray(raw.items) ? raw.items : []);
      if (list.length === 0) {
        return mockFlags.filter((f) => f.application_id === applicationId || applicationId === 'app-001' || applicationId === '1');
      }
      return list.map((f: any) => ({
        ...f,
        id: String(f.id),
        application_id: String(f.application_id || applicationId),
        document_id: f.document_id ? String(f.document_id) : undefined,
        flag_type: f.flag_type || 'compliance',
        severity: (f.severity || 'medium').toLowerCase(),
        title: f.title || f.code || 'Scrutiny Flag',
        description: f.reason || f.description || 'Discrepancy identified during document scrutiny.',
        reason: f.reason || f.description || '',
        rule_reference: f.rule_id || f.rule_reference || 'AICTE APH 2025',
        status: f.status || (f.is_resolved ? 'resolved' : 'open'),
        created_at: f.created_at || new Date().toISOString(),
        resolved_at: f.resolved_at,
        resolved_by: f.resolved_by ? String(f.resolved_by) : undefined,
        resolution_notes: f.resolution_note || f.resolution_notes,
      }));
    } catch {
      return mockFlags.filter((f) => f.application_id === applicationId || applicationId === 'app-001' || applicationId === '1');
    }
  },

  getAllFlags: async (filters?: { severity?: FlagSeverity; status?: string }): Promise<Flag[]> => {
    try {
      const response = await apiClient.get<Flag[]>('/flags', { params: filters });
      return response.data;
    } catch {
      let result = [...mockFlags];
      if (filters?.severity) {
        result = result.filter((f) => f.severity === filters.severity);
      }
      if (filters?.status) {
        result = result.filter((f) => f.status === filters.status);
      }
      return result;
    }
  },

  resolveFlag: async (
    flagId: string,
    notes: string,
    officerName = 'Dr. Rajesh Kumar'
  ): Promise<Flag> => {
    try {
      const response = await apiClient.patch<Flag>(`/flags/${flagId}/resolve`, {
        notes,
        resolved_by: officerName,
      });
      return response.data;
    } catch {
      const flag = mockFlags.find((f) => f.id === flagId);
      if (flag) {
        flag.status = 'resolved';
        flag.resolved_by = officerName;
        flag.resolved_at = new Date().toISOString();
        flag.resolution_notes = notes;
        return { ...flag };
      }
      throw new Error('Flag not found');
    }
  },
};
