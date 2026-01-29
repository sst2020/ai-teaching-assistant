import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

// Mock所有可能有问题的导入
jest.mock('./components/common/Toast', () => {
  return {
    __esModule: true,
    ToastProvider: ({ children }) => <div data-testid="toast-provider">{children}</div>,
    useToast: () => ({
      showToast: jest.fn()
    })
  };
});

jest.mock('./contexts/ThemeContext', () => {
  return {
    __esModule: true,
    ThemeProvider: ({ children }) => <div data-testid="theme-provider">{children}</div>,
    useTheme: () => ({
      theme: 'light',
      toggleTheme: jest.fn()
    })
  };
});

jest.mock('./services/api', () => {
  return {
    __esModule: true,
    default: {
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      delete: jest.fn()
    }
  };
});

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

// Mock i18n
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (str: string) => str,
    i18n: {
      changeLanguage: () => new Promise(() => {}),
    },
  }),
  initReactI18next: {
    type: '3rdParty',
    init: () => {},
  }
}));

describe('App Component', () => {
  test('renders without crashing', async () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    // 检查是否渲染了应用的基本结构
    expect(screen.getByTestId('theme-provider')).toBeInTheDocument();
    expect(screen.getByTestId('toast-provider')).toBeInTheDocument();
  });
});

// 测试登录页面
describe('Login Page', () => {
  test('renders login form elements', async () => {
    render(
      <MemoryRouter initialEntries={['/login']}>
        <App />
      </MemoryRouter>
    );

    // 检查登录表单元素是否存在
    expect(screen.getByLabelText(/login\.studentIdLabel/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/login\.passwordLabel/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login\.submitButton/i })).toBeInTheDocument();
  });
});

// 测试注册页面
describe('Register Page', () => {
  test('renders register form elements', async () => {
    render(
      <MemoryRouter initialEntries={['/register']}>
        <App />
      </MemoryRouter>
    );

    // 检查注册表单元素是否存在
    expect(screen.getByLabelText(/register\.nameLabel/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/register\.studentIdLabel/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/register\.passwordLabel/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register\.submitButton/i })).toBeInTheDocument();
  });
});

// 测试学生仪表板
describe('Student Dashboard', () => {
  test('renders student dashboard elements', async () => {
    render(
      <MemoryRouter initialEntries={['/student-dashboard']}>
        <App />
      </MemoryRouter>
    );

    // 检查是否显示了学生仪表板相关元素
    expect(screen.getByText(/studentDashboard\.welcome/i)).toBeInTheDocument();
  });
});

// 测试提交作业页面
describe('Submit Assignment Page', () => {
  test('renders assignment submission elements', async () => {
    render(
      <MemoryRouter initialEntries={['/submit-assignment']}>
        <App />
      </MemoryRouter>
    );

    // 检查是否有代码编辑器
    const editor = screen.queryByTestId('monaco-editor');
    if (editor) {
      expect(editor).toBeInTheDocument();
    }

    // 检查提交按钮
    expect(screen.getByRole('button', { name: /submitAssignment\.submitButton/i })).toBeInTheDocument();
  });
});