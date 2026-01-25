import React, { useState, useEffect, useCallback } from 'react';
import './ApiTester.css';

// HTTP 方法类型
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

// 请求历史记录类型
interface RequestHistoryItem {
  id: string;
  timestamp: number;
  method: HttpMethod;
  url: string;
  headers: Record<string, string>;
  body: string;
  status?: number;
  responseTime?: number;
}

// 响应类型
interface ApiResponse {
  status: number;
  statusText: string;
  headers: Record<string, string>;
  data: unknown;
  responseTime: number;
}

const STORAGE_KEY = 'api-tester-history';
const MAX_HISTORY = 50;

const ApiTester: React.FC = () => {
  // 请求状态
  const [method, setMethod] = useState<HttpMethod>('GET');
  const [url, setUrl] = useState<string>('http://localhost:8000/api/');
  const [headers, setHeaders] = useState<string>('{\n  "Content-Type": "application/json"\n}');
  const [body, setBody] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // 响应状态
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 历史记录
  const [history, setHistory] = useState<RequestHistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // 从 localStorage 加载历史记录
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setHistory(JSON.parse(saved));
      }
    } catch (e) {
      console.error('加载历史记录失败:', e);
    }
  }, []);

  // 保存历史记录到 localStorage
  const saveHistory = useCallback((newHistory: RequestHistoryItem[]) => {
    const trimmed = newHistory.slice(0, MAX_HISTORY);
    setHistory(trimmed);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    } catch (e) {
      console.error('保存历史记录失败:', e);
    }
  }, []);

  // 发送请求
  const sendRequest = async () => {
    setIsLoading(true);
    setError(null);
    setResponse(null);

    const startTime = Date.now();
    const requestId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    try {
      // 解析请求头
      let parsedHeaders: Record<string, string> = {};
      if (headers.trim()) {
        try {
          parsedHeaders = JSON.parse(headers);
        } catch {
          throw new Error('请求头 JSON 格式无效');
        }
      }

      // 添加认证令牌
      const token = localStorage.getItem('access_token');
      if (token && !parsedHeaders['Authorization']) {
        parsedHeaders['Authorization'] = `Bearer ${token}`;
      }

      // 构建请求选项
      const options: RequestInit = {
        method,
        headers: parsedHeaders,
      };

      // 添加请求体（非 GET 请求）
      if (method !== 'GET' && body.trim()) {
        options.body = body;
      }

      // 发送请求
      const res = await fetch(url, options);
      const responseTime = Date.now() - startTime;

      // 解析响应头
      const responseHeaders: Record<string, string> = {};
      res.headers.forEach((value, key) => {
        responseHeaders[key] = value;
      });

      // 解析响应体
      let responseData: unknown;
      const contentType = res.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        responseData = await res.json();
      } else {
        responseData = await res.text();
      }

      const apiResponse: ApiResponse = {
        status: res.status,
        statusText: res.statusText,
        headers: responseHeaders,
        data: responseData,
        responseTime,
      };

      setResponse(apiResponse);

      // 保存到历史记录
      const historyItem: RequestHistoryItem = {
        id: requestId,
        timestamp: Date.now(),
        method,
        url,
        headers: parsedHeaders,
        body,
        status: res.status,
        responseTime,
      };
      saveHistory([historyItem, ...history]);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '请求失败';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // 从历史记录加载请求
  const loadFromHistory = (item: RequestHistoryItem) => {
    setMethod(item.method);
    setUrl(item.url);
    setHeaders(JSON.stringify(item.headers, null, 2));
    setBody(item.body);
    setShowHistory(false);
  };

  // 清除历史记录
  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  // 格式化响应数据
  const formatResponseData = (data: unknown): string => {
    if (typeof data === 'string') return data;
    try {
      return JSON.stringify(data, null, 2);
    } catch {
      return String(data);
    }
  };

  // 获取状态码颜色类名
  const getStatusClass = (status: number): string => {
    if (status >= 200 && status < 300) return 'status-success';
    if (status >= 400 && status < 500) return 'status-client-error';
    if (status >= 500) return 'status-server-error';
    return 'status-info';
  };

  return (
    <div className="api-tester">
      <div className="api-tester-header">
        <h1>API 测试工具</h1>
        <button
          className="history-toggle"
          onClick={() => setShowHistory(!showHistory)}
        >
          {showHistory ? '隐藏历史' : '显示历史'} ({history.length})
        </button>
      </div>

      <div className="api-tester-content">
        {/* 请求构建器 */}
        <div className="request-builder">
          <div className="request-line">
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value as HttpMethod)}
              className={`method-select method-${method.toLowerCase()}`}
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="PATCH">PATCH</option>
              <option value="DELETE">DELETE</option>
            </select>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="请输入 API URL"
              className="url-input"
            />
            <button
              onClick={sendRequest}
              disabled={isLoading || !url.trim()}
              className="send-button"
            >
              {isLoading ? '发送中...' : '发送'}
            </button>
          </div>

          <div className="request-sections">
            <div className="section">
              <label>请求头 (JSON)</label>
              <textarea
                value={headers}
                onChange={(e) => setHeaders(e.target.value)}
                placeholder='{"Content-Type": "application/json"}'
                className="headers-input"
                rows={4}
              />
            </div>

            {method !== 'GET' && (
              <div className="section">
                <label>请求体</label>
                <textarea
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  placeholder="请输入请求体内容"
                  className="body-input"
                  rows={6}
                />
              </div>
            )}
          </div>
        </div>

        {/* 响应查看器 */}
        <div className="response-viewer">
          <h2>响应</h2>
          {isLoading && <div className="loading">请求中...</div>}
          {error && <div className="error-message">{error}</div>}
          {response && (
            <div className="response-content">
              <div className="response-meta">
                <span className={`status-badge ${getStatusClass(response.status)}`}>
                  {response.status} {response.statusText}
                </span>
                <span className="response-time">{response.responseTime}ms</span>
              </div>
              <div className="response-headers">
                <h3>响应头</h3>
                <pre>{JSON.stringify(response.headers, null, 2)}</pre>
              </div>
              <div className="response-body">
                <h3>响应体</h3>
                <pre>{formatResponseData(response.data)}</pre>
              </div>
            </div>
          )}
          {!isLoading && !error && !response && (
            <div className="empty-state">点击发送按钮执行请求</div>
          )}
        </div>
      </div>

      {/* 历史记录面板 */}
      {showHistory && (
        <div className="history-panel">
          <div className="history-header">
            <h2>请求历史</h2>
            <button onClick={clearHistory} className="clear-history">
              清除全部
            </button>
          </div>
          <div className="history-list">
            {history.length === 0 ? (
              <div className="empty-history">暂无历史记录</div>
            ) : (
              history.map((item) => (
                <div
                  key={item.id}
                  className="history-item"
                  onClick={() => loadFromHistory(item)}
                >
                  <span className={`method-badge method-${item.method.toLowerCase()}`}>
                    {item.method}
                  </span>
                  <span className="history-url">{item.url}</span>
                  {item.status && (
                    <span className={`status-badge ${getStatusClass(item.status)}`}>
                      {item.status}
                    </span>
                  )}
                  <span className="history-time">
                    {new Date(item.timestamp).toLocaleString()}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiTester;

