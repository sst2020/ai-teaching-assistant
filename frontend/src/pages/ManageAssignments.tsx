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
import { useTranslation } from 'react-i18next';
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
  const { t, i18n } = useTranslation('assignments');
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
      setError(t('loadError'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters, page, t]);

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
      setError(t('loadDetailError'));
      console.error(err);
    }
  }, [t]);

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
      setError(t('saveError'));
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm(t('deleteConfirm'))) {
      return;
    }
    try {
      // TODO: 调用删除 API
      console.log('删除作业:', id);
      loadAssignments();
    } catch (err) {
      setError(t('deleteError'));
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
    const locale = i18n.language === 'zh' ? 'zh-CN' : 'en-US';
    return date.toLocaleDateString(locale, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getTypeLabel = (type: AssignmentType) => {
    return t(`typeLabels.${type}`);
  };

  return (
    <div className="manage-assignments">
      <header className="page-header">
        <div className="header-left">
          <button className="btn-back" onClick={() => navigate('/teacher')}>
            {`← ${t('back')}`}
          </button>
          <h1>{`📋 ${t('title')}`}</h1>
        </div>
        <button className="btn-primary" onClick={openCreateForm}>
          {`➕ ${t('newAssignment')}`}
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {/* 筛选栏 */}
      <div className="filters-bar">
        <select
          value={filters.assignment_type || ''}
          onChange={(e) => setFilters({ ...filters, assignment_type: e.target.value as AssignmentType || undefined })}
        >
          <option value="">{t('filters.allTypes')}</option>
          <option value="code">{t('types.code')}</option>
          <option value="essay">{t('types.essay')}</option>
          <option value="quiz">{t('types.quiz')}</option>
          <option value="project">{t('types.project')}</option>
        </select>
        <select
          value={filters.is_published === undefined ? '' : filters.is_published.toString()}
          onChange={(e) => setFilters({ ...filters, is_published: e.target.value === '' ? undefined : e.target.value === 'true' })}
        >
          <option value="">{t('filters.allStatus')}</option>
          <option value="true">{t('filters.published')}</option>
          <option value="false">{t('filters.draft')}</option>
        </select>
      </div>

      {/* 作业列表 */}
      <div className="assignments-list">
        {loading ? (
          <div className="loading">{t('loading')}</div>
        ) : assignments.length === 0 ? (
          <div className="empty-state">
            <p>{t('empty.message')}</p>
            <button className="btn-primary" onClick={openCreateForm}>
              {t('empty.createFirst')}
            </button>
          </div>
        ) : (
          <>
            <table className="assignments-table">
              <thead>
                <tr>
                  <th>{t('table.title')}</th>
                  <th>{t('table.type')}</th>
                  <th>{t('table.maxScore')}</th>
                  <th>{t('table.dueDate')}</th>
                  <th>{t('table.status')}</th>
                  <th>{t('table.actions')}</th>
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
                        <span className="status-badge published">{t('status.published')}</span>
                      ) : (
                        <span className="status-badge draft">{t('status.draft')}</span>
                      )}
                    </td>
                    <td className="actions-cell">
                      <button
                        className="btn-icon"
                        onClick={() => navigate(`/grading?assignment=${assignment.id}`)}
                        title={t('actions.grade')}
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-icon"
                        onClick={() => loadAssignment(String(assignment.id))}
                        title={t('actions.edit')}
                      >
                        ⚙️
                      </button>
                      <button
                        className="btn-icon danger"
                        onClick={() => handleDelete(String(assignment.id))}
                        title={t('actions.delete')}
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
                {t('pagination.prev')}
              </button>
              <span>{t('pagination.pageInfo', { current: page, total: totalPages })}</span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                {t('pagination.next')}
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
              <h2>{editingId ? t('form.editTitle') : t('form.createTitle')}</h2>
              <button className="btn-close" onClick={closeForm}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="title">{t('form.title')} {t('form.titleRequired')}</label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  required
                  placeholder={t('form.titlePlaceholder')}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="assignment_type">{t('form.type')} {t('form.typeRequired')}</label>
                  <select
                    id="assignment_type"
                    name="assignment_type"
                    value={formData.assignment_type}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="code">{`💻 ${t('types.code')}`}</option>
                    <option value="essay">{`📝 ${t('types.essay')}`}</option>
                    <option value="quiz">{`❓ ${t('types.quiz')}`}</option>
                    <option value="project">{`🎯 ${t('types.project')}`}</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="max_score">{t('form.maxScore')} {t('form.maxScoreRequired')}</label>
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
                <label htmlFor="description">{t('form.description')}</label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder={t('form.descriptionPlaceholder')}
                />
              </div>

              <div className="form-group">
                <label htmlFor="instructions">{t('form.instructions')}</label>
                <textarea
                  id="instructions"
                  name="instructions"
                  value={formData.instructions}
                  onChange={handleInputChange}
                  rows={5}
                  placeholder={t('form.instructionsPlaceholder')}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="due_date">{t('form.dueDate')} {t('form.dueDateRequired')}</label>
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
                  <label htmlFor="late_penalty_percent">{t('form.latePenalty')}</label>
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
                  {t('form.allowLate')}
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="is_published"
                    checked={formData.is_published}
                    onChange={handleInputChange}
                  />
                  {t('form.publishNow')}
                </label>
              </div>

              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={closeForm}>
                  {t('form.cancel')}
                </button>
                <button type="submit" className="btn-primary" disabled={submitting}>
                  {submitting ? t('form.saving') : (editingId ? t('form.update') : t('form.create'))}
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

