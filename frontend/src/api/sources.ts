import { fetchApi } from './client';
import { SourceTrustHistory } from '../types/api';

export async function getSourceTrustHistory(
  sourceHandle: string
): Promise<SourceTrustHistory> {
  const cleanHandle = encodeURIComponent(sourceHandle);
  return fetchApi<SourceTrustHistory>(`/api/v1/sources/${cleanHandle}/trust-history`);
}
