import { apiClient } from '@/lib/api/client';
import { ENDPOINTS } from '@/lib/api/endpoints';
import { sessionStore } from '@/lib/auth/session';
import type { AuthTokens, AuthUser, LoginCredentials } from '../types';

/** Raw shapes returned by the FastAPI backend. */
interface TokenResponseDto {
  access_token: string;
  refresh_token: string;
}

interface UserReadDto {
  id: string;
  full_name: string;
  email: string | null;
  is_active: boolean;
  is_superuser: boolean;
}

function mapTokens(dto: TokenResponseDto): AuthTokens {
  return {
    accessToken: dto.access_token,
    refreshToken: dto.refresh_token,
    expiresIn: 0,
  };
}

function mapUser(dto: UserReadDto): AuthUser {
  return {
    id: dto.id,
    fullName: dto.full_name,
    email: dto.email,
    isActive: dto.is_active,
    isSuperuser: dto.is_superuser,
  };
}

export const authService = {
  /** POST /api/v1/auth/login — backend expects OAuth2 form-data (username/password). */
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const body = new URLSearchParams({
      username: credentials.email,
      password: credentials.password,
    });

    const dto = await apiClient.post<TokenResponseDto>(ENDPOINTS.AUTH_LOGIN, body, {
      skipAuth: true,
    });
    const tokens = mapTokens(dto);
    sessionStore.set(tokens);
    return tokens;
  },

  /** Local-only: clears the session cookies. No backend session to invalidate. */
  logout: (): void => {
    sessionStore.clear();
  },

  /** GET /api/v1/auth/me — current authenticated user. */
  me: async (): Promise<AuthUser> => {
    const dto = await apiClient.get<UserReadDto>(ENDPOINTS.AUTH_ME);
    return mapUser(dto);
  },
};
