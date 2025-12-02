// Project Report Intelligent Analysis - frontend TypeScript types
// NOTE: 这里是后端 `schemas.report_analysis` 的精简对齐版本，只保留前端当前需要展示的字段。

export type ReportFileType = 'pdf' | 'docx' | 'markdown';

export type ReportLanguage = 'zh' | 'en' | 'mixed';

export type ReferenceFormat = 'apa' | 'mla' | 'gbt7714' | 'unknown';

export type SectionType =
  | 'abstract'
  | 'introduction'
  | 'related_work'
  | 'method'
  | 'results'
  | 'discussion'
  | 'conclusion'
  | 'references'
  | 'appendix'
  | 'other';

export interface ReportSection {
  id: string;
  title: string;
  level: number;
  section_type: SectionType;
  order_index: number;
  text: string;
  children: ReportSection[];
}

export interface ReferenceEntry {
  raw_text: string;
  detected_format: ReferenceFormat;
  is_valid: boolean;
  problems: string[];
}

export interface ReportParseResult {
  file_id?: string | null;
  file_name: string;
  file_type: ReportFileType;
  language: ReportLanguage;
  sections: ReportSection[];
  references: ReferenceEntry[];
  raw_text: string;
}

export interface ChapterLengthStats {
  section_id: string;
  title: string;
  word_count: number;
  proportion: number;
  evaluation: string;
}

export interface FigureTableStats {
  figure_count: number;
  table_count: number;
  evaluation: string;
}

export interface ReferenceStats {
  total_count: number;
  valid_count: number;
  expected_min_count: number;
  format_compliance_ratio: number;
  evaluation: string;
}

export interface ReportQualityMetrics {
  total_word_count: number;
  word_count_evaluation: string;
  required_sections_present: Record<SectionType, boolean>;
  chapter_length_stats: ChapterLengthStats[];
  figure_table_stats: FigureTableStats;
  reference_stats: ReferenceStats;
  overall_completeness_score: number;
}

export type LogicIssueType =
  | 'missing_evidence'
  | 'logical_gap'
  | 'weak_conclusion'
  | 'redundant_content';

export interface LogicIssue {
  issue_type: LogicIssueType;
  section_id?: string | null;
  paragraph_index?: number | null;
  description: string;
  suggested_fix?: string | null;
}

export interface LogicAnalysisResult {
  section_order_score: number;
  coherence_score: number;
  argumentation_score: number;
  issues: LogicIssue[];
  summary: string;
}

export interface InnovationPoint {
  section_id?: string | null;
  highlight_text: string;
  reason: string;
}

export interface InnovationAnalysisResult {
  novelty_score: number;
  difference_summary: string;
  innovation_points: InnovationPoint[];
}

export interface LanguageQualityMetrics {
  average_sentence_length: number;
  long_sentence_ratio: number;
  vocabulary_richness: number;
  grammar_issue_count: number;
  academic_tone_score: number;
  readability_score: number;
}

export type FormattingIssueType =
  | 'title_inconsistent'
  | 'figure_table_numbering'
  | 'reference_format'
  | 'pagination'
  | 'font_style';

export interface FormattingIssue {
  issue_type: FormattingIssueType;
  location?: string | null;
  description: string;
  suggested_fix?: string | null;
}

export interface FormattingCheckResult {
  reference_style: ReferenceFormat;
  title_consistency_score: number;
  figure_table_consistency_score: number;
  issues: FormattingIssue[];
}

export interface ImprovementSuggestion {
  category: string;
  section_id?: string | null;
  summary: string;
  details: string;
}

export interface ReportAnalysisRequest {
  file_name: string;
  file_type: ReportFileType;
  content: string;
  language?: ReportLanguage;
  reference_style_preference?: ReferenceFormat;
}

export interface ReportAnalysisResponse {
  report_id: string;
  file_name: string;
  analyzed_at: string;
  parsed: ReportParseResult;
  quality: ReportQualityMetrics;
  logic: LogicAnalysisResult;
  innovation: InnovationAnalysisResult;
  language_quality: LanguageQualityMetrics;
  formatting: FormattingCheckResult;
  suggestions: ImprovementSuggestion[];
  overall_score: number;
  summary: string;
}

