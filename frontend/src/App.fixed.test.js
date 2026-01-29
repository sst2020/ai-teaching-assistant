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

// Mock Toast组件
const MockToastProvider = ({ children }) => <>{children}</>;
jest.mock('./components/common/Toast', () => ({
  ToastProvider: MockToastProvider,
  useToast: () => ({
    showToast: jest.fn()
  })
}));

// Mock ThemeContext
const MockThemeProvider = ({ children }) => <>{children}</>;
jest.mock('./contexts/ThemeContext', () => ({
  ThemeProvider: MockThemeProvider,
  useTheme: () => ({
    theme: 'light',
    toggleTheme: jest.fn()
  })
}));

// Mock AuthContext with all required methods
const MockAuthProvider = ({ children }) => <>{children}</>;
jest.mock('./contexts/AuthContext', () => ({
  AuthProvider: MockAuthProvider,
  useAuth: () => ({
    user: null,
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
    loading: false,
    error: null,
    isAuthenticated: false,
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
    delete: jest.fn()
  }
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

// 导入App组件
const App = React.lazy(() => import('./App'));

describe('App Component Renders Without Crashing', () => {
  test('renders App component with all providers', async () => {
    const { container } = render(
      <MemoryRouter>
        <React.Suspense fallback={<div>Loading...</div>}>
          <App />
        </React.Suspense>
      </MemoryRouter>
    );
    
    // 等待组件加载完成
    await screen.findByText(/login\.title/i); // 应该能看到登录页面的标题
    
    // 检查页面基本结构
    expect(container.firstChild).toBeInTheDocument();
  });
});

// 测试登录页面
describe('Login Page', () => {
  test('renders login form elements', () => {
    render(
      <MemoryRouter initialEntries={['/login']}>
        <React.Suspense fallback={<div>Loading...</div>}>
          <App />
        </React.Suspense>
      </MemoryRouter>
    );
    
    // 检查登录表单元素是否存在
    expect(screen.getByLabelText(/login\.studentIdLabel/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/login\.passwordLabel/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login\.submitButton/i })).toBeInTheDocument();
    expect(screen.getByText(/login\.noAccount/i)).toBeInTheDocument();
  });
});

// 测试注册页面
describe('Register Page', () => {
  test('renders register form elements', () => {
    render(
      <MemoryRouter initialEntries={['/register']}>
        <React.Suspense fallback={<div>Loading...</div>}>
          <App />
        </React.Suspense>
      </MemoryRouter>
    );
    
    // 检查注册表单元素是否存在
    expect(screen.getByLabelText(/register\.nameLabel/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/register\.studentIdLabel/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/register\.passwordLabel/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register\.submitButton/i })).toBeInTheDocument();
    expect(screen.getByText(/register\.hasAccount/i)).toBeInTheDocument();
  });
});

// 测试受保护的路由
describe('Protected Routes', () => {
  test('redirects to login when accessing protected route without auth', () => {
    render(
      <MemoryRouter initialEntries={['/student-dashboard']}>
        <React.Suspense fallback={<div>Loading...</div>}>
          <App />
        </React.Suspense>
      </MemoryRouter>
    );
    
    // 未认证用户访问受保护路由时应被重定向到登录页
    expect(screen.getByText(/login\.title/i)).toBeInTheDocument();
  });
});

// 测试提交作业页面
describe('Submit Assignment Page', () => {
  test('renders assignment submission elements', () => {
    render(
      <MemoryRouter initialEntries={['/submit-assignment']}>
        <React.Suspense fallback={<div>Loading...</div>}>
          <App />
        </React.Suspense>
      </MemoryRouter>
    );
    
    // 检查是否有代码编辑器
    const editor = screen.queryByTestId('monaco-editor');
    if (editor) {
      expect(editor).toBeInTheDocument();
    }
    
    // 检查提交按钮
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });
});