/**
 * 知识库管理组件
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  KnowledgeBaseEntry,
  KnowledgeBaseCategory,
  DifficultyLevel,
  CATEGORY_LABELS,
  DIFFICULTY_LABELS,
} from '../../types/knowledgeBase';
import {
  getKnowledgeBaseEntries,
  searchKnowledgeBase,
  deleteKnowledgeBaseEntry,
  getKnowledgeBaseStats,
} from '../../services/api';
import styles from './KnowledgeBase.module.css';

interface KnowledgeBaseProps {
  onSelectEntry?: (entry: KnowledgeBaseEntry) => void;
  showManagement?: boolean;
}

const KnowledgeBase: React.FC<KnowledgeBaseProps> = ({
  onSelectEntry,
  showManagement = true,
}) => {
  const [entries, setEntries] = useState<KnowledgeBaseEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<number | ''>('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [stats, setStats] = useState<{ total: number; active: number } | null>(null);

  const loadEntries = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getKnowledgeBaseEntries(
        page,
        20,
        selectedCategory || undefined,
        selectedDifficulty || undefined
      );
      setEntries(response.entries);
      setTotalPages(Math.ceil(response.total / 20));
    } catch (err) {
      setError('加载知识库失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, selectedCategory, selectedDifficulty]);

  const loadStats = useCallback(async () => {
    try {
      const response = await getKnowledgeBaseStats();
      setStats({ total: response.total_entries, active: response.active_entries });
    } catch (err) {
      console.error('加载统计失败', err);
    }
  }, []);

  useEffect(() => {
    loadEntries();
    loadStats();
  }, [loadEntries, loadStats]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadEntries();
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await searchKnowledgeBase({
        query: searchQuery,
        category: selectedCategory as KnowledgeBaseCategory || undefined,
        difficulty_level: selectedDifficulty as DifficultyLevel || undefined,
        limit: 20,
      });
      setEntries(response.results.map(r => ({
        entry_id: r.entry_id,
        category: r.category,
        question: r.question,
        answer: r.answer,
        keywords: r.keywords,
        difficulty_level: r.difficulty_level,
        language: null,
        view_count: 0,
        helpful_count: 0,
        is_active: true,
        created_at: '',
        updated_at: '',
      })));
      setTotalPages(1);
    } catch (err) {
      setError('搜索失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (entryId: string) => {
    if (!window.confirm('确定要删除这个条目吗？')) return;
    try {
      await deleteKnowledgeBaseEntry(entryId);
      loadEntries();
      loadStats();
    } catch (err) {
      setError('删除失败');
      console.error(err);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>📚 知识库管理</h2>
        {stats && (
          <div className={styles.stats}>
            <span>总条目: {stats.total}</span>
            <span>启用: {stats.active}</span>
          </div>
        )}
      </div>

      <div className={styles.filters}>
        <div className={styles.searchBox}>
          <input
            type="text"
            placeholder="搜索问题..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch}>搜索</button>
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => { setSelectedCategory(e.target.value); setPage(1); }}
        >
          <option value="">全部分类</option>
          {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
        <select
          value={selectedDifficulty}
          onChange={(e) => { setSelectedDifficulty(e.target.value ? Number(e.target.value) : ''); setPage(1); }}
        >
          <option value="">全部难度</option>
          {Object.entries(DIFFICULTY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>

      {error && <div className={styles.error}>{error}</div>}
      {loading && <div className={styles.loading}>加载中...</div>}

      <div className={styles.entryList}>
        {entries.map((entry) => (
          <div
            key={entry.entry_id}
            className={styles.entryCard}
            onClick={() => onSelectEntry?.(entry)}
          >
            <div className={styles.entryHeader}>
              <span className={styles.category}>
                {CATEGORY_LABELS[entry.category] || entry.category}
              </span>
              <span className={styles.difficulty}>
                {DIFFICULTY_LABELS[entry.difficulty_level]}
              </span>
              {entry.language && <span className={styles.language}>{entry.language}</span>}
            </div>
            <h3 className={styles.question}>{entry.question}</h3>
            <p className={styles.answer}>{entry.answer.substring(0, 150)}...</p>
            <div className={styles.entryFooter}>
              <div className={styles.keywords}>
                {entry.keywords.slice(0, 5).map((kw, i) => (
                  <span key={i} className={styles.keyword}>{kw}</span>
                ))}
              </div>
              <div className={styles.meta}>
                <span>👁 {entry.view_count}</span>
                <span>👍 {entry.helpful_count}</span>
              </div>
              {showManagement && (
                <button
                  className={styles.deleteBtn}
                  onClick={(e) => { e.stopPropagation(); handleDelete(entry.entry_id); }}
                >
                  删除
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div className={styles.pagination}>
          <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}>上一页</button>
          <span>{page} / {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>下一页</button>
        </div>
      )}
    </div>
  );
};

export default KnowledgeBase;

