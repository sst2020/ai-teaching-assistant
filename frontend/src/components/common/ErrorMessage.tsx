import React from 'react';
import './ErrorMessage.css';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry, onDismiss }) => {
  return (
    <div className="error-message-container">
      <div className="error-icon">⚠️</div>
      <p className="error-text">{message}</p>
      {onRetry && (
        <button className="retry-button" onClick={onRetry}>
          Try Again
        </button>
      )}
      {onDismiss && (
        <button className="dismiss-button" onClick={onDismiss}>
          Dismiss
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;

