import React, { useState } from 'react';
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

  const handleAnalyze = async (content: string, fileName: string, fileType: ReportFileType) => {
    setIsAnalyzing(true);
    setError(null);
    try {
      const request: ReportAnalysisRequest = {
        file_name: fileName,
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
        {/* TODO: 拆分为 Upload / Structure / Quality / Logic / Suggestions 子组件 */}
        <div>
          暂未实现详细子视图，此处已打通后端 API 调用链，可在后续步骤细化 UI。
        </div>
      </div>
    </div>
  );
};

export default ReportAnalysis;
