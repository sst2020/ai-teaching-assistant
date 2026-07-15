import React, { useState, useCallback } from 'react';
import { UploadedFile } from '../../types/plagiarism';

interface BatchUploadProps {
  onFilesReady: (files: UploadedFile[]) => void;
  isAnalyzing: boolean;
}

const BatchUpload: React.FC<BatchUploadProps> = ({ onFilesReady, isAnalyzing }) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);

  const readFileContent = async (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  };

  const extractStudentInfo = (filename: string): { id: string; name: string } => {
    // 尝试从文件名提取学生信息，格式：学号_姓名.py 或 姓名_学号.py
    const nameWithoutExt = filename.replace(/\.[^/.]+$/, '');
    const parts = nameWithoutExt.split(/[_-]/);
    
    if (parts.length >= 2) {
      // 假设第一部分是学号，第二部分是姓名
      return { id: parts[0], name: parts[1] };
    }
    return { id: nameWithoutExt, name: nameWithoutExt };
  };

  const handleFiles = useCallback(async (fileList: FileList) => {
    const newFiles: UploadedFile[] = [];
    
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      if (!file.name.endsWith('.py') && !file.name.endsWith('.txt')) {
        continue; // 只接受 Python 和文本文件
      }
      
      const { id, name } = extractStudentInfo(file.name);
      const uploadedFile: UploadedFile = {
        file,
        studentId: id,
        studentName: name,
        code: '',
        status: 'reading',
      };
      
      try {
        uploadedFile.code = await readFileContent(file);
        uploadedFile.status = 'ready';
      } catch {
        uploadedFile.status = 'error';
        uploadedFile.error = '文件读取失败';
      }
      
      newFiles.push(uploadedFile);
    }
    
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  const updateStudentInfo = (index: number, field: 'studentId' | 'studentName', value: string) => {
    setFiles(prev => prev.map((f, i) => 
      i === index ? { ...f, [field]: value } : f
    ));
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleStartAnalysis = () => {
    const readyFiles = files.filter(f => f.status === 'ready');
    if (readyFiles.length >= 2) {
      onFilesReady(readyFiles);
    }
  };

  const readyCount = files.filter(f => f.status === 'ready').length;

  return (
    <div className="batch-upload">
      <div
        className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="upload-icon">📁</div>
        <p>拖拽文件到此处，或点击选择文件</p>
        <p className="upload-hint">支持 .py 和 .txt 文件，文件名格式：学号_姓名.py</p>
        <input
          type="file"
          multiple
          accept=".py,.txt"
          onChange={handleInputChange}
          className="file-input"
        />
      </div>

      {files.length > 0 && (
        <div className="file-list">
          <h4>已上传文件 ({readyCount}/{files.length})</h4>
          <div className="file-table">
            {files.map((f, index) => (
              <div key={index} className={`file-row ${f.status}`}>
                <span className="file-name">{f.file.name}</span>
                <input
                  type="text"
                  value={f.studentId}
                  onChange={(e) => updateStudentInfo(index, 'studentId', e.target.value)}
                  placeholder="学号"
                  className="student-input"
                />
                <input
                  type="text"
                  value={f.studentName}
                  onChange={(e) => updateStudentInfo(index, 'studentName', e.target.value)}
                  placeholder="姓名"
                  className="student-input"
                />
                <span className={`status-badge ${f.status}`}>
                  {f.status === 'ready' ? '✓' : f.status === 'error' ? '✗' : '...'}
                </span>
                <button onClick={() => removeFile(index)} className="remove-btn">×</button>
              </div>
            ))}
          </div>
        </div>
      )}

      <button
        className="analyze-btn"
        onClick={handleStartAnalysis}
        disabled={readyCount < 2 || isAnalyzing}
      >
        {isAnalyzing ? '分析中...' : `开始分析 (${readyCount} 份作业)`}
      </button>
    </div>
  );
};

export default BatchUpload;

