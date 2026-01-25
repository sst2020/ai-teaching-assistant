import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

// 主题类型定义
export type Theme = 'light' | 'dark';

// Context 类型定义
interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
  isDarkMode: boolean;
}

// Storage key
const THEME_KEY = 'theme_preference';

// 创建 Context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// 获取系统偏好主题
const getSystemTheme = (): Theme => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return 'light';
};

// 从 localStorage 获取保存的主题
const getSavedTheme = (): Theme | null => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved === 'light' || saved === 'dark') {
      return saved;
    }
  }
  return null;
};

// 获取初始主题
const getInitialTheme = (): Theme => {
  const saved = getSavedTheme();
  if (saved) {
    return saved;
  }
  return getSystemTheme();
};

// ThemeProvider 组件
interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(getInitialTheme);

  // 应用主题到 DOM
  const applyTheme = useCallback((newTheme: Theme) => {
    document.documentElement.setAttribute('data-theme', newTheme);
    // 更新 meta theme-color 以适配移动端
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute(
        'content',
        newTheme === 'dark' ? '#1C1B1F' : '#FFFBFE'
      );
    }
  }, []);

  // 设置主题
  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem(THEME_KEY, newTheme);
    applyTheme(newTheme);
  }, [applyTheme]);

  // 切换主题
  const toggleTheme = useCallback(() => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  }, [theme, setTheme]);

  // 初始化时应用主题
  useEffect(() => {
    applyTheme(theme);
  }, []);

  // 监听系统主题变化
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      // 仅当用户未手动设置主题时跟随系统
      if (!getSavedTheme()) {
        const newTheme = e.matches ? 'dark' : 'light';
        setThemeState(newTheme);
        applyTheme(newTheme);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [applyTheme]);

  const value: ThemeContextType = {
    theme,
    toggleTheme,
    setTheme,
    isDarkMode: theme === 'dark',
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

// useTheme Hook
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeContext;

