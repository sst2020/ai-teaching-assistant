import React, { useState, useMemo, useCallback } from 'react';
import { SubmissionComparison, SimilarityMatrix } from '../../types/plagiarism';

interface SuspiciousListProps {
  pairs: SubmissionComparison[];
  matrix: SimilarityMatrix;
  onPairClick?: (pair: SubmissionComparison) => void;
}

type SortField = 'similarity' | 'student1' | 'student2';
type SortOrder = 'asc' | 'desc';

const SuspiciousList: React.FC<SuspiciousListProps> = ({ pairs, matrix, onPairClick }) => {
  const [sortField, setSortField] = useState<SortField>('similarity');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [filter, setFilter] = useState('');

  const getStudentName = useCallback((studentId: string): string => {
    const index = matrix.student_ids.indexOf(studentId);
    return index >= 0 ? (matrix.student_names[index] || studentId) : studentId;
  }, [matrix.student_ids, matrix.student_names]);

  const getSimilarityLevel = (score: number): { label: string; className: string } => {
    if (score >= 0.9) return { label: '极高', className: 'very-high' };
    if (score >= 0.8) return { label: '高', className: 'high' };
    if (score >= 0.7) return { label: '中高', className: 'medium-high' };
    return { label: '中', className: 'medium' };
  };

  const sortedAndFilteredPairs = useMemo(() => {
    let result = [...pairs];

    // 过滤
    if (filter) {
      const lowerFilter = filter.toLowerCase();
      result = result.filter(pair => {
        const name1 = getStudentName(pair.student_id_1).toLowerCase();
        const name2 = getStudentName(pair.student_id_2).toLowerCase();
        return name1.includes(lowerFilter) || name2.includes(lowerFilter) ||
               pair.student_id_1.toLowerCase().includes(lowerFilter) ||
               pair.student_id_2.toLowerCase().includes(lowerFilter);
      });
    }

    // 排序
    result.sort((a, b) => {
      let comparison = 0;
      switch (sortField) {
        case 'similarity':
          comparison = a.similarity_score - b.similarity_score;
          break;
        case 'student1':
          comparison = getStudentName(a.student_id_1).localeCompare(getStudentName(b.student_id_1));
          break;
        case 'student2':
          comparison = getStudentName(a.student_id_2).localeCompare(getStudentName(b.student_id_2));
          break;
      }
      return sortOrder === 'desc' ? -comparison : comparison;
    });

    return result;
  }, [pairs, sortField, sortOrder, filter, getStudentName]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return '↕️';
    return sortOrder === 'desc' ? '↓' : '↑';
  };

  return (
    <div className="suspicious-list">
      <div className="list-header">
        <h3>⚠️ 可疑相似作业列表</h3>
        <div className="list-controls">
          <input
            type="text"
            placeholder="搜索学生..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="search-input"
          />
          <span className="result-count">
            共 {sortedAndFilteredPairs.length} 对
          </span>
        </div>
      </div>

      <div className="list-table">
        <div className="table-header">
          <div 
            className="header-cell sortable" 
            onClick={() => handleSort('student1')}
          >
            学生1 {getSortIcon('student1')}
          </div>
          <div 
            className="header-cell sortable" 
            onClick={() => handleSort('student2')}
          >
            学生2 {getSortIcon('student2')}
          </div>
          <div 
            className="header-cell sortable" 
            onClick={() => handleSort('similarity')}
          >
            相似度 {getSortIcon('similarity')}
          </div>
          <div className="header-cell">分析备注</div>
          <div className="header-cell">操作</div>
        </div>

        <div className="table-body">
          {sortedAndFilteredPairs.length === 0 ? (
            <div className="empty-message">
              {filter ? '没有匹配的结果' : '没有发现可疑的相似作业 🎉'}
            </div>
          ) : (
            sortedAndFilteredPairs.map((pair, index) => {
              const level = getSimilarityLevel(pair.similarity_score);
              return (
                <div 
                  key={index} 
                  className={`table-row ${level.className}`}
                  onClick={() => onPairClick?.(pair)}
                >
                  <div className="cell">
                    <span className="student-name">{getStudentName(pair.student_id_1)}</span>
                    <span className="student-id">{pair.student_id_1}</span>
                  </div>
                  <div className="cell">
                    <span className="student-name">{getStudentName(pair.student_id_2)}</span>
                    <span className="student-id">{pair.student_id_2}</span>
                  </div>
                  <div className="cell">
                    <span className={`similarity-badge ${level.className}`}>
                      {(pair.similarity_score * 100).toFixed(1)}%
                    </span>
                    <span className="level-label">{level.label}</span>
                  </div>
                  <div className="cell notes">
                    {pair.analysis_notes || '-'}
                  </div>
                  <div className="cell">
                    <button className="detail-btn">查看详情</button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default SuspiciousList;

