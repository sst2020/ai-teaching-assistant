import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// Mock i18n
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (str) => str,
    i18n: {
      changeLanguage: () => new Promise(() => {}),
    },
  }),
  initReactI18next: {
    type: '3rdParty',
    init: () => {},
  }
}));

// Mock ToastContext (App imports ToastProvider from contexts/ToastContext)
jest.mock('./contexts/ToastContext', () => ({
  __esModule: true,
  ToastProvider: ({ children }) => <>{children}</>,
  useToast: () => ({
    showToast: jest.fn(),
    showSuccess: jest.fn(),
    showError: jest.fn(),
    showInfo: jest.fn(),
    showWarning: jest.fn(),
    removeToast: jest.fn()
  })
}));

// Mock ThemeContext
jest.mock('./contexts/ThemeContext', () => ({
  __esModule: true,
  ThemeProvider: ({ children }) => <>{children}</>,
  useTheme: () => ({
    theme: 'light',
    toggleTheme: jest.fn()
  })
}));

// Mock AuthContext with all required methods
jest.mock('./contexts/AuthContext', () => ({
  __esModule: true,
  AuthProvider: ({ children }) => <>{children}</>,
  useAuth: () => ({
    user: null,
    tokens: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
    refreshToken: jest.fn(),
    changePassword: jest.fn(),
    revokeAllTokens: jest.fn(),
    updateProfile: jest.fn(),
    uploadAvatar: jest.fn(),
    deleteAccount: jest.fn(),
    clearError: jest.fn()
  })
}));

// Mock API服务
jest.mock('./services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } }
  },
  setAuthToken: jest.fn(),
  login: jest.fn(),
  register: jest.fn(),
  logout: jest.fn(),
  refreshToken: jest.fn(),
  changePassword: jest.fn(),
  revokeAllTokens: jest.fn(),
  updateProfile: jest.fn(),
  uploadAvatar: jest.fn(),
  deleteAccount: jest.fn()
}));

// Mock Monaco Editor
jest.mock('@monaco-editor/react', () => {
  return {
    __esModule: true,
    default: ({ value, onChange, language }) => (
      <textarea
        data-testid="monaco-editor"
        value={value || ''}
        onChange={(e) => onChange && onChange(e.target.value)}
        data-language={language}
      />
    )
  };
});

// 直接导入App组件（不使用React.lazy）
import App from './App';

describe('App Component Renders Without Crashing', () => {
  test('renders App component with all providers', () => {
    const { container } = render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    // 未认证用户默认路由会重定向到登录页
    expect(screen.getByText(/login\.title/i)).toBeInTheDocument();
    expect(container.firstChild).toBeInTheDocument();
  });
});

// 测试登录页面
describe('Login Page', () => {
  test('renders login form elements', () => {
    render(
      <MemoryRouter initialEntries={['/login']}>
        <App />
      </MemoryRouter>
    );

    // 检查登录表单元素是否存在
    expect(screen.getByText(/login\.title/i)).toBeInTheDocument();
  });
});

// 测试注册页面
describe('Register Page', () => {
  test('renders register form elements', () => {
    render(
      <MemoryRouter initialEntries={['/register']}>
        <App />
      </MemoryRouter>
    );

    // 检查注册表单元素是否存在
    expect(screen.getByText(/register\.title/i)).toBeInTheDocument();
  });
});

// 测试受保护的路由
describe('Protected Routes', () => {
  test('redirects to login when accessing protected route without auth', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>
    );

    // 未认证用户访问受保护路由时应被重定向到登录页
    expect(screen.getByText(/login\.title/i)).toBeInTheDocument();
  });
});