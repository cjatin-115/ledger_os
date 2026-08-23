import { API_BASE_URL } from '../constants';
import type { ApiError } from '../types/api';
import { getAccessToken, getRefreshToken, setTokens } from './tokenStorage';

export class ApiClientError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
  auth?: boolean;
  formData?: FormData;
  retry?: boolean;
};

async function parseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as ApiError | { detail: unknown };
    if (typeof data.detail === 'string') return data.detail;
    return `Request failed (${response.status})`;
  } catch {
    return `Request failed (${response.status})`;
  }
}

const DEFAULT_PROD_URL = 'https://ledgeros-api.onrender.com';
let cachedBaseUrl: string | null = null;

export async function getEffectiveBaseUrl(): Promise<string> {
  if (cachedBaseUrl) return cachedBaseUrl;

  const candidates = Array.from(
    new Set([API_BASE_URL, DEFAULT_PROD_URL].filter(Boolean)),
  );

  for (const candidate of candidates) {
    const clean = candidate.replace(/\/+$/, '');
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1500);
      const res = await fetch(`${clean}/api/v1/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        cachedBaseUrl = clean;
        return clean;
      }
    } catch {
      // Ignore network errors and test next candidate
    }
  }

  cachedBaseUrl = DEFAULT_PROD_URL.replace(/\/+$/, '');
  return cachedBaseUrl;
}

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = await getRefreshToken();
  if (!refreshToken) return false;

  const baseUrl = await getEffectiveBaseUrl();
  const response = await fetch(`${baseUrl}/api/v1/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) return false;

  const data = (await response.json()) as {
    access_token: string;
    refresh_token: string;
  };
  await setTokens(data.access_token, data.refresh_token);
  return true;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = 'GET', body, auth = true, formData, retry = true } = options;

  const headers: Record<string, string> = {};

  if (!formData) {
    headers['Content-Type'] = 'application/json';
  }

  if (auth) {
    const token = await getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const baseUrl = await getEffectiveBaseUrl();
  const response = await fetch(`${baseUrl}/api/v1${path}`, {
    method,
    headers,
    body: formData ?? (body !== undefined ? JSON.stringify(body) : undefined),
  });

  if (response.status === 401 && auth && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return apiRequest<T>(path, { ...options, retry: false });
    }
  }

  if (!response.ok) {
    throw new ApiClientError(await parseError(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function checkBackendHealth(): Promise<boolean> {
  const baseUrl = await getEffectiveBaseUrl();
  try {
    const response = await fetch(`${baseUrl}/api/v1/health`);
    if (response.ok) return true;
    const fallbackRes = await fetch(`${baseUrl}/health`);
    return fallbackRes.ok;
  } catch {
    return false;
  }
}
