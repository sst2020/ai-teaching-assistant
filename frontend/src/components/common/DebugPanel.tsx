import React, { useState, useEffect } from 'react';
import './DebugPanel.css';

interface PerformanceData {
  url: string;
  method: string;
  responseTime: number;
  status: number;
  timestamp: number;
}

interface ErrorData {
  url: string;
  method: string;
  status?: number;
  message: string;
  responseTime: number;
  timestamp: number;
  requestId?: string;
}

interface DebugPanelProps {
  isVisible: boolean;
  onToggle: () => void;
}

export const DebugPanel: React.FC<DebugPanelProps> = ({ isVisible, onToggle }) => {
  const [activeTab, setActiveTab] = useState<'performance' | 'errors' | 'logs'>('performance');
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
  const [errorData, setErrorData] = useState<ErrorData[]>([]);
  const [isMinimized, setIsMinimized] = useState(false);

  // 更新性能数据
  useEffect(() => {
    const updateData = () => {
      const performance = JSON.parse(sessionStorage.getItem('api_performance') || '[]');
      const errors = JSON.parse(sessionStorage.getItem('api_errors') || '[]');
      setPerformanceData(performance);
      setErrorData(errors);
    };

    updateData();
    const interval = setInterval(updateData, 1000); // 每秒更新一次

    return () => clearInterval(interval);
  }, []);

  // 计算统计数据
  const stats = {
    totalRequests: performanceData.length,
    averageResponseTime: performanceData.length > 0 
      ? Math.round(performanceData.reduce((sum, item) => sum + item.responseTime, 0) / performanceData.length)
      : 0,
    errorCount: errorData.length,
    successRate: performanceData.length > 0 
      ? Math.round(((performanceData.length - errorData.length) / performanceData.length) * 100)
      : 100
  };

  const clearData = () => {
    sessionStorage.removeItem('api_performance');
    sessionStorage.removeItem('api_errors');
    setPerformanceData([]);
    setErrorData([]);
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getStatusColor = (status: number) => {
    if (status >= 200 && status < 300) return '#4CAF50';
    if (status >= 300 && status < 400) return '#FF9800';
    if (status >= 400 && status < 500) return '#F44336';
    if (status >= 500) return '#9C27B0';
    return '#757575';
  };

  if (!isVisible) {
    return (
      <div className="debug-panel-toggle" onClick={onToggle}>
        🐛 Debug
      </div>
    );
  }

  return (
    <div className={`debug-panel ${isMinimized ? 'minimized' : ''}`}>
      <div className="debug-panel-header">
        <div className="debug-panel-title">
          🐛 调试面板
        </div>
        <div className="debug-panel-controls">
          <button onClick={() => setIsMinimized(!isMinimized)} className="minimize-btn">
            {isMinimized ? '📈' : '📉'}
          </button>
          <button onClick={onToggle} className="close-btn">
            ✕
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          <div className="debug-panel-stats">
            <div className="stat-item">
              <span className="stat-label">总请求:</span>
              <span className="stat-value">{stats.totalRequests}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">平均响应:</span>
              <span className="stat-value">{stats.averageResponseTime}ms</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">错误数:</span>
              <span className="stat-value error">{stats.errorCount}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">成功率:</span>
              <span className="stat-value">{stats.successRate}%</span>
            </div>
            <button onClick={clearData} className="clear-btn">
              清空数据
            </button>
          </div>

          <div className="debug-panel-tabs">
            <button 
              className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
              onClick={() => setActiveTab('performance')}
            >
              性能监控 ({performanceData.length})
            </button>
            <button 
              className={`tab ${activeTab === 'errors' ? 'active' : ''}`}
              onClick={() => setActiveTab('errors')}
            >
              错误日志 ({errorData.length})
            </button>
            <button 
              className={`tab ${activeTab === 'logs' ? 'active' : ''}`}
              onClick={() => setActiveTab('logs')}
            >
              控制台日志
            </button>
          </div>

          <div className="debug-panel-content">
            {activeTab === 'performance' && (
              <div className="performance-tab">
                <div className="table-container">
                  <table className="debug-table">
                    <thead>
                      <tr>
                        <th>时间</th>
                        <th>方法</th>
                        <th>URL</th>
                        <th>状态</th>
                        <th>响应时间</th>
                      </tr>
                    </thead>
                    <tbody>
                      {performanceData.slice(-20).reverse().map((item, index) => (
                        <tr key={index}>
                          <td>{formatTime(item.timestamp)}</td>
                          <td className={`method method-${item.method.toLowerCase()}`}>
                            {item.method}
                          </td>
                          <td className="url">{item.url}</td>
                          <td>
                            <span 
                              className="status-badge"
                              style={{ backgroundColor: getStatusColor(item.status) }}
                            >
                              {item.status}
                            </span>
                          </td>
                          <td className={item.responseTime > 1000 ? 'slow' : ''}>
                            {item.responseTime}ms
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'errors' && (
              <div className="errors-tab">
                <div className="table-container">
                  <table className="debug-table">
                    <thead>
                      <tr>
                        <th>时间</th>
                        <th>方法</th>
                        <th>URL</th>
                        <th>状态</th>
                        <th>错误信息</th>
                      </tr>
                    </thead>
                    <tbody>
                      {errorData.slice(-20).reverse().map((item, index) => (
                        <tr key={index} className="error-row">
                          <td>{formatTime(item.timestamp)}</td>
                          <td className={`method method-${item.method?.toLowerCase()}`}>
                            {item.method}
                          </td>
                          <td className="url">{item.url}</td>
                          <td>
                            {item.status && (
                              <span 
                                className="status-badge error"
                                style={{ backgroundColor: getStatusColor(item.status) }}
                              >
                                {item.status}
                              </span>
                            )}
                          </td>
                          <td className="error-message" title={item.message}>
                            {item.message}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'logs' && (
              <div className="logs-tab">
                <div className="log-info">
                  <p>控制台日志请查看浏览器开发者工具 Console 面板</p>
                  <p>快捷键: F12 或 Ctrl+Shift+I (Windows) / Cmd+Option+I (Mac)</p>
                  <button 
                    onClick={() => {
                      if (process.env.REACT_APP_AUTO_OPEN_DEVTOOLS === 'true') {
                        console.log('Opening DevTools...');
                      }
                    }}
                    className="open-devtools-btn"
                  >
                    打开开发者工具
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};
