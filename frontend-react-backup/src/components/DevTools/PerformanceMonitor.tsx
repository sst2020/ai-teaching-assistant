import React, { useEffect, useMemo, useState } from 'react';
import './PerformanceMonitor.css';

interface PerformanceEntry {
  url: string;
  method: string;
  responseTime: number;
  status: number;
  timestamp: number;
}

interface ErrorEntry {
  url: string;
  method: string;
  status?: number;
  message: string;
  responseTime: number;
  timestamp: number;
  requestId?: string;
}

const readSessionList = <T,>(key: string): T[] => {
  try {
    const raw = sessionStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T[]) : [];
  } catch (err) {
    console.warn(`[PerformanceMonitor] Failed to parse ${key}:`, err);
    return [];
  }
};

const formatMs = (value: number) => `${Math.round(value)}ms`;

const PerformanceMonitor: React.FC = () => {
  const [entries, setEntries] = useState<PerformanceEntry[]>([]);
  const [errors, setErrors] = useState<ErrorEntry[]>([]);

  useEffect(() => {
    const update = () => {
      setEntries(readSessionList<PerformanceEntry>('api_performance'));
      setErrors(readSessionList<ErrorEntry>('api_errors'));
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  const stats = useMemo(() => {
    const total = entries.length;
    const avg = total
      ? entries.reduce((sum, item) => sum + item.responseTime, 0) / total
      : 0;
    const sorted = [...entries].sort((a, b) => a.responseTime - b.responseTime);
    const p95 = total ? sorted[Math.floor(total * 0.95)]?.responseTime ?? 0 : 0;
    const slow = entries.filter((item) => item.responseTime > 1000).length;
    const errorCount = errors.length;
    const errorRate = total ? Math.round((errorCount / total) * 100) : 0;
    return { total, avg, p95, slow, errorCount, errorRate };
  }, [entries, errors]);

  const topEndpoints = useMemo(() => {
    const aggregated = new Map<
      string,
      { count: number; avg: number; max: number; status: number }
    >();

    entries.forEach((entry) => {
      const key = `${entry.method} ${entry.url}`;
      const existing = aggregated.get(key);
      if (!existing) {
        aggregated.set(key, {
          count: 1,
          avg: entry.responseTime,
          max: entry.responseTime,
          status: entry.status,
        });
        return;
      }
      const nextCount = existing.count + 1;
      aggregated.set(key, {
        count: nextCount,
        avg: (existing.avg * existing.count + entry.responseTime) / nextCount,
        max: Math.max(existing.max, entry.responseTime),
        status: entry.status,
      });
    });

    return Array.from(aggregated.entries())
      .map(([key, value]) => ({ key, ...value }))
      .sort((a, b) => b.avg - a.avg)
      .slice(0, 8);
  }, [entries]);

  const recent = useMemo(
    () => [...entries].sort((a, b) => b.timestamp - a.timestamp).slice(0, 20),
    [entries]
  );

  const clearData = () => {
    sessionStorage.removeItem('api_performance');
    sessionStorage.removeItem('api_errors');
    setEntries([]);
    setErrors([]);
  };

  return (
    <div className="performance-monitor">
      <header className="monitor-header">
        <div>
          <h1>Performance Monitor</h1>
          <p>Live API timing and reliability overview.</p>
        </div>
        <button className="clear-btn" onClick={clearData}>
          Clear Data
        </button>
      </header>

      <section className="monitor-stats">
        <div className="stat-card">
          <span className="stat-label">Total Requests</span>
          <span className="stat-value">{stats.total}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Average Time</span>
          <span className="stat-value">{formatMs(stats.avg)}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">P95 Latency</span>
          <span className="stat-value">{formatMs(stats.p95)}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Slow Requests</span>
          <span className="stat-value">{stats.slow}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Error Rate</span>
          <span className="stat-value">{stats.errorRate}%</span>
        </div>
      </section>

      <section className="monitor-grid">
        <div className="panel">
          <h2>Top Endpoints (Avg)</h2>
          {topEndpoints.length === 0 ? (
            <div className="empty">No performance data yet.</div>
          ) : (
            <div className="endpoint-list">
              {topEndpoints.map((item) => (
                <div key={item.key} className="endpoint-row">
                  <div className="endpoint-meta">
                    <span className="endpoint-name">{item.key}</span>
                    <span className="endpoint-count">{item.count} calls</span>
                  </div>
                  <div className="endpoint-bar">
                    <span style={{ width: `${Math.min(item.avg / 20, 100)}%` }} />
                  </div>
                  <div className="endpoint-metrics">
                    <span>{formatMs(item.avg)}</span>
                    <span className="max">max {formatMs(item.max)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="panel">
          <h2>Recent Requests</h2>
          {recent.length === 0 ? (
            <div className="empty">No recent requests.</div>
          ) : (
            <div className="recent-table">
              {recent.map((entry, index) => (
                <div key={`${entry.timestamp}-${index}`} className="recent-row">
                  <div className="recent-left">
                    <span className={`method method-${entry.method.toLowerCase()}`}>
                      {entry.method}
                    </span>
                    <span className="recent-url">{entry.url}</span>
                  </div>
                  <div className="recent-right">
                    <span className={`status status-${entry.status}`}>
                      {entry.status}
                    </span>
                    <span className={entry.responseTime > 1000 ? 'slow' : ''}>
                      {formatMs(entry.responseTime)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default PerformanceMonitor;
