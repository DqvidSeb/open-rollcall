// HTTP API client — wraps fetch with: base URL, auth headers, error normalization.

import { sessionStore } from '@/lib/auth/session';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
  /** Skip attaching the Authorization header (e.g. for /auth/login). */
  skipAuth?: boolean;
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: unknown };
    if (typeof data.detail === 'string') return data.detail;
  } catch {
    // Response had no JSON body — fall back below.
  }
  return response.statusText || `Request failed with status ${response.status}`;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { params, skipAuth, headers, body, ...init } = options;

  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) url.searchParams.set(key, String(value));
    });
  }

  const requestHeaders = new Headers(headers);
  const isFormBody = body instanceof URLSearchParams;
  if (!isFormBody && !requestHeaders.has('Content-Type')) {
    requestHeaders.set('Content-Type', 'application/json');
  }

  if (!skipAuth) {
    const tokens = sessionStore.get();
    if (tokens) requestHeaders.set('Authorization', `Bearer ${tokens.accessToken}`);
  }

  const response = await fetch(url.toString(), { ...init, headers: requestHeaders, body });

  if (!response.ok) {
    throw new ApiError(response.status, await readErrorMessage(response));
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: 'GET' }),

  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, {
      ...options,
      method: 'POST',
      body: body instanceof URLSearchParams ? body : JSON.stringify(body),
    }),

  patch: <T>(path: string, body: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: 'PATCH', body: JSON.stringify(body) }),

  delete: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: 'DELETE' }),
};
