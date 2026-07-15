import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: () => {
        const authStore = useAuthStore()
        if (!authStore.isAuthenticated) return '/login'
        return authStore.userRole === 'student' ? '/dashboard' : '/teacher'
      }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { hideHeader: true, public: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { hideHeader: true, public: true }
    },
    // Student routes
    {
      path: '/dashboard',
      name: 'student-dashboard',
      component: () => import('@/views/student/DashboardView.vue'),
      meta: { requiresAuth: true, roles: ['student'] }
    },
    {
      path: '/grades',
      name: 'grades',
      component: () => import('@/views/student/GradesView.vue'),
      meta: { requiresAuth: true, roles: ['student'] }
    },
    {
      path: '/submit/:assignmentId',
      name: 'submit-assignment',
      component: () => import('@/views/student/SubmitAssignmentView.vue'),
      meta: { requiresAuth: true, roles: ['student'] }
    },
    // Teacher routes
    {
      path: '/teacher',
      name: 'teacher-dashboard',
      component: () => import('@/views/teacher/DashboardView.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] }
    },
    {
      path: '/manage-assignments',
      name: 'manage-assignments',
      component: () => import('@/views/teacher/ManageAssignmentsView.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] }
    },
    {
      path: '/grading',
      name: 'grading',
      component: () => import('@/views/teacher/GradingView.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] }
    },
    {
      path: '/question-queue',
      name: 'question-queue',
      component: () => import('@/views/teacher/QuestionQueueView.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] }
    },
    // Common features
    {
      path: '/smart-qa',
      name: 'smart-qa',
      component: () => import('@/views/features/SmartQAView.vue'),
      meta: { requiresAuth: true, roles: ['student', 'teacher', 'admin'] }
    },
    {
      path: '/knowledge-base',
      name: 'knowledge-base',
      component: () => import('@/views/features/KnowledgeBaseView.vue'),
      meta: { requiresAuth: true, roles: ['student', 'teacher', 'admin'] }
    },
    {
      path: '/student-records',
      name: 'student-records',
      component: () => import('@/views/features/StudentRecordsView.vue'),
      meta: { requiresAuth: true, roles: ['student', 'teacher', 'admin'] }
    },
    {
      path: '/account',
      name: 'account',
      component: () => import('@/views/common/AccountView.vue'),
      meta: { requiresAuth: true }
    },
    // Advanced features (teacher/admin only)
    {
      path: '/code-analysis',
      name: 'code-analysis',
      component: () => import('@/views/features/CodeAnalysisView.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] }
    },
    {
      path: '/qa',
      name: 'qa-interface',
      component: () => import('@/views/features/QAInterfaceView.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] }
    },
    {
      path: '/plagiarism',
      name: 'plagiarism-check',
      component: () => import('@/views/features/PlagiarismView.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] }
    },
    {
      path: '/report-analysis',
      name: 'report-analysis',
      component: () => import('@/views/features/ReportAnalysisView.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] }
    },
    // Dev tools
    {
      path: '/dev/api-tester',
      name: 'api-tester',
      component: () => import('@/views/dev/ApiTesterView.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] }
    },
    {
      path: '/dev/performance-monitor',
      name: 'performance-monitor',
      component: () => import('@/views/dev/PerformanceMonitorView.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] }
    },
    // Error pages
    {
      path: '/forbidden',
      name: 'forbidden',
      component: () => import('@/views/error/ForbiddenView.vue'),
      meta: { hideHeader: true }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Handle public routes
  if (to.meta.public) {
    if (authStore.isAuthenticated) {
      return next(authStore.userRole === 'student' ? '/dashboard' : '/teacher')
    }
    return next()
  }

  // Check authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next('/login')
  }

  // Check role permissions
  if (to.meta.roles && !to.meta.roles.includes(authStore.userRole || '')) {
    return next('/forbidden')
  }

  next()
})

export default router
