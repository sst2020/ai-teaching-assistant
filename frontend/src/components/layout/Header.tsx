import React, { useState, useEffect, useRef } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { getHealthStatus } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import './Header.css';

interface HeaderProps {
  activeTab?: string;
}

const Header: React.FC<HeaderProps> = () => {
  const { t, i18n } = useTranslation('navigation');
  const { t: tAuth } = useTranslation('auth');
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // 点击外部关闭菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        await getHealthStatus();
        setBackendStatus('connected');
      } catch (error) {
        setBackendStatus('disconnected');
      }
    };

    checkBackendStatus();
    // Check every 30 seconds
    const interval = setInterval(checkBackendStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const toggleLanguage = () => {
    const newLang = i18n.language === 'zh' ? 'en' : 'zh';
    i18n.changeLanguage(newLang);
  };

  const handleLogout = async () => {
    setShowUserMenu(false);
    await logout();
    navigate('/login');
  };

  const handleProfileClick = () => {
    setShowUserMenu(false);
    navigate('/account');
  };

  const getAvatarUrl = () => {
    if (user?.avatar_url) {
      if (user.avatar_url.startsWith('/')) {
        return `http://localhost:8000${user.avatar_url}`;
      }
      return user.avatar_url;
    }
    return null;
  };

  // 根据用户角色渲染导航项
  const renderNavigationItems = () => {
    if (!isAuthenticated || !user) return null;

    const role = user.role;

    // 学生导航项
    if (role === 'student') {
      return (
        <>
          <NavLink
            to="/dashboard"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            🏠 {t('menu.dashboard')}
          </NavLink>
          <NavLink
            to="/submit/assignment" // 使用通用路径，实际应用中应根据实际情况调整
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            📝 {t('menu.submitAssignment')}
          </NavLink>
          <NavLink
            to="/grades"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            📊 {t('menu.grades')}
          </NavLink>
          <NavLink
            to="/smart-qa"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            💬 {t('menu.smartQA')}
          </NavLink>
        </>
      );
    }

    // 教师和管理员导航项
    if (role === 'teacher' || role === 'admin') {
      return (
        <>
          <NavLink
            to="/teacher"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            👨‍🏫 {t('menu.teacherDashboard')}
          </NavLink>
          <NavLink
            to="/grading"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            ✍️ {t('menu.grading')}
          </NavLink>
          <NavLink
            to="/manage-assignments"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            📋 {t('menu.manageAssignments')}
          </NavLink>
          <NavLink
            to="/question-queue"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            ❓ {t('menu.questionQueue')}
          </NavLink>
          <NavLink
            to="/code-analysis"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            📊 {t('menu.codeAnalysis')}
          </NavLink>
          <NavLink
            to="/plagiarism"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            🔍 {t('menu.plagiarism')}
          </NavLink>
          <NavLink
            to="/report-analysis"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            📑 {t('menu.reportAnalysis')}
          </NavLink>
          {/* 教师也可以访问学生功能进行演示 */}
          <NavLink
            to="/smart-qa"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            💬 {t('menu.smartQA')}
          </NavLink>
          {/* 开发工具 - 仅开发环境显示 */}
          {process.env.NODE_ENV === 'development' && (
            <NavLink
              to="/dev/api-tester"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              🔧 API 测试
            </NavLink>
          )}
        </>
      );
    }

    // 默认返回空导航
    return null;
  };

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-brand">
          <NavLink to={user?.role === 'teacher' || user?.role === 'admin' ? '/teacher' : '/dashboard'} className="brand-link">
            <span className="header-logo">🎓</span>
            <h1 className="header-title">{t('appTitle')}</h1>
          </NavLink>
        </div>
        <nav className="header-nav">
          {renderNavigationItems()}
        </nav>
        <div className="header-actions">
          <button
            className="language-toggle"
            onClick={toggleLanguage}
            title={i18n.language === 'zh' ? 'Switch to English' : '切换到中文'}
          >
            🌐 {i18n.language === 'zh' ? 'EN' : '中'}
          </button>
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={theme === 'light' ? '切换到深色模式' : '切换到浅色模式'}
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
          <div className="header-status">
            <span className={`status-indicator ${backendStatus}`}></span>
            <span className="status-text">
              {backendStatus === 'checking' && t('status.checking')}
              {backendStatus === 'connected' && t('status.backendConnected')}
              {backendStatus === 'disconnected' && t('status.backendOffline')}
            </span>
          </div>

          {/* 用户菜单 */}
          {isAuthenticated && user && (
            <div className="user-menu-container" ref={userMenuRef}>
              <button
                className="user-menu-trigger"
                onClick={() => setShowUserMenu(!showUserMenu)}
              >
                {getAvatarUrl() ? (
                  <img src={getAvatarUrl()!} alt="Avatar" className="user-avatar" />
                ) : (
                  <div className="user-avatar-placeholder">
                    {user.name?.charAt(0) || user.student_id?.charAt(0) || '?'}
                  </div>
                )}
                <span className="user-name">{user.name || user.student_id}</span>
                <span className="dropdown-arrow">{showUserMenu ? '▲' : '▼'}</span>
              </button>

              {showUserMenu && (
                <div className="user-dropdown">
                  <button onClick={handleProfileClick} className="dropdown-item">
                    {`👤 ${tAuth('profile')}`}
                  </button>
                  <div className="dropdown-divider" />
                  <button onClick={handleLogout} className="dropdown-item logout">
                    {`🚪 ${tAuth('logout')}`}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;

