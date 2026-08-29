import { apiClient, setAuthToken, clearAuthToken } from './client';
import { LoginPayload, TokenResponse, UserProfile, UserRole } from '../types/api';

export async function loginUser(payload: LoginPayload): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>('/api/v1/auth/login', payload);
  setAuthToken(res.data.access_token);
  return res.data;
}

export async function demoLoginUser(role: UserRole): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>('/api/v1/auth/demo-login', { role });
  setAuthToken(res.data.access_token);
  return res.data;
}

export async function getCurrentUser(): Promise<UserProfile> {
  const res = await apiClient.get<UserProfile>('/api/v1/auth/me');
  return res.data;
}

export function logoutUser(): void {
  clearAuthToken();
}
