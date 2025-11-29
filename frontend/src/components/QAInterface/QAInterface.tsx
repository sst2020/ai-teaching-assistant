import React, { useState } from 'react';
import { askQuestion, handleApiError } from '../../services/api';
import { QuestionResponse } from '../../types/api';
import { LoadingSpinner, ErrorMessage } from '../common';
import './QAInterface.css';

interface Message {
  id: string;
  type: 'question' | 'answer';
  content: string;
  timestamp: Date;
  confidence?: number;
}

const QAInterface: React.FC = () => {
  const [question, setQuestion] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) return;

    const questionMessage: Message = {
      id: Date.now().toString(),
      type: 'question',
      content: question,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, questionMessage]);
    setQuestion('');
    setLoading(true);
    setError(null);

    try {
      const response: QuestionResponse = await askQuestion({
        student_id: 'demo-student',
        course_id: 'demo-course',
        question: question,
      });

      const answerMessage: Message = {
        id: response.question_id,
        type: 'answer',
        content: response.ai_answer,
        timestamp: new Date(),
        confidence: response.confidence,
      };

      setMessages(prev => [...prev, answerMessage]);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceLabel = (confidence: number): string => {
    if (confidence >= 0.8) return 'High confidence';
    if (confidence >= 0.5) return 'Medium confidence';
    return 'Low confidence';
  };

  return (
    <div className="qa-interface">
      <div className="qa-header">
        <h2>💬 Q&A Assistant</h2>
        <p>Ask questions about programming, algorithms, or course material</p>
      </div>

      <div className="qa-content">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="empty-state">
              <span className="empty-icon">🤖</span>
              <p>Ask me anything about programming!</p>
              <div className="suggestion-chips">
                <button onClick={() => setQuestion('What is recursion?')}>
                  What is recursion?
                </button>
                <button onClick={() => setQuestion('Explain Big O notation')}>
                  Explain Big O notation
                </button>
                <button onClick={() => setQuestion('How do I debug Python code?')}>
                  How do I debug Python code?
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
                <p>{msg.content}</p>
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

          {loading && (
            <div className="message answer loading">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <LoadingSpinner size="small" message="Thinking..." />
              </div>
            </div>
          )}
        </div>

        {error && <ErrorMessage message={error} />}

        <form className="input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Type your question here..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !question.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default QAInterface;

