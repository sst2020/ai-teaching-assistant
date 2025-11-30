import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { getHealthStatus } from '../../services/api';
import './Header.css';

interface HeaderProps {
  activeTab?: string;
}

const Header: React.FC<HeaderProps> = () => {
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

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-brand">
          <NavLink to="/dashboard" className="brand-link">
            <span className="header-logo">🎓</span>
            <h1 className="header-title">AI Teaching Assistant</h1>
          </NavLink>
        </div>
        <nav className="header-nav">
          <NavLink
            to="/dashboard"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            🏠 Dashboard
          </NavLink>
          <NavLink
            to="/code-analysis"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            📊 Code Analysis
          </NavLink>
          <NavLink
            to="/qa"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            💬 Q&A
          </NavLink>
        </nav>
        <div className="header-status">
          <span className={`status-indicator ${backendStatus}`}></span>
          <span className="status-text">
            {backendStatus === 'checking' && 'Checking...'}
            {backendStatus === 'connected' && 'Backend Connected'}
            {backendStatus === 'disconnected' && 'Backend Offline'}
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;

