// Authentication Types

export interface User {
  id: number;
  email: string;
  student_id?: string;
  name?: string;
  role: 'student' | 'teacher' | 'admin';
  is_active: boolean;
  last_login: string | null;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  student_id: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
  message: string;
}

export interface RegisterResponse {
  user: User;
  tokens: AuthTokens;
  message: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

export interface ChangePasswordResponse {
  message: string;
}

export interface RevokeAllTokensResponse {
  message: string;
  revoked_count: number;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  changePassword: (oldPassword: string, newPassword: string) => Promise<void>;
  revokeAllTokens: () => Promise<void>;
  clearError: () => void;
}

