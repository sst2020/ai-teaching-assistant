import React, { useState, useRef } from 'react';
import { analyzeProjectReport } from '../../services/api';
import {
  ReportAnalysisRequest,
  ReportAnalysisResponse,
  ReportFileType,
} from '../../types/reportAnalysis';
import './ReportAnalysis.css';

type TabType = 'upload' | 'structure' | 'quality' | 'logic' | 'suggestions';

const ReportAnalysis: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('upload');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<ReportAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [textContent, setTextContent] = useState('');
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAnalyze = async (content: string, name: string, fileType: ReportFileType) => {
    setIsAnalyzing(true);
    setError(null);
    try {
      const request: ReportAnalysisRequest = {
        file_name: name,
        file_type: fileType,
        content,
      };
      const resp = await analyzeProjectReport(request);
      setResult(resp);
      setActiveTab('structure');
    } catch (e) {
      setError(e instanceof Error ? e.message : '分析失败，请稍后重试');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setTextContent(content);
    };
    reader.readAsText(file);
  };

  const handleSubmit = () => {
    if (!textContent.trim()) {
      setError('请输入或上传报告内容');
      return;
    }
    // 根据文件扩展名确定类型，默认为 markdown
    let fileType: ReportFileType = 'markdown';
    if (fileName.endsWith('.pdf')) {
      fileType = 'pdf';
    } else if (fileName.endsWith('.docx')) {
      fileType = 'docx';
    }
    handleAnalyze(textContent, fileName || 'report.md', fileType);
  };

  return (
    <div className="report-analysis">
      <div className="page-header">
        <h1>📑 项目报告智能分析系统</h1>
        <p>自动解析项目报告结构，评估质量并生成智能修改建议</p>
      </div>

      <div className="tab-nav">
        <button
          className={`tab-btn ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          上传与解析
        </button>
        <button
          className={`tab-btn ${activeTab === 'structure' ? 'active' : ''} ${!result ? 'disabled' : ''}`}
          disabled={!result}
          onClick={() => result && setActiveTab('structure')}
        >
          报告结构
        </button>
        <button
          className={`tab-btn ${activeTab === 'quality' ? 'active' : ''} ${!result ? 'disabled' : ''}`}
          disabled={!result}
          onClick={() => result && setActiveTab('quality')}
        >
          质量评估
        </button>
        <button
          className={`tab-btn ${activeTab === 'logic' ? 'active' : ''} ${!result ? 'disabled' : ''}`}
          disabled={!result}
          onClick={() => result && setActiveTab('logic')}
        >
          逻辑与创新
        </button>
        <button
          className={`tab-btn ${activeTab === 'suggestions' ? 'active' : ''} ${!result ? 'disabled' : ''}`}
          disabled={!result}
          onClick={() => result && setActiveTab('suggestions')}
        >
          修改建议
        </button>
      </div>

      {error && (
        <div className="error-message">
          <span>❌ {error}</span>
          <button onClick={() => setError(null)}>关闭</button>
        </div>
      )}

      <div className="tab-content">
        {activeTab === 'upload' && (
          <div className="upload-section">
            <div className="upload-area">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept=".txt,.md,.markdown"
                style={{ display: 'none' }}
              />
              <button
                className="upload-btn"
                onClick={() => fileInputRef.current?.click()}
                disabled={isAnalyzing}
              >
                📁 选择文件
              </button>
              {fileName && <span className="file-name">{fileName}</span>}
            </div>
            <div className="text-input-area">
              <textarea
                placeholder="或直接粘贴报告内容..."
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                disabled={isAnalyzing}
                rows={10}
              />
            </div>
            <button
              className="analyze-btn"
              onClick={handleSubmit}
              disabled={isAnalyzing || !textContent.trim()}
            >
              {isAnalyzing ? '⏳ 分析中...' : '🔍 开始分析'}
            </button>
          </div>
        )}

        {activeTab === 'structure' && result && (
          <div className="result-section">
            <h3>📋 报告结构分析</h3>
            <pre>{JSON.stringify(result.parsed, null, 2)}</pre>
          </div>
        )}

        {activeTab === 'quality' && result && (
          <div className="result-section">
            <h3>📊 质量评估</h3>
            <pre>{JSON.stringify(result.quality, null, 2)}</pre>
          </div>
        )}

        {activeTab === 'logic' && result && (
          <div className="result-section">
            <h3>💡 逻辑与创新分析</h3>
            <pre>{JSON.stringify({ logic: result.logic, innovation: result.innovation }, null, 2)}</pre>
          </div>
        )}

        {activeTab === 'suggestions' && result && (
          <div className="result-section">
            <h3>✏️ 修改建议</h3>
            <pre>{JSON.stringify(result.suggestions, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportAnalysis;
