import { fetchApi } from './client';
import {
  ClaimCreatePayload,
  ClaimResponse,
  ClaimSummary,
  PaginatedResponse,
  TraceEntry,
  VerdictResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export interface StreamInitResponse {
  claim_id: string;
  stream_url: string;
  status: string;
}

export async function submitClaimSync(payload: ClaimCreatePayload): Promise<ClaimResponse> {
  return fetchApi<ClaimResponse>('/api/v1/claims', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function startStreamingClaim(
  payload: ClaimCreatePayload
): Promise<StreamInitResponse> {
  return fetchApi<StreamInitResponse>('/api/v1/claims/stream', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getClaim(id: string): Promise<ClaimResponse> {
  return fetchApi<ClaimResponse>(`/api/v1/claims/${id}`);
}

export async function listRecentClaims(
  page: number = 1,
  pageSize: number = 50,
  ticker?: string,
  sourceHandle?: string
): Promise<PaginatedResponse<ClaimSummary>> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  if (ticker && ticker !== 'ALL') params.append('ticker', ticker);
  if (sourceHandle) params.append('source_handle', sourceHandle);

  const res = await fetchApi<any>(`/api/v1/claims?${params.toString()}`);
  
  // Normalize response whether backend returns PaginatedResponse or flat array
  if (Array.isArray(res)) {
    return {
      items: res,
      total: res.length,
      page: 1,
      page_size: res.length,
      pages: 1,
    };
  }

  if (res && Array.isArray(res.items)) {
    return res as PaginatedResponse<ClaimSummary>;
  }

  return {
    items: [],
    total: 0,
    page: 1,
    page_size: pageSize,
    pages: 0,
  };
}

/**
 * Connects to live SSE stream for an executing claim.
 * Relays real-time agent trace steps and final verdict.
 */
export function connectTraceStream(
  claimId: string,
  onStep: (step: TraceEntry) => void,
  onCompleted: (verdict: VerdictResponse) => void,
  onError?: (error: any) => void
): () => void {
  const streamUrl = `${API_BASE_URL}/api/v1/claims/${claimId}/stream`;
  const eventSource = new EventSource(streamUrl);

  eventSource.addEventListener('trace_step', (event: MessageEvent) => {
    try {
      const stepData: TraceEntry = JSON.parse(event.data);
      onStep(stepData);
    } catch (e) {
      console.error('Error parsing trace_step SSE event:', e);
    }
  });

  eventSource.addEventListener('completed', (event: MessageEvent) => {
    try {
      const verdictData: VerdictResponse = JSON.parse(event.data);
      onCompleted(verdictData);
      eventSource.close();
    } catch (e) {
      console.error('Error parsing completed SSE event:', e);
    }
  });

  eventSource.addEventListener('error', (event: Event) => {
    if (onError) onError(event);
    eventSource.close();
  });

  return () => {
    eventSource.close();
  };
}
