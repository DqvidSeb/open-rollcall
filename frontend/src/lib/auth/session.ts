// Session helpers — stub, to be implemented
// Will handle token storage, retrieval, and expiry checks

import type { AuthTokens } from '@/features/auth/types';

const STORAGE_KEY = 'orc_tokens';

export const sessionStore = {
  get: (): AuthTokens | null => {
    // TODO: read from httpOnly cookie or secure storage
    if (typeof window === 'undefined') return null;
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as AuthTokens;
    } catch {
      return null;
    }
  },

  set: (_tokens: AuthTokens): void => {
    // TODO: prefer httpOnly cookie via /api/auth route
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(_tokens));
    }
  },

  clear: (): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY);
    }
  },

  isExpired: (_tokens: AuthTokens): boolean => {
    // TODO: implement JWT decode check
    return false;
  },
};
