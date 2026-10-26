import apiClient from './client';
import { GraphData, GraphEntity, GraphRelation } from '../types';
import { mockGraphData } from './mockData';

export const graphApi = {
  getGraphData: async (applicationId?: string): Promise<GraphData> => {
    try {
      const response = await apiClient.get<any>('/graph', {
        params: { application_id: applicationId },
      });
      const data = response.data;
      if (data && Array.isArray(data.elements) && data.elements.length > 0) {
        const nodes: GraphEntity[] = [];
        const edges: GraphRelation[] = [];
        for (const el of data.elements) {
          const item = el.data || el;
          if (item.source && item.target) {
            edges.push({
              id: String(item.id),
              source: String(item.source),
              target: String(item.target),
              type: item.type || item.label || 'connected_to',
              label: item.label || 'connected_to',
              flagged: Boolean(item.is_flagged || item.flagged),
              flag_reason: item.flag_reason || '',
              confidence: item.confidence ?? 0.95,
            });
          } else {
            nodes.push({
              id: String(item.id),
              label: item.name || item.label || item.id,
              type: item.type || 'institution',
              flagged: Boolean(item.is_flagged || item.flagged),
              flag_reasons: item.flag_reason ? [item.flag_reason] : [],
              properties: item.metadata || {},
            });
          }
        }
        return { nodes, edges };
      }
      if (data && Array.isArray(data.nodes) && Array.isArray(data.edges)) {
        return data;
      }
      return mockGraphData;
    } catch {
      return mockGraphData;
    }
  },
};
