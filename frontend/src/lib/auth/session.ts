// Session storage — JWT pair persisted in cookies so the auth guard in
// `proxy.ts` (server-side) can read them, while client code can still
// attach the access token to API requests.

import type { AuthTokens } from '@/features/auth/types';

export const ACCESS_TOKEN_COOKIE = 'rc_access_token';
export const REFRESH_TOKEN_COOKIE = 'rc_refresh_token';

const COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 7; // 7 days

function setCookie(name: string, value: string, maxAgeSeconds: number): void {
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAgeSeconds}; samesite=lax`;
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function deleteCookie(name: string): void {
  document.cookie = `${name}=; path=/; max-age=0; samesite=lax`;
}

export const sessionStore = {
  get(): AuthTokens | null {
    if (typeof document === 'undefined') return null;

    const accessToken = getCookie(ACCESS_TOKEN_COOKIE);
    const refreshToken = getCookie(REFRESH_TOKEN_COOKIE);
    if (!accessToken || !refreshToken) return null;

    return { accessToken, refreshToken, expiresIn: 0 };
  },

  set(tokens: AuthTokens): void {
    if (typeof document === 'undefined') return;

    setCookie(ACCESS_TOKEN_COOKIE, tokens.accessToken, COOKIE_MAX_AGE_SECONDS);
    setCookie(REFRESH_TOKEN_COOKIE, tokens.refreshToken, COOKIE_MAX_AGE_SECONDS);
  },

  clear(): void {
    if (typeof document === 'undefined') return;

    deleteCookie(ACCESS_TOKEN_COOKIE);
    deleteCookie(REFRESH_TOKEN_COOKIE);
  },
};
