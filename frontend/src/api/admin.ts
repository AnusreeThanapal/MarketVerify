import { apiClient } from './client';
import {
  AdminDataListResponse,
  UserProfile,
  RawClaimRecord,
  RawAgentRunRecord,
  RawQdrantDocRecord,
} from '../types/api';

export async function fetchRawUsers(
  skip = 0,
  limit = 20,
  search?: string
): Promise<AdminDataListResponse<UserProfile>> {
  const res = await apiClient.get<AdminDataListResponse<UserProfile>>('/api/v1/admin/data/users', {
    params: { skip, limit, search },
  });
  return res.data;
}

export async function fetchRawClaims(
  skip = 0,
  limit = 20,
  ticker?: string,
  search?: string
): Promise<AdminDataListResponse<RawClaimRecord>> {
  const res = await apiClient.get<AdminDataListResponse<RawClaimRecord>>('/api/v1/admin/data/claims', {
    params: { skip, limit, ticker, search },
  });
  return res.data;
}

export async function fetchRawAgentRuns(
  skip = 0,
  limit = 20,
  claimId?: string
): Promise<AdminDataListResponse<RawAgentRunRecord>> {
  const res = await apiClient.get<AdminDataListResponse<RawAgentRunRecord>>('/api/v1/admin/data/agent-runs', {
    params: { skip, limit, claim_id: claimId },
  });
  return res.data;
}

export async function fetchRawTrustDocs(
  limit = 50,
  search?: string
): Promise<{ collection: string; total: number; items: RawQdrantDocRecord[] }> {
  const res = await apiClient.get<{ collection: string; total: number; items: RawQdrantDocRecord[] }>(
    '/api/v1/admin/data/trust-tier-docs',
    {
      params: { limit, search },
    }
  );
  return res.data;
}

export async function fetchRawFilingDocs(
  limit = 50,
  search?: string
): Promise<{ collection: string; total: number; items: RawQdrantDocRecord[] }> {
  const res = await apiClient.get<{ collection: string; total: number; items: RawQdrantDocRecord[] }>(
    '/api/v1/admin/data/filing-docs',
    {
      params: { limit, search },
    }
  );
  return res.data;
}

export async function fetchRawSentimentDocs(
  limit = 50,
  search?: string
): Promise<{ collection: string; total: number; items: RawQdrantDocRecord[] }> {
  const res = await apiClient.get<{ collection: string; total: number; items: RawQdrantDocRecord[] }>(
    '/api/v1/admin/data/sentiment-docs',
    {
      params: { limit, search },
    }
  );
  return res.data;
}
