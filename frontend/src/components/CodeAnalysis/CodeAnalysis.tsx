import React, { useState } from 'react';
import { analyzeCode, handleApiError } from '../../services/api';
import { CodeAnalysisResponse } from '../../types/api';
import { LoadingSpinner, ErrorMessage } from '../common';
import './CodeAnalysis.css';

const SAMPLE_CODE = `def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    """Calculate nth Fibonacci number."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
`;

const CodeAnalysis: React.FC = () => {
  const [code, setCode] = useState<string>(SAMPLE_CODE);
  const [language, setLanguage] = useState<string>('python');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CodeAnalysisResponse | null>(null);

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError('Please enter some code to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await analyzeCode({
        code,
        language,
        include_style: true,
        include_complexity: true,
        include_smells: true,
      });
      setResult(response);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return '#48bb78';
    if (score >= 60) return '#ecc94b';
    return '#f56565';
  };

  return (
    <div className="code-analysis">
      <div className="analysis-header">
        <h2>📊 Code Analysis</h2>
        <p>Analyze your Python code for style issues, complexity, and code smells</p>
      </div>

      <div className="analysis-content">
        <div className="code-input-section">
          <div className="input-header">
            <label htmlFor="code-input">Enter your code:</label>
            <select 
              value={language} 
              onChange={(e) => setLanguage(e.target.value)}
              className="language-select"
            >
              <option value="python">Python</option>
            </select>
          </div>
          <textarea
            id="code-input"
            className="code-textarea"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here..."
            rows={15}
          />
          <button 
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? 'Analyzing...' : '🔍 Analyze Code'}
          </button>
        </div>

        <div className="results-section">
          {loading && <LoadingSpinner message="Analyzing your code..." />}
          {error && <ErrorMessage message={error} onRetry={handleAnalyze} />}
          {result && (
            <div className="analysis-results">
              <div className="score-card">
                <div 
                  className="score-circle"
                  style={{ borderColor: getScoreColor(result.overall_quality_score) }}
                >
                  <span className="score-value">{result.overall_quality_score}</span>
                  <span className="score-label">Quality Score</span>
                </div>
              </div>

              <div className="metrics-grid">
                <div className="metric-card">
                  <h4>📈 Complexity</h4>
                  <div className="metric-value">
                    {result.complexity_metrics.cyclomatic_complexity}
                  </div>
                  <div className="metric-label">Cyclomatic Complexity</div>
                </div>
                <div className="metric-card">
                  <h4>📏 Lines of Code</h4>
                  <div className="metric-value">
                    {result.complexity_metrics.lines_of_code}
                  </div>
                  <div className="metric-label">Total Lines</div>
                </div>
                <div className="metric-card">
                  <h4>🔧 Functions</h4>
                  <div className="metric-value">
                    {result.complexity_metrics.function_count}
                  </div>
                  <div className="metric-label">Function Count</div>
                </div>
                <div className="metric-card">
                  <h4>⚠️ Style Issues</h4>
                  <div className="metric-value">
                    {result.style_analysis.total_issues}
                  </div>
                  <div className="metric-label">Total Issues</div>
                </div>
              </div>

              {result.recommendations.length > 0 && (
                <div className="recommendations">
                  <h4>💡 Recommendations</h4>
                  <ul>
                    {result.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CodeAnalysis;

