'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { useRouter } from '@/lib/i18n/navigation';
import { sessionStore } from '@/lib/auth/session';
import { authService } from '../services/auth.service';
import { DASHBOARD_ROUTE, AUTH_ROUTES } from '../constants';
import type { AuthUser, LoginCredentials } from '../types';

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    let cancelled = false;

    async function loadSession() {
      if (!sessionStore.get()) {
        setIsLoading(false);
        return;
      }
      try {
        const me = await authService.me();
        if (!cancelled) setUser(me);
      } catch {
        sessionStore.clear();
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void loadSession();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      await authService.login(credentials);
      const me = await authService.me();
      setUser(me);
      router.replace(DASHBOARD_ROUTE);
    },
    [router],
  );

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
    router.replace(AUTH_ROUTES.LOGIN);
  }, [router]);

  const value = useMemo<AuthContextValue>(
    () => ({ user, isAuthenticated: user !== null, isLoading, login, logout }),
    [user, isLoading, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthContext must be used within an AuthProvider');
  return ctx;
}
