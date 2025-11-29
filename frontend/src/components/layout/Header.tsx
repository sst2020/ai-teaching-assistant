import React, { useState, useEffect } from 'react';
import { getHealthStatus } from '../../services/api';
import './Header.css';

const Header: React.FC = () => {
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
          <span className="header-logo">🎓</span>
          <h1 className="header-title">AI Teaching Assistant</h1>
        </div>
        <nav className="header-nav">
          <a href="#dashboard" className="nav-link active">Dashboard</a>
          <a href="#code-analysis" className="nav-link">Code Analysis</a>
          <a href="#qa" className="nav-link">Q&A</a>
          <a href="#grading" className="nav-link">Grading</a>
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

