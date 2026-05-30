// Auth service — stub, to be implemented
import type { LoginCredentials, RegisterCredentials, AuthTokens, AuthUser } from '../types';

export const authService = {
  login: async (_credentials: LoginCredentials): Promise<AuthTokens> => {
    // TODO: POST /api/v1/auth/login
    throw new Error('Not implemented');
  },

  register: async (_data: RegisterCredentials): Promise<AuthUser> => {
    // TODO: POST /api/v1/auth/register
    throw new Error('Not implemented');
  },

  logout: async (): Promise<void> => {
    // TODO: POST /api/v1/auth/logout
    throw new Error('Not implemented');
  },

  refreshToken: async (_refreshToken: string): Promise<AuthTokens> => {
    // TODO: POST /api/v1/auth/refresh
    throw new Error('Not implemented');
  },

  me: async (): Promise<AuthUser> => {
    // TODO: GET /api/v1/auth/me
    throw new Error('Not implemented');
  },
};
