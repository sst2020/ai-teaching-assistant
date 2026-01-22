// Authentication Types

export interface User {
  id: number;
  student_id: string;
  name?: string;
  avatar_url?: string;
  role: 'student' | 'teacher' | 'admin';
  is_active: boolean;
  last_login: string | null;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  student_id: string;
  password: string;
}

export interface RegisterData {
  student_id: string;
  password: string;
  name: string;
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

export interface UpdateProfileRequest {
  name?: string;
}

export interface UpdateProfileResponse {
  user: User;
  message: string;
}

export interface AvatarUploadResponse {
  avatar_url: string;
  message: string;
}

export interface DeleteAccountRequest {
  password: string;
}

export interface DeleteAccountResponse {
  message: string;
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
  updateProfile: (name: string) => Promise<void>;
  uploadAvatar: (file: File) => Promise<string>;
  deleteAccount: (password: string) => Promise<void>;
  clearError: () => void;
}

