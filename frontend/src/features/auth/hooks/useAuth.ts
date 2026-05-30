// useAuth — stub, to be implemented
// Will manage login, logout, session refresh, and global auth state
'use client';

import type { AuthState } from '../types';

export function useAuth(): AuthState {
  // TODO: implement with context or zustand store
  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
  };
}
