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
      await apiRegister(data);
      // After registration, automatically log in
      await login({ email: data.email, password: data.password });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Registration failed';
      dispatch({ type: 'AUTH_FAILURE', payload: message });
      throw error;
    }
  }, [login]);

  // Logout function
  const logout = useCallback(() => {
    clearAuthData();
    dispatch({ type: 'LOGOUT' });
  }, []);

  // Refresh token function
  const refreshTokenFn = useCallback(async () => {
    if (!state.tokens?.refresh_token) {
      throw new Error('No refresh token available');
    }
    try {
      const response = await apiRefreshToken(state.tokens.refresh_token);
      if (state.user) {
        saveAuthData(state.user, response);
        dispatch({ type: 'AUTH_SUCCESS', payload: { user: state.user, tokens: response } });
      }
    } catch (error) {
      logout();
      throw error;
    }
  }, [state.tokens, state.user, logout]);

  // Clear error function
  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, []);

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshToken: refreshTokenFn,
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

