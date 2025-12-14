import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import {
  AuthState,
  AuthContextType,
  User,
  AuthTokens,
  LoginCredentials,
  RegisterData
} from '../types/auth';
import {
  login as apiLogin,
  register as apiRegister,
  refreshToken as apiRefreshToken,
  logout as apiLogout,
  changePassword as apiChangePassword,
  revokeAllTokens as apiRevokeAllTokens,
  setAuthToken
} from '../services/api';

// Storage keys
const TOKEN_KEY = 'auth_tokens';
const USER_KEY = 'auth_user';

// Initial state
const initialState: AuthState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Action types
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; tokens: AuthTokens } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_LOADING'; payload: boolean };

// Reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, isLoading: true, error: null };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        tokens: action.payload.tokens,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Load stored auth data on mount
  useEffect(() => {
    const loadStoredAuth = () => {
      try {
        const storedTokens = localStorage.getItem(TOKEN_KEY);
        const storedUser = localStorage.getItem(USER_KEY);

        console.log('[AuthContext] Loading stored auth data...');
        console.log('[AuthContext] storedTokens:', storedTokens ? 'exists' : 'null');
        console.log('[AuthContext] storedUser:', storedUser ? 'exists' : 'null');

        if (storedTokens && storedUser) {
          // Validate JSON before parsing
          if (!storedTokens.startsWith('{') || !storedUser.startsWith('{')) {
            console.error('[AuthContext] Invalid stored data format, clearing...');
            throw new Error('Invalid stored data format');
          }
          const tokens: AuthTokens = JSON.parse(storedTokens);
          const user: User = JSON.parse(storedUser);
          // Set the auth token for API requests
          setAuthToken(tokens.access_token);
          dispatch({ type: 'AUTH_SUCCESS', payload: { user, tokens } });
          console.log('[AuthContext] Auth loaded successfully');
        } else {
          console.log('[AuthContext] No stored auth data, setting loading to false');
          dispatch({ type: 'SET_LOADING', payload: false });
        }
      } catch (error) {
        console.error('[AuthContext] Error loading stored auth:', error);
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        setAuthToken(null);
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    loadStoredAuth();
  }, []);

  // Save auth data to storage
  const saveAuthData = (user: User, tokens: AuthTokens) => {
    localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    setAuthToken(tokens.access_token);
  };

  // Clear auth data from storage
  const clearAuthData = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setAuthToken(null);
  };

  // Login function
  const login = useCallback(async (credentials: LoginCredentials) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await apiLogin(credentials);
      saveAuthData(response.user, response.tokens);
      dispatch({ type: 'AUTH_SUCCESS', payload: { user: response.user, tokens: response.tokens } });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Login failed';
      dispatch({ type: 'AUTH_FAILURE', payload: message });
      throw error;
    }
  }, []);

  // Register function
  const register = useCallback(async (data: RegisterData) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await apiRegister(data);
      // 注册成功后直接使用返回的 tokens 登录
      saveAuthData(response.user, response.tokens);
      dispatch({ type: 'AUTH_SUCCESS', payload: { user: response.user, tokens: response.tokens } });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Registration failed';
      dispatch({ type: 'AUTH_FAILURE', payload: message });
      throw error;
    }
  }, []);

  // Logout function
  const logout = useCallback(async () => {
    try {
      // 调用后端登出 API 将 token 加入黑名单
      await apiLogout();
    } catch (error) {
      console.error('[AuthContext] Logout API call failed:', error);
      // 即使 API 调用失败也要清除本地数据
    } finally {
      clearAuthData();
      dispatch({ type: 'LOGOUT' });
    }
  }, []);

  // Refresh token function
  const refreshTokenFn = useCallback(async () => {
    if (!state.tokens?.refresh_token) {
      throw new Error('No refresh token available');
    }
    try {
      const response = await apiRefreshToken(state.tokens.refresh_token);
      // 使用新的 token 结构
      const newTokens = {
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        token_type: response.token_type,
        expires_in: response.expires_in,
      };
      if (state.user) {
        saveAuthData(state.user, newTokens);
        dispatch({ type: 'AUTH_SUCCESS', payload: { user: state.user, tokens: newTokens } });
      }
    } catch (error) {
      await logout();
      throw error;
    }
  }, [state.tokens, state.user, logout]);

  // Change password function
  const changePassword = useCallback(async (oldPassword: string, newPassword: string) => {
    try {
      await apiChangePassword(oldPassword, newPassword);
      // 密码修改成功后,后端会撤销所有 tokens,需要重新登录
      await logout();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Change password failed';
      dispatch({ type: 'AUTH_FAILURE', payload: message });
      throw error;
    }
  }, [logout]);

  // Revoke all tokens function
  const revokeAllTokens = useCallback(async () => {
    try {
      await apiRevokeAllTokens();
      // 撤销所有 tokens 后需要重新登录
      await logout();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Revoke tokens failed';
      dispatch({ type: 'AUTH_FAILURE', payload: message });
      throw error;
    }
  }, [logout]);

  // Clear error function
  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, []);

  // 自动 token 刷新机制
  useEffect(() => {
    if (!state.tokens || !state.isAuthenticated) {
      return;
    }

    // 计算 token 过期时间(提前 5 分钟刷新)
    const refreshBeforeExpiry = 5 * 60 * 1000; // 5 分钟
    const expiryTime = state.tokens.expires_in * 1000; // 转换为毫秒
    const refreshTime = expiryTime - refreshBeforeExpiry;

    console.log('[AuthContext] Setting up auto token refresh');
    console.log('[AuthContext] Token expires in:', expiryTime / 1000, 'seconds');
    console.log('[AuthContext] Will refresh in:', refreshTime / 1000, 'seconds');

    // 设置定时器在 token 即将过期时自动刷新
    const timer = setTimeout(async () => {
      console.log('[AuthContext] Auto refreshing token...');
      try {
        await refreshTokenFn();
        console.log('[AuthContext] Token auto-refreshed successfully');
      } catch (error) {
        console.error('[AuthContext] Auto token refresh failed:', error);
      }
    }, refreshTime);

    return () => {
      console.log('[AuthContext] Clearing auto refresh timer');
      clearTimeout(timer);
    };
  }, [state.tokens, state.isAuthenticated, refreshTokenFn]);

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshToken: refreshTokenFn,
    changePassword,
    revokeAllTokens,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;

