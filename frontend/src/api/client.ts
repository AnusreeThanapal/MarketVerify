const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export class ApiError extends Error {
  constructor(public status: number, public message: string, public data?: any) {
    super(message);
    this.name = 'ApiError';
  }
}

let currentAuthToken: string | null = null;

export function setAuthToken(token: string) {
  currentAuthToken = token;
  try {
    localStorage.setItem('marketverify_auth_token', token);
  } catch (e) {
    console.warn('Could not persist token to localStorage', e);
  }
}

export function clearAuthToken() {
  currentAuthToken = null;
  try {
    localStorage.removeItem('marketverify_auth_token');
  } catch (e) {
    console.warn('Could not clear token from localStorage', e);
  }
}

export function getAuthToken(): string | null {
  if (!currentAuthToken) {
    try {
      currentAuthToken = localStorage.getItem('marketverify_auth_token');
    } catch {
      currentAuthToken = null;
    }
  }
  return currentAuthToken;
}

export async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      errorDetail = response.statusText;
    }
    throw new ApiError(response.status, errorDetail);
  }

  return response.json();
}

export const apiClient = {
  get: async <T>(url: string, config?: { params?: Record<string, any> }): Promise<{ data: T }> => {
    let finalUrl = url;
    if (config?.params) {
      const query = new URLSearchParams();
      Object.entries(config.params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') {
          query.append(k, String(v));
        }
      });
      const qs = query.toString();
      if (qs) {
        finalUrl += (url.includes('?') ? '&' : '?') + qs;
      }
    }
    const data = await fetchApi<T>(finalUrl, { method: 'GET' });
    return { data };
  },
  post: async <T>(url: string, body?: any): Promise<{ data: T }> => {
    const data = await fetchApi<T>(url, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
    return { data };
  },
};
