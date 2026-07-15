// 扩展 i18next 类型以支持命名空间
import 'i18next';

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: {
      common: Record<string, unknown>;
      auth: Record<string, unknown>;
      navigation: Record<string, unknown>;
      dashboard: Record<string, unknown>;
      qa: Record<string, unknown>;
      analysis: Record<string, unknown>;
      student: Record<string, unknown>;
      teacher: Record<string, unknown>;
      plagiarism: Record<string, unknown>;
      report: Record<string, unknown>;
      grading: Record<string, unknown>;
      assignments: Record<string, unknown>;
    };
    allowObjectInHTMLChildren: true;
  }
}

