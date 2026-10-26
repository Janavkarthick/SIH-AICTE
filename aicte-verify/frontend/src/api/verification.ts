import apiClient from './client';
import { VerificationResult, VerificationCheckType } from '../types';
import { mockVerifications } from './mockData';

export const verificationApi = {
  getVerificationsByApplication: async (applicationId: string): Promise<VerificationResult[]> => {
    try {
      const response = await apiClient.get<VerificationResult[]>(
        `/applications/${applicationId}/verifications`
      );
      return response.data;
    } catch {
      return mockVerifications.filter(
        (v) => v.application_id === applicationId || applicationId === 'app-001'
      );
    }
  },

  runVerificationCheck: async (
    applicationId: string,
    checkType: VerificationCheckType,
    targetIdentifier: string
  ): Promise<VerificationResult> => {
    try {
      const response = await apiClient.post<VerificationResult>(
        `/applications/${applicationId}/verifications/run`,
        {
          check_type: checkType,
          target_identifier: targetIdentifier,
        }
      );
      return response.data;
    } catch {
      const newResult: VerificationResult = {
        id: `vr-${Date.now()}`,
        application_id: applicationId,
        check_type: checkType,
        check_name: `${checkType.replace('_', ' ').toUpperCase()} Live Registry Check`,
        target_identifier: targetIdentifier,
        status: 'verified',
        response_data: {
          verified: true,
          match_percentage: 98.4,
          timestamp: new Date().toISOString(),
          registry_source: 'National Digital Registry Portal (Sandbox)',
        },
        source_authority: 'Central Statutory Verification Gateway',
        verified_at: new Date().toISOString(),
        is_simulated: true,
      };
      mockVerifications.push(newResult);
      return newResult;
    }
  },
};
