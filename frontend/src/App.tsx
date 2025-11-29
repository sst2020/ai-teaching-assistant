import React, { useState } from 'react';
import { Header } from './components/layout';
import { Dashboard } from './components/Dashboard';
import { CodeAnalysis } from './components/CodeAnalysis';
import { QAInterface } from './components/QAInterface';
import './App.css';

type TabType = 'dashboard' | 'code-analysis' | 'qa';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');

  const handleHashChange = () => {
    const hash = window.location.hash.replace('#', '') as TabType;
    if (['dashboard', 'code-analysis', 'qa'].includes(hash)) {
      setActiveTab(hash);
    }
  };

  React.useEffect(() => {
    window.addEventListener('hashchange', handleHashChange);
    handleHashChange(); // Check initial hash
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'code-analysis':
        return <CodeAnalysis />;
      case 'qa':
        return <QAInterface />;
      case 'dashboard':
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Header />
      <main className="app-main">
        <div className="tab-navigation">
          <button
            className={`tab-button ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('dashboard');
              window.location.hash = 'dashboard';
            }}
          >
            🏠 Dashboard
          </button>
          <button
            className={`tab-button ${activeTab === 'code-analysis' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('code-analysis');
              window.location.hash = 'code-analysis';
            }}
          >
            📊 Code Analysis
          </button>
          <button
            className={`tab-button ${activeTab === 'qa' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('qa');
              window.location.hash = 'qa';
            }}
          >
            💬 Q&A
          </button>
        </div>
        <div className="content-container">
          {renderContent()}
        </div>
      </main>
    </div>
  );
};

export default App;

