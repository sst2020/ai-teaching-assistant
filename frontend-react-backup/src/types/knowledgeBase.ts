/**
 * 知识库相关类型定义
 */

// 知识库分类枚举
export type KnowledgeBaseCategory =
  | 'syntax_error'
  | 'logic_error'
  | 'environment'
  | 'algorithm'
  | 'concept'
  | 'debugging'
  | 'data_structure'
  | 'best_practice'
  | 'other';

// 难度级别枚举
export type DifficultyLevel = 1 | 2 | 3 | 4 | 5;

// 分类标签映射
export const CATEGORY_LABELS: Record<KnowledgeBaseCategory, string> = {
  syntax_error: '语法错误',
  logic_error: '逻辑错误',
  environment: '环境配置',
  algorithm: '算法问题',
  concept: '概念理解',
  debugging: '调试技巧',
  data_structure: '数据结构',
  best_practice: '最佳实践',
  other: '其他',
};

// 难度级别标签映射
export const DIFFICULTY_LABELS: Record<DifficultyLevel, string> = {
  1: 'L1 - 入门级',
  2: 'L2 - 基础级',
  3: 'L3 - 中级',
  4: 'L4 - 高级',
  5: 'L5 - 专家级',
};

// 知识库条目
export interface KnowledgeBaseEntry {
  entry_id: string;
  category: KnowledgeBaseCategory;
  question: string;
  answer: string;
  keywords: string[];
  difficulty_level: DifficultyLevel;
  language: string | null;
  view_count: number;
  helpful_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 创建知识库条目请求
export interface KnowledgeBaseCreateRequest {
  category: KnowledgeBaseCategory;
  question: string;
  answer: string;
  keywords: string[];
  difficulty_level: DifficultyLevel;
  language?: string | null;
}

// 更新知识库条目请求
export interface KnowledgeBaseUpdateRequest {
  category?: KnowledgeBaseCategory;
  question?: string;
  answer?: string;
  keywords?: string[];
  difficulty_level?: DifficultyLevel;
  language?: string | null;
  is_active?: boolean;
}

// 搜索请求
export interface KnowledgeBaseSearchRequest {
  query: string;
  category?: KnowledgeBaseCategory;
  difficulty_level?: DifficultyLevel;
  language?: string;
  limit?: number;
}

// 搜索结果
export interface KnowledgeBaseSearchResult {
  entry_id: string;
  question: string;
  answer: string;
  category: KnowledgeBaseCategory;
  difficulty_level: DifficultyLevel;
  keywords: string[];
  relevance_score: number;
}

// 搜索响应
export interface KnowledgeBaseSearchResponse {
  query: string;
  total_results: number;
  results: KnowledgeBaseSearchResult[];
}

// 列表响应
export interface KnowledgeBaseListResponse {
  total: number;
  page: number;
  page_size: number;
  entries: KnowledgeBaseEntry[];
}

// 统计信息
export interface KnowledgeBaseStats {
  total_entries: number;
  active_entries: number;
  total_views: number;
  total_helpful: number;
  entries_by_category: Record<string, number>;
  entries_by_difficulty: Record<string, number>;
}

// 分类信息
export interface CategoryInfo {
  value: string;
  label: string;
  description: string;
  count: number;
}

// 分类列表响应
export interface CategoriesResponse {
  categories: CategoryInfo[];
}

