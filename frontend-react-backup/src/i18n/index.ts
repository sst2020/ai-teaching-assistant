import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// 导入翻译文件
import zhCommon from './locales/zh/common.json';
import zhAuth from './locales/zh/auth.json';
import zhNavigation from './locales/zh/navigation.json';
import zhDashboard from './locales/zh/dashboard.json';
import zhQa from './locales/zh/qa.json';
import zhAnalysis from './locales/zh/analysis.json';
import zhStudent from './locales/zh/student.json';
import zhTeacher from './locales/zh/teacher.json';
import zhPlagiarism from './locales/zh/plagiarism.json';
import zhReport from './locales/zh/report.json';
import zhGrading from './locales/zh/grading.json';
import zhAssignments from './locales/zh/assignments.json';

import enCommon from './locales/en/common.json';
import enAuth from './locales/en/auth.json';
import enNavigation from './locales/en/navigation.json';
import enDashboard from './locales/en/dashboard.json';
import enQa from './locales/en/qa.json';
import enAnalysis from './locales/en/analysis.json';
import enStudent from './locales/en/student.json';
import enTeacher from './locales/en/teacher.json';
import enPlagiarism from './locales/en/plagiarism.json';
import enReport from './locales/en/report.json';
import enGrading from './locales/en/grading.json';
import enAssignments from './locales/en/assignments.json';

// 定义资源
const resources = {
  zh: {
    common: zhCommon,
    auth: zhAuth,
    navigation: zhNavigation,
    dashboard: zhDashboard,
    qa: zhQa,
    analysis: zhAnalysis,
    student: zhStudent,
    teacher: zhTeacher,
    plagiarism: zhPlagiarism,
    report: zhReport,
    grading: zhGrading,
    assignments: zhAssignments,
  },
  en: {
    common: enCommon,
    auth: enAuth,
    navigation: enNavigation,
    dashboard: enDashboard,
    qa: enQa,
    analysis: enAnalysis,
    student: enStudent,
    teacher: enTeacher,
    plagiarism: enPlagiarism,
    report: enReport,
    grading: enGrading,
    assignments: enAssignments,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'zh', // 默认语言为中文
    defaultNS: 'common',
    ns: ['common', 'auth', 'navigation', 'dashboard', 'qa', 'analysis', 'student', 'teacher', 'plagiarism', 'report', 'grading', 'assignments'],
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false, // React 已经处理了 XSS
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
    react: {
      useSuspense: false, // 禁用 Suspense 以避免加载问题
    },
  });

export default i18n;

