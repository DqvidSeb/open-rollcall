export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

/** Mirrors backend `UserRead` (app/schemas/auth.py). */
export interface AuthUser {
  id: string;
  fullName: string;
  email: string | null;
  isActive: boolean;
  isSuperuser: boolean;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
