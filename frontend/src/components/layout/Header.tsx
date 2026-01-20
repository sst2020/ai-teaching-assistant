import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { getHealthStatus } from '../../services/api';
import './Header.css';

interface HeaderProps {
  activeTab?: string;
}

const Header: React.FC<HeaderProps> = () => {
  const { t, i18n } = useTranslation('navigation');
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

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

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-brand">
          <NavLink to="/dashboard" className="brand-link">
            <span className="header-logo">🎓</span>
            <h1 className="header-title">{t('appTitle')}</h1>
          </NavLink>
        </div>
        <nav className="header-nav">
          <NavLink
            to="/dashboard"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            🏠 {t('menu.dashboard')}
          </NavLink>
          <NavLink
            to="/code-analysis"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            📊 {t('menu.codeAnalysis')}
          </NavLink>
          <NavLink
            to="/qa"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            💬 {t('menu.qa')}
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
        </nav>
        <div className="header-actions">
          <button
            className="language-toggle"
            onClick={toggleLanguage}
            title={i18n.language === 'zh' ? 'Switch to English' : '切换到中文'}
          >
            🌐 {i18n.language === 'zh' ? 'EN' : '中'}
          </button>
          <div className="header-status">
            <span className={`status-indicator ${backendStatus}`}></span>
            <span className="status-text">
              {backendStatus === 'checking' && t('status.checking')}
              {backendStatus === 'connected' && t('status.backendConnected')}
              {backendStatus === 'disconnected' && t('status.backendOffline')}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

