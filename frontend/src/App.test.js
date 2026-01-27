import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

// Mock complex components that might cause issues during testing
jest.mock('./components/layout/Header', () => {
  return {
    __esModule: true,
    Header: ({ children }) => <header data-testid="mock-header">{children}</header>,
  };
});

jest.mock('./contexts/AuthContext', () => {
  return {
    __esModule: true,
    AuthProvider: ({ children }) => <div data-testid="auth-provider">{children}</div>,
    useAuth: () => ({ user: null, login: jest.fn(), logout: jest.fn() }),
  };
});

jest.mock('./contexts/ToastContext', () => {
  return {
    __esModule: true,
    ToastProvider: ({ children }) => <div>{children}</div>,
  };
});

jest.mock('./contexts/ThemeContext', () => {
  return {
    __esModule: true,
    ThemeProvider: ({ children }) => <div>{children}</div>,
  };
});

test('renders App component without crashing', () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );

  // Since the actual App component is complex, we just check if it renders
  // without throwing errors
  expect(screen.getByTestId('auth-provider')).toBeInTheDocument();
});
