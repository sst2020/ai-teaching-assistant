import React, { Component, ReactNode } from 'react';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface ErrorReport {
  errorId: string;
  timestamp: string;
  message: string;
  stack?: string;
  componentStack?: string;
  retryCount: number;
}

export interface ErrorBoundaryProps {
  children: ReactNode;
  /** 自定义降级 UI，接收错误信息和重试函数 */
  fallback?: (report: ErrorReport, retry: () => void) => ReactNode;
  /** 错误发生时的回调，可用于上报到监控服务 */
  onError?: (report: ErrorReport) => void;
  /** 是否在开发模式下展示详细调试信息（默认仅 development 环境显示） */
  showDebugInfo?: boolean;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
  errorId: string;
  timestamp: string;
  retryCount: number;
  debugExpanded: boolean;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function generateErrorId(): string {
  return `err_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`;
}

// ─── Component ───────────────────────────────────────────────────────────────

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      errorId: '',
      timestamp: '',
      retryCount: 0,
      debugExpanded: false,
    };
    this.handleRetry = this.handleRetry.bind(this);
    this.toggleDebug = this.toggleDebug.bind(this);
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────────

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
      errorId: generateErrorId(),
      timestamp: new Date().toISOString(),
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    const { errorId, timestamp, retryCount } = this.state;

    const report: ErrorReport = {
      errorId,
      timestamp,
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack ?? undefined,
      retryCount,
    };

    // 结构化错误日志 —— 始终输出
    console.group(`🚨 [ErrorBoundary] ${errorId}`);
    console.error('错误信息:', error.message);
    console.error('错误堆栈:', error.stack);
    console.error('组件堆栈:', errorInfo.componentStack);
    console.error('发生时间:', timestamp);
    console.error('重试次数:', retryCount);
    console.groupEnd();

    // 保存 errorInfo 到 state，供调试面板使用
    this.setState({ errorInfo });

    // 触发外部回调（用于接入 Sentry / 自定义监控）
    if (this.props.onError) {
      try {
        this.props.onError(report);
      } catch (cbError) {
        console.warn('[ErrorBoundary] onError 回调抛出异常:', cbError);
      }
    }
  }

  // ── Actions ────────────────────────────────────────────────────────────────

  handleRetry(): void {
    this.setState((prev) => ({
      hasError: false,
      error: undefined,
      errorInfo: undefined,
      errorId: '',
      timestamp: '',
      retryCount: prev.retryCount + 1,
      debugExpanded: false,
    }));
  }

  toggleDebug(): void {
    this.setState((prev) => ({ debugExpanded: !prev.debugExpanded }));
  }

  // ── Render helpers ─────────────────────────────────────────────────────────

  private buildReport(): ErrorReport {
    const { error, errorId, timestamp, retryCount, errorInfo } = this.state;
    return {
      errorId,
      timestamp,
      message: error?.message ?? '未知错误',
      stack: error?.stack,
      componentStack: errorInfo?.componentStack ?? undefined,
      retryCount,
    };
  }

  private renderDefaultFallback(report: ErrorReport): ReactNode {
    const isDev =
      this.props.showDebugInfo !== undefined
        ? this.props.showDebugInfo
        : process.env.NODE_ENV === 'development';

    const { debugExpanded } = this.state;

    return (
      <div style={styles.container}>
        {/* 头部图标 + 标题 */}
        <div style={styles.header}>
          <span style={styles.icon}>⚠️</span>
          <div>
            <h2 style={styles.title}>页面出现错误</h2>
            <p style={styles.subtitle}>{report.message}</p>
          </div>
        </div>

        {/* 错误元数据 */}
        <div style={styles.meta}>
          <span style={styles.metaItem}>🆔 {report.errorId}</span>
          <span style={styles.metaItem}>🕐 {new Date(report.timestamp).toLocaleString('zh-CN')}</span>
          {report.retryCount > 0 && (
            <span style={styles.metaItem}>🔁 已重试 {report.retryCount} 次</span>
          )}
        </div>

        {/* 操作按钮 */}
        <div style={styles.actions}>
          <button style={styles.retryBtn} onClick={this.handleRetry}>
            🔄 重试
          </button>
          <button
            style={styles.reloadBtn}
            onClick={() => window.location.reload()}
          >
            ↺ 刷新页面
          </button>
        </div>

        {/* 调试信息（仅 dev 环境或 showDebugInfo=true） */}
        {isDev && (
          <div style={styles.debugSection}>
            <button style={styles.debugToggle} onClick={this.toggleDebug}>
              {debugExpanded ? '▲ 隐藏调试信息' : '▼ 展开调试信息'}
            </button>
            {debugExpanded && (
              <div style={styles.debugContent}>
                {report.stack && (
                  <>
                    <p style={styles.debugLabel}>错误堆栈：</p>
                    <pre style={styles.pre}>{report.stack}</pre>
                  </>
                )}
                {report.componentStack && (
                  <>
                    <p style={styles.debugLabel}>组件堆栈：</p>
                    <pre style={styles.pre}>{report.componentStack}</pre>
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // ── Main render ────────────────────────────────────────────────────────────

  render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }

    const report = this.buildReport();

    if (this.props.fallback) {
      return this.props.fallback(report, this.handleRetry);
    }

    return this.renderDefaultFallback(report);
  }
}

// ─── Inline styles (no external CSS dependency) ──────────────────────────────

const styles: Record<string, React.CSSProperties> = {
  container: {
    margin: '2rem auto',
    maxWidth: 680,
    padding: '2rem',
    borderRadius: 12,
    border: '1px solid #fca5a5',
    background: '#fff1f2',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    color: '#1f2937',
  },
  header: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '1rem',
    marginBottom: '1rem',
  },
  icon: { fontSize: '2rem', lineHeight: 1 },
  title: { margin: 0, fontSize: '1.25rem', color: '#b91c1c' },
  subtitle: { margin: '0.25rem 0 0', fontSize: '0.95rem', color: '#374151' },
  meta: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '0.5rem',
    marginBottom: '1.25rem',
  },
  metaItem: {
    fontSize: '0.8rem',
    background: '#fee2e2',
    padding: '0.2rem 0.6rem',
    borderRadius: 999,
    color: '#7f1d1d',
  },
  actions: { display: 'flex', gap: '0.75rem', marginBottom: '1.25rem' },
  retryBtn: {
    padding: '0.5rem 1.25rem',
    borderRadius: 8,
    border: 'none',
    background: '#dc2626',
    color: '#fff',
    fontWeight: 600,
    cursor: 'pointer',
    fontSize: '0.9rem',
  },
  reloadBtn: {
    padding: '0.5rem 1.25rem',
    borderRadius: 8,
    border: '1px solid #d1d5db',
    background: '#fff',
    color: '#374151',
    fontWeight: 500,
    cursor: 'pointer',
    fontSize: '0.9rem',
  },
  debugSection: { borderTop: '1px solid #fca5a5', paddingTop: '0.75rem' },
  debugToggle: {
    background: 'none',
    border: 'none',
    color: '#6b7280',
    cursor: 'pointer',
    fontSize: '0.85rem',
    padding: 0,
  },
  debugContent: { marginTop: '0.75rem' },
  debugLabel: { margin: '0.5rem 0 0.25rem', fontWeight: 600, fontSize: '0.85rem', color: '#4b5563' },
  pre: {
    margin: 0,
    padding: '0.75rem',
    borderRadius: 6,
    background: '#1f2937',
    color: '#f9fafb',
    fontSize: '0.75rem',
    overflowX: 'auto' as const,
    whiteSpace: 'pre-wrap' as const,
    wordBreak: 'break-word' as const,
    maxHeight: 300,
    overflowY: 'auto' as const,
  },
};

export default ErrorBoundary;