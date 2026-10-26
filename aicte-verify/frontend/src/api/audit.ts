import apiClient from './client';
import { AuditEntry } from '../types';
import { mockAuditEntries } from './mockData';

export interface ChainVerificationResult {
  is_valid: boolean;
  total_blocks: number;
  last_verified_at: string;
  tampered_block_index?: number;
  error_message?: string;
}

export const auditApi = {
  getAuditLogs: async (filters?: {
    actor?: string;
    action?: string;
    from_date?: string;
  }): Promise<AuditEntry[]> => {
    try {
      const response = await apiClient.get<any>('/audit/logs', { params: filters });
      const rawData = response.data;
      const rawList: any[] = Array.isArray(rawData)
        ? rawData
        : Array.isArray(rawData?.items)
        ? rawData.items
        : [];

      if (rawList.length > 0) {
        return rawList.map((e: any, idx: number) => ({
          id: String(e.id ?? `aud-${idx}`),
          timestamp: e.timestamp ? new Date(e.timestamp).toISOString() : new Date().toISOString(),
          actor_id: String(e.actor_id ?? 'system'),
          actor_name: e.actor_name || e.actor_username || 'Authorized Officer',
          actor_role: e.actor_role || (e.actor_username === 'admin' ? 'Central Admin' : e.actor_username?.startsWith('ro') ? 'Regional Officer' : 'System'),
          action: e.action || 'INSPECT',
          entity_type: e.entity_type || (e.rule_check ? 'StatutoryRule' : 'AuditRecord'),
          entity_id: e.entity_id || `#${e.id || idx + 1}`,
          details: typeof e.details === 'string' ? e.details : typeof e.details_json === 'string' ? e.details_json : JSON.stringify(e.details || {}),
          prev_hash: e.prev_hash || e.previous_hash || '0'.repeat(64),
          curr_hash: e.curr_hash || e.entry_hash || '0'.repeat(64),
          ip_address: e.ip_address || '127.0.0.1',
          is_tampered: e.is_tampered || false,
        }));
      }

      // If empty backend list, fall back to mock entries
      let entries = [...mockAuditEntries];
      if (filters?.actor) {
        entries = entries.filter((e) =>
          e.actor_name.toLowerCase().includes(filters.actor!.toLowerCase())
        );
      }
      if (filters?.action) {
        entries = entries.filter((e) => e.action === filters.action);
      }
      return entries;
    } catch {
      let entries = [...mockAuditEntries];
      if (filters?.actor) {
        entries = entries.filter((e) =>
          e.actor_name.toLowerCase().includes(filters.actor!.toLowerCase())
        );
      }
      if (filters?.action) {
        entries = entries.filter((e) => e.action === filters.action);
      }
      return entries;
    }
  },

  logAction: async (action: string, entityType: string, entityId: string, details: string): Promise<AuditEntry> => {
    try {
      const response = await apiClient.post<any>('/audit/log', {
        action,
        entity_type: entityType,
        entity_id: entityId,
        details,
      });
      return response.data;
    } catch {
      const lastEntry = mockAuditEntries[mockAuditEntries.length - 1];
      const newEntry: AuditEntry = {
        id: `aud-${Date.now()}`,
        timestamp: new Date().toISOString(),
        actor_id: 'current_user',
        actor_name: 'Authorized User',
        actor_role: 'officer',
        action,
        entity_type: entityType,
        entity_id: entityId,
        details,
        prev_hash: lastEntry ? lastEntry.curr_hash : '0000000000000000',
        curr_hash: Math.random().toString(16).substring(2, 18) + Math.random().toString(16).substring(2, 18),
        ip_address: '127.0.0.1',
        is_tampered: false,
      };
      mockAuditEntries.push(newEntry);
      return newEntry;
    }
  },

  verifyChainIntegrity: async (): Promise<ChainVerificationResult> => {
    try {
      const response = await apiClient.get<any>('/audit/verify-chain');
      const data = response.data;
      const isValid = data.valid ?? data.is_valid ?? true;
      const total = data.verified_count ?? data.total_blocks ?? 0;
      return {
        is_valid: isValid,
        total_blocks: total,
        last_verified_at: new Date().toISOString(),
        tampered_block_index: data.tampered_entry_id ?? data.tampered_block_index,
        error_message: isValid ? undefined : (data.reason || data.error_message || 'Cryptographic hash mismatch detected!'),
      };
    } catch {
      // Check local mock chain integrity
      let isValid = true;
      let tamperedIdx: number | undefined;

      for (let i = 1; i < mockAuditEntries.length; i++) {
        if (mockAuditEntries[i].prev_hash !== mockAuditEntries[i - 1].curr_hash || mockAuditEntries[i].is_tampered) {
          isValid = false;
          tamperedIdx = i;
          break;
        }
      }

      return {
        is_valid: isValid,
        total_blocks: mockAuditEntries.length,
        last_verified_at: new Date().toISOString(),
        tampered_block_index: tamperedIdx,
        error_message: isValid
          ? undefined
          : `Cryptographic hash chain broken at block #${tamperedIdx}: PrevHash mismatch detected!`,
      };
    }
  },

  simulateTamper: async (entryIndex = 2): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await apiClient.post<any>('/audit/simulate-tamper');
      return {
        success: true,
        message: response.data?.message || 'Simulated unauthorized tamper injected into ledger. Chain verification will now detect violation!',
      };
    } catch {
      if (mockAuditEntries[entryIndex]) {
        mockAuditEntries[entryIndex].is_tampered = true;
        mockAuditEntries[entryIndex].details =
          '[TAMPERED SIMULATION]: Details altered without hash recomputation!';
        mockAuditEntries[entryIndex].curr_hash = 'ffffffffffffffffdeadbeef12345678';
        return {
          success: true,
          message: `Simulated unauthorized tamper at entry index #${entryIndex} (${mockAuditEntries[entryIndex].id}). Chain integrity verification will now fail!`,
        };
      }
      return { success: false, message: 'Invalid index to tamper' };
    }
  },

  resetTamper: async (): Promise<void> => {
    try {
      await apiClient.post('/audit/reset-tamper');
    } catch {
      // ignore
    }
    // Also reset local mock hashes
    for (let i = 0; i < mockAuditEntries.length; i++) {
      mockAuditEntries[i].is_tampered = false;
    }
    if (mockAuditEntries[2]) {
      mockAuditEntries[2].curr_hash =
        '2c4b6a8e0f1d3e5a7b9c1d3e5f7a9b0c2d4e6f8a0b1c2d3e4f5a6b7c8d9e0f1a';
      mockAuditEntries[2].details =
        'Officer resolved flag SEC-PII-005: Auto-redaction verified for Aadhaar data.';
    }
  },
};
