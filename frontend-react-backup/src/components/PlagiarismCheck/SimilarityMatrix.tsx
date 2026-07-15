import React, { useMemo } from 'react';
import { SimilarityMatrix as SimilarityMatrixType, SimilarityMatrixEntry } from '../../types/plagiarism';

interface SimilarityMatrixProps {
  data: SimilarityMatrixType;
  onCellClick?: (entry: SimilarityMatrixEntry) => void;
}

const SimilarityMatrixComponent: React.FC<SimilarityMatrixProps> = ({ data, onCellClick }) => {
  const { matrix, student_names, student_ids, threshold } = data;

  // 根据相似度值获取颜色
  const getColor = (value: number): string => {
    if (value >= 0.9) return '#dc2626'; // 红色 - 极高
    if (value >= 0.7) return '#f97316'; // 橙色 - 高
    if (value >= 0.5) return '#eab308'; // 黄色 - 中
    if (value >= 0.3) return '#84cc16'; // 浅绿 - 低
    return '#22c55e'; // 绿色 - 无
  };

  // 获取显示名称（优先使用姓名，否则使用ID）
  const getDisplayName = (index: number): string => {
    return student_names[index] || student_ids[index] || `学生${index + 1}`;
  };

  // 查找对应的entry
  const findEntry = (i: number, j: number): SimilarityMatrixEntry | undefined => {
    return data.entries.find(
      e => (e.student_id_1 === student_ids[i] && e.student_id_2 === student_ids[j]) ||
           (e.student_id_1 === student_ids[j] && e.student_id_2 === student_ids[i])
    );
  };

  const handleCellClick = (i: number, j: number) => {
    if (i === j) return;
    const entry = findEntry(i, j);
    if (entry && onCellClick) {
      onCellClick(entry);
    }
  };

  // 计算统计信息
  const stats = useMemo(() => {
    let maxSim = 0;
    let avgSim = 0;
    let count = 0;
    let flaggedCount = 0;

    for (let i = 0; i < matrix.length; i++) {
      for (let j = i + 1; j < matrix.length; j++) {
        const sim = matrix[i][j];
        maxSim = Math.max(maxSim, sim);
        avgSim += sim;
        count++;
        if (sim >= threshold) flaggedCount++;
      }
    }

    return {
      maxSimilarity: maxSim,
      avgSimilarity: count > 0 ? avgSim / count : 0,
      flaggedPairs: flaggedCount,
      totalPairs: count,
    };
  }, [matrix, threshold]);

  return (
    <div className="similarity-matrix">
      <div className="matrix-header">
        <h3>📊 相似度矩阵热力图</h3>
        <div className="matrix-stats">
          <span>最高相似度: <strong>{(stats.maxSimilarity * 100).toFixed(1)}%</strong></span>
          <span>平均相似度: <strong>{(stats.avgSimilarity * 100).toFixed(1)}%</strong></span>
          <span>可疑对数: <strong className="flagged">{stats.flaggedPairs}</strong></span>
        </div>
      </div>

      <div className="matrix-container">
        <div className="matrix-grid" style={{ 
          gridTemplateColumns: `80px repeat(${matrix.length}, 1fr)` 
        }}>
          {/* 空白角落 */}
          <div className="matrix-cell corner"></div>
          
          {/* 列标题 */}
          {student_ids.map((_, index) => (
            <div key={`col-${index}`} className="matrix-cell header-cell">
              <span className="header-text" title={getDisplayName(index)}>
                {getDisplayName(index).slice(0, 4)}
              </span>
            </div>
          ))}

          {/* 行数据 */}
          {matrix.map((row, i) => (
            <React.Fragment key={`row-${i}`}>
              {/* 行标题 */}
              <div className="matrix-cell header-cell row-header">
                <span className="header-text" title={getDisplayName(i)}>
                  {getDisplayName(i).slice(0, 6)}
                </span>
              </div>
              
              {/* 数据单元格 */}
              {row.map((value, j) => {
                const isSelf = i === j;
                const isFlagged = !isSelf && value >= threshold;
                
                return (
                  <div
                    key={`cell-${i}-${j}`}
                    className={`matrix-cell data-cell ${isSelf ? 'self' : ''} ${isFlagged ? 'flagged' : ''}`}
                    style={{ backgroundColor: isSelf ? '#e5e7eb' : getColor(value) }}
                    onClick={() => handleCellClick(i, j)}
                    title={isSelf ? '自身' : `${getDisplayName(i)} vs ${getDisplayName(j)}: ${(value * 100).toFixed(1)}%`}
                  >
                    {!isSelf && (
                      <span className="cell-value">{(value * 100).toFixed(0)}</span>
                    )}
                  </div>
                );
              })}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* 图例 */}
      <div className="matrix-legend">
        <span className="legend-title">相似度:</span>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#22c55e' }}></span>
          <span>0-30%</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#84cc16' }}></span>
          <span>30-50%</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#eab308' }}></span>
          <span>50-70%</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#f97316' }}></span>
          <span>70-90%</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#dc2626' }}></span>
          <span>90%+</span>
        </div>
      </div>
    </div>
  );
};

export default SimilarityMatrixComponent;

