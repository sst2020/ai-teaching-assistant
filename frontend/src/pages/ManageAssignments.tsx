/**
 * 作业管理页面
 * 
 * 功能:
 * - 作业列表展示（分页、筛选）
 * - 创建新作业
 * - 编辑现有作业
 * - 删除作业
 * - 发布/取消发布作业
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  getAssignments,
  getAssignment,
} from '../services/api';
import {
  Assignment,
  AssignmentType,
  AssignmentFilters,
} from '../types/assignment';
import './ManageAssignments.css';

interface AssignmentFormData {
  title: string;
  description: string;
  instructions: string;
  assignment_type: AssignmentType;
  max_score: number;
  due_date: string;
  is_published: boolean;
  allow_late_submission: boolean;
  late_penalty_percent: number;
}

const initialFormData: AssignmentFormData = {
  title: '',
  description: '',
  instructions: '',
  assignment_type: 'code',
  max_score: 100,
  due_date: '',
  is_published: false,
  allow_late_submission: true,
  late_penalty_percent: 10,
};

const ManageAssignments: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const editId = searchParams.get('edit');

  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState<AssignmentFilters>({
    page: 1,
    page_size: 10,
  });

  // 表单状态
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<AssignmentFormData>(initialFormData);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // 加载作业列表
  const loadAssignments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getAssignments({ ...filters, page });
      setAssignments(response.items || response.assignments || []);
      setTotalPages(response.total_pages || 1);
    } catch (err) {
      setError('加载作业列表失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  // 加载单个作业（编辑模式）
  const loadAssignment = useCallback(async (id: string) => {
    try {
      const assignment = await getAssignment(id);
      setFormData({
        title: assignment.title,
        description: assignment.description,
        instructions: assignment.instructions,
        assignment_type: assignment.assignment_type,
        max_score: assignment.max_score,
        due_date: assignment.due_date.slice(0, 16), // 格式化为 datetime-local
        is_published: assignment.is_published,
        allow_late_submission: assignment.allow_late_submission,
        late_penalty_percent: assignment.late_penalty_percent || 10,
      });
      setEditingId(id);
      setShowForm(true);
    } catch (err) {
      setError('加载作业详情失败');
      console.error(err);
    }
  }, []);

  useEffect(() => {
    loadAssignments();
  }, [loadAssignments]);

  useEffect(() => {
    if (editId) {
      loadAssignment(editId);
    }
  }, [editId, loadAssignment]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      // TODO: 调用创建/更新 API
      console.log('提交表单:', formData, editingId ? '更新' : '创建');
      
      // 模拟成功
      setShowForm(false);
      setFormData(initialFormData);
      setEditingId(null);
      loadAssignments();
    } catch (err) {
      setError('保存作业失败');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除这个作业吗？此操作不可撤销。')) {
      return;
    }
    try {
      // TODO: 调用删除 API
      console.log('删除作业:', id);
      loadAssignments();
    } catch (err) {
      setError('删除作业失败');
      console.error(err);
    }
  };

  const openCreateForm = () => {
    setFormData(initialFormData);
    setEditingId(null);
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setFormData(initialFormData);
    setEditingId(null);
    navigate('/manage-assignments', { replace: true });
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getTypeLabel = (type: AssignmentType) => {
    const labels: Record<AssignmentType, string> = {
      code: '💻 代码',
      essay: '📝 论文',
      quiz: '❓ 测验',
      project: '🎯 项目',
    };
    return labels[type] || type;
  };

  return (
    <div className="manage-assignments">
      <header className="page-header">
        <div className="header-left">
          <button className="btn-back" onClick={() => navigate('/teacher')}>
            ← 返回
          </button>
          <h1>📋 作业管理</h1>
        </div>
        <button className="btn-primary" onClick={openCreateForm}>
          ➕ 新建作业
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {/* 筛选栏 */}
      <div className="filters-bar">
        <select
          value={filters.assignment_type || ''}
          onChange={(e) => setFilters({ ...filters, assignment_type: e.target.value as AssignmentType || undefined })}
        >
          <option value="">全部类型</option>
          <option value="code">代码作业</option>
          <option value="essay">论文作业</option>
          <option value="quiz">测验</option>
          <option value="project">项目</option>
        </select>
        <select
          value={filters.is_published === undefined ? '' : filters.is_published.toString()}
          onChange={(e) => setFilters({ ...filters, is_published: e.target.value === '' ? undefined : e.target.value === 'true' })}
        >
          <option value="">全部状态</option>
          <option value="true">已发布</option>
          <option value="false">草稿</option>
        </select>
      </div>

      {/* 作业列表 */}
      <div className="assignments-list">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : assignments.length === 0 ? (
          <div className="empty-state">
            <p>暂无作业</p>
            <button className="btn-primary" onClick={openCreateForm}>
              创建第一个作业
            </button>
          </div>
        ) : (
          <>
            <table className="assignments-table">
              <thead>
                <tr>
                  <th>作业标题</th>
                  <th>类型</th>
                  <th>满分</th>
                  <th>截止日期</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {assignments.map((assignment) => (
                  <tr key={assignment.id}>
                    <td className="title-cell">
                      <span className="assignment-title">{assignment.title}</span>
                      <span className="assignment-desc">{assignment.description.slice(0, 50)}...</span>
                    </td>
                    <td>
                      <span className={`type-badge ${assignment.assignment_type}`}>
                        {getTypeLabel(assignment.assignment_type)}
                      </span>
                    </td>
                    <td>{assignment.max_score}</td>
                    <td>{formatDate(assignment.due_date)}</td>
                    <td>
                      {assignment.is_published ? (
                        <span className="status-badge published">已发布</span>
                      ) : (
                        <span className="status-badge draft">草稿</span>
                      )}
                    </td>
                    <td className="actions-cell">
                      <button
                        className="btn-icon"
                        onClick={() => navigate(`/grading?assignment=${assignment.id}`)}
                        title="批改"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-icon"
                        onClick={() => loadAssignment(String(assignment.id))}
                        title="编辑"
                      >
                        ⚙️
                      </button>
                      <button
                        className="btn-icon danger"
                        onClick={() => handleDelete(String(assignment.id))}
                        title="删除"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* 分页 */}
            <div className="pagination">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                上一页
              </button>
              <span>第 {page} / {totalPages} 页</span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                下一页
              </button>
            </div>
          </>
        )}
      </div>

      {/* 创建/编辑表单模态框 */}
      {showForm && (
        <div className="modal-overlay" onClick={closeForm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingId ? '编辑作业' : '新建作业'}</h2>
              <button className="btn-close" onClick={closeForm}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="title">作业标题 *</label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  required
                  placeholder="输入作业标题"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="assignment_type">作业类型 *</label>
                  <select
                    id="assignment_type"
                    name="assignment_type"
                    value={formData.assignment_type}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="code">💻 代码作业</option>
                    <option value="essay">📝 论文作业</option>
                    <option value="quiz">❓ 测验</option>
                    <option value="project">🎯 项目</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="max_score">满分 *</label>
                  <input
                    type="number"
                    id="max_score"
                    name="max_score"
                    value={formData.max_score}
                    onChange={handleInputChange}
                    required
                    min="1"
                    max="1000"
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="description">作业描述</label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="简要描述作业内容"
                />
              </div>

              <div className="form-group">
                <label htmlFor="instructions">详细说明</label>
                <textarea
                  id="instructions"
                  name="instructions"
                  value={formData.instructions}
                  onChange={handleInputChange}
                  rows={5}
                  placeholder="详细的作业要求和评分标准"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="due_date">截止日期 *</label>
                  <input
                    type="datetime-local"
                    id="due_date"
                    name="due_date"
                    value={formData.due_date}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="late_penalty_percent">迟交扣分 (%)</label>
                  <input
                    type="number"
                    id="late_penalty_percent"
                    name="late_penalty_percent"
                    value={formData.late_penalty_percent}
                    onChange={handleInputChange}
                    min="0"
                    max="100"
                  />
                </div>
              </div>

              <div className="form-checkboxes">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="allow_late_submission"
                    checked={formData.allow_late_submission}
                    onChange={handleInputChange}
                  />
                  允许迟交
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="is_published"
                    checked={formData.is_published}
                    onChange={handleInputChange}
                  />
                  立即发布
                </label>
              </div>

              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={closeForm}>
                  取消
                </button>
                <button type="submit" className="btn-primary" disabled={submitting}>
                  {submitting ? '保存中...' : (editingId ? '更新作业' : '创建作业')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ManageAssignments;

