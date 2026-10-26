import apiClient from './client';
import { ComplianceResult, CapacityCalculation } from '../types';
import { mockComplianceResults, mockCapacityCalculation } from './mockData';

export const complianceApi = {
  getComplianceByApplication: async (applicationId: string): Promise<ComplianceResult[]> => {
    try {
      const response = await apiClient.get<ComplianceResult[]>(
        `/applications/${applicationId}/compliance`
      );
      return response.data;
    } catch {
      return mockComplianceResults.filter(
        (c) => c.application_id === applicationId || applicationId === 'app-001'
      );
    }
  },

  getCapacityCalculation: async (applicationId: string): Promise<CapacityCalculation> => {
    try {
      const response = await apiClient.get<CapacityCalculation>(
        `/applications/${applicationId}/capacity`
      );
      return response.data;
    } catch {
      return mockCapacityCalculation;
    }
  },

  recalculateCapacity: async (
    applicationId: string,
    params: { built_up_area_sqm: number; faculty_count: number; applied_intake: number }
  ): Promise<CapacityCalculation> => {
    try {
      const response = await apiClient.post<CapacityCalculation>(
        `/applications/${applicationId}/capacity/calculate`,
        params
      );
      return response.data;
    } catch {
      const maxInfra = Math.floor(params.built_up_area_sqm / 8.5);
      const maxFac = params.faculty_count * 20;
      const approved = Math.min(params.applied_intake, maxInfra, maxFac);
      const bottleneck =
        maxInfra < maxFac ? 'infrastructure' : maxFac < maxInfra ? 'faculty' : 'balanced';

      return {
        built_up_area_sqm: params.built_up_area_sqm,
        required_sqm_per_student: 8.5,
        faculty_count: params.faculty_count,
        faculty_ratio_required: 20,
        max_capacity_infrastructure: maxInfra,
        max_capacity_faculty: maxFac,
        bottleneck_factor: bottleneck,
        applied_intake: params.applied_intake,
        suggested_approved_intake: approved,
        explanation: `Calculated capacity dynamically: Infrastructure ceiling is ${maxInfra} students, Faculty ceiling is ${maxFac} students. Constraint factor: ${bottleneck.toUpperCase()}.`,
      };
    }
  },
};
