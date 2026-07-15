// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock for ES modules that Jest cannot parse
jest.mock('react-markdown', () => {
  return {
    __esModule: true,
    default: ({ children }) => <div data-testid="react-markdown">{children}</div>
  };
});

jest.mock('remark-gfm', () => {
  return () => {};
});

jest.mock('react-syntax-highlighter', () => {
  return {
    __esModule: true,
    Prism: ({ children }) => <pre data-testid="syntax-highlighter">{children}</pre>
  };
});

jest.mock('react-syntax-highlighter/dist/esm/styles/prism', () => {
  return {
    oneDark: {}
  };
});
