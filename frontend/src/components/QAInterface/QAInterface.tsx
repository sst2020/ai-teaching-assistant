import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useTranslation } from 'react-i18next';
import { askQuestionStream, handleApiError } from '../../services/api';
import { LoadingSpinner, ErrorMessage } from '../common';
import { useAuth } from '../../contexts/AuthContext';
import './QAInterface.css';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const codeStyle = oneDark as any;

interface Message {
  id: string;
  type: 'question' | 'answer';
  content: string;
  timestamp: Date;
  confidence?: number;
  isStreaming?: boolean;
}

const QAInterface: React.FC = () => {
  const { t } = useTranslation('qa');
  const { user, isAuthenticated } = useAuth();
  const [question, setQuestion] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [streamingContent, setStreamingContent] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!question.trim()) return;

    const currentQuestion = question;
    const questionMessage: Message = {
      id: Date.now().toString(),
      type: 'question',
      content: currentQuestion,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, questionMessage]);
    setQuestion('');
    setLoading(true);
    setError(null);
    setStreamingContent('');

    // 创建一个临时的流式消息
    const streamingMessageId = `streaming-${Date.now()}`;

    try {
      let fullContent = '';
      let finalConfidence = 0.85;

      await askQuestionStream(
        {
          student_id: user?.student_id || 'anonymous',
          course_id: 'general',
          question: currentQuestion,
        },
        {
          onStart: () => {
            // 流式开始
          },
          onChunk: (chunk: string) => {
            fullContent += chunk;
            setStreamingContent(fullContent);
          },
          onDone: (confidence: number) => {
            finalConfidence = confidence;
            // 流式完成，添加最终消息
            const answerMessage: Message = {
              id: streamingMessageId,
              type: 'answer',
              content: fullContent,
              timestamp: new Date(),
              confidence: finalConfidence,
              isStreaming: false,
            };
            setMessages(prev => [...prev, answerMessage]);
            setStreamingContent('');
            setLoading(false);
          },
          onError: (errorMsg: string) => {
            setError(errorMsg);
            setStreamingContent('');
            setLoading(false);
          },
        }
      );
    } catch (err) {
      setError(handleApiError(err));
      setStreamingContent('');
      setLoading(false);
    }
  };

  const getConfidenceLabel = (confidence: number): string => {
    if (confidence >= 0.8) return t('confidence.high');
    if (confidence >= 0.5) return t('confidence.medium');
    return t('confidence.low');
  };

  return (
    <div className="qa-interface">
      <div className="qa-header">
        <h2>{`💬 ${t('title')}`}</h2>
        <p>{t('subtitle')}</p>
      </div>

      <div className="qa-content">
        {!isAuthenticated && (
          <div className="info-banner" style={{
            padding: '12px 16px',
            marginBottom: '16px',
            backgroundColor: '#fff3cd',
            border: '1px solid #ffc107',
            borderRadius: '8px',
            color: '#856404',
            fontSize: '14px'
          }}>
            <>{t('anonymousHint')}<a href="/login" style={{ color: '#0066cc', marginLeft: '8px' }}>{t('loginPrompt')}</a> {t('loginBenefit')}</>
          </div>
        )}
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="empty-state">
              <span className="empty-icon">{t('emptyState.icon')}</span>
              <p>{t('emptyState.message')}</p>
              <div className="suggestion-chips">
                <button onClick={() => setQuestion(t('emptyState.suggestions.recursion'))}>
                  {t('emptyState.suggestions.recursion')}
                </button>
                <button onClick={() => setQuestion(t('emptyState.suggestions.bigO'))}>
                  {t('emptyState.suggestions.bigO')}
                </button>
                <button onClick={() => setQuestion(t('emptyState.suggestions.debug'))}>
                  {t('emptyState.suggestions.debug')}
                </button>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.type}`}>
              <div className="message-avatar">
                {msg.type === 'question' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                {msg.type === 'answer' ? (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code({ node, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '');
                        const isInline = !match && !className;
                        return !isInline && match ? (
                          <SyntaxHighlighter
                            style={codeStyle}
                            language={match[1]}
                            PreTag="div"
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        );
                      },
                      // 自定义表格样式
                      table({ children }) {
                        return (
                          <div className="markdown-table-wrapper">
                            <table>{children}</table>
                          </div>
                        );
                      },
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  <p>{msg.content}</p>
                )}
                <div className="message-meta">
                  <span className="message-time">
                    {msg.timestamp.toLocaleTimeString()}
                  </span>
                  {msg.confidence !== undefined && (
                    <span className={`confidence-badge ${msg.confidence >= 0.8 ? 'high' : msg.confidence >= 0.5 ? 'medium' : 'low'}`}>
                      {getConfidenceLabel(msg.confidence)}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}

          {/* 流式内容显示 */}
          {loading && streamingContent && (
            <div className="message answer streaming">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      const isInline = !match && !className;
                      return !isInline && match ? (
                        <SyntaxHighlighter
                          style={codeStyle}
                          language={match[1]}
                          PreTag="div"
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                    table({ children }) {
                      return (
                        <div className="markdown-table-wrapper">
                          <table>{children}</table>
                        </div>
                      );
                    },
                  }}
                >
                  {streamingContent}
                </ReactMarkdown>
                <span className="streaming-cursor">▊</span>
              </div>
            </div>
          )}

          {/* 等待开始时显示 */}
          {loading && !streamingContent && (
            <div className="message answer loading">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <LoadingSpinner size="small" message={t('loading')} />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {error && <ErrorMessage message={error} />}

        <form className="input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder={t('input.placeholder')}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !question.trim()}>
            {t('input.send')}
          </button>
        </form>
      </div>
    </div>
  );
};

export default QAInterface;

