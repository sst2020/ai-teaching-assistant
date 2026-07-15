<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const userRole = computed(() => authStore.userRole)
const userName = computed(() => authStore.userName)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/code-analysis')) return 'code-analysis'
  if (path.startsWith('/qa')) return 'qa'
  if (path.startsWith('/plagiarism')) return 'plagiarism'
  if (path.startsWith('/report-analysis')) return 'report-analysis'
  if (path.startsWith('/teacher')) return 'teacher'
  if (path.startsWith('/grading')) return 'grading'
  if (path.startsWith('/manage-assignments')) return 'manage-assignments'
  if (path.startsWith('/question-queue')) return 'question-queue'
  if (path.startsWith('/student-records')) return 'student-records'
  return 'dashboard'
})

const isStudent = computed(() => userRole.value === 'student')
const isTeacher = computed(() => userRole.value === 'teacher' || userRole.value === 'admin')

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const handleMenuSelect = (index: string) => {
  const routeMap: Record<string, string> = {
    'dashboard': '/dashboard',
    'grades': '/grades',
    'teacher': '/teacher',
    'manage-assignments': '/manage-assignments',
    'grading': '/grading',
    'question-queue': '/question-queue',
    'code-analysis': '/code-analysis',
    'qa': '/qa',
    'plagiarism': '/plagiarism',
    'report-analysis': '/report-analysis',
    'smart-qa': '/smart-qa',
    'knowledge-base': '/knowledge-base',
    'student-records': '/student-records',
  }
  const path = routeMap[index]
  if (path) {
    router.push(path)
  }
}
</script>

<template>
  <el-header class="app-header">
    <div class="header-left">
      <div class="logo" @click="router.push('/')">
        <el-icon><School /></el-icon>
        <span>AI Teaching Assistant</span>
      </div>

      <el-menu
        :active-index="activeMenu"
        class="header-menu"
        mode="horizontal"
        :ellipsis="false"
        @select="handleMenuSelect"
      >
        <!-- Student Navigation -->
        <template v-if="isStudent">
          <el-menu-item index="dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>Dashboard</span>
          </el-menu-item>
          <el-menu-item index="grades">
            <el-icon><Trophy /></el-icon>
            <span>成绩</span>
          </el-menu-item>
        </template>

        <!-- Teacher Navigation -->
        <template v-if="isTeacher">
          <el-menu-item index="teacher">
            <el-icon><HomeFilled /></el-icon>
            <span>Dashboard</span>
          </el-menu-item>
          <el-menu-item index="manage-assignments">
            <el-icon><Document /></el-icon>
            <span>作业管理</span>
          </el-menu-item>
          <el-menu-item index="grading">
            <el-icon><EditPen /></el-icon>
            <span>批改作业</span>
          </el-menu-item>
          <el-menu-item index="question-queue">
            <el-icon><ChatDotRound /></el-icon>
            <span>问题队列</span>
          </el-menu-item>

          <el-sub-menu index="features">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>高级功能</span>
            </template>
            <el-menu-item index="code-analysis">
              <el-icon><Monitor /></el-icon>
              <span>代码分析</span>
            </el-menu-item>
            <el-menu-item index="qa">
              <el-icon><ChatLineRound /></el-icon>
              <span>智能问答</span>
            </el-menu-item>
            <el-menu-item index="plagiarism">
              <el-icon><Search /></el-icon>
              <span>抄袭检测</span>
            </el-menu-item>
            <el-menu-item index="report-analysis">
              <el-icon><DocumentChecked /></el-icon>
              <span>报告分析</span>
            </el-menu-item>
          </el-sub-menu>
        </template>

        <!-- Common Features -->
        <el-menu-item index="smart-qa">
          <el-icon><ChatLineRound /></el-icon>
          <span>智能答疑</span>
        </el-menu-item>
        <el-menu-item index="knowledge-base">
          <el-icon><Reading /></el-icon>
          <span>知识库</span>
        </el-menu-item>
        <el-menu-item index="student-records">
          <el-icon><User /></el-icon>
          <span>学生记录</span>
        </el-menu-item>
      </el-menu>
    </div>

    <div class="header-right">
      <el-dropdown>
        <span class="user-info">
          <el-icon><UserFilled /></el-icon>
          <span>{{ userName }}</span>
          <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="router.push('/account')">
              <el-icon><Setting /></el-icon>
              账号设置
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  z-index: 100;
  
  /* Liquid Glass Effect */
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 
    0 4px 24px rgba(0, 0, 0, 0.08),
    0 1px 2px rgba(0, 0, 0, 0.04),
    inset 0 0 0 1px rgba(255, 255, 255, 0.6);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 48px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.02);
}

.logo .el-icon {
  font-size: 28px;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Glass Menu Styling */
.header-menu {
  border-bottom: none;
  background: transparent;
}

.header-menu :deep(.el-menu-item) {
  border-radius: 14px;
  padding: 10px 20px;
  margin: 0 4px;
  font-weight: 500;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.7);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.header-menu :deep(.el-menu-item::before) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.1) 0%, rgba(88, 86, 214, 0.1) 100%);
  border-radius: 14px;
  opacity: 0;
  transition: opacity 0.25s ease;
}

.header-menu :deep(.el-menu-item:hover::before) {
  opacity: 1;
}

.header-menu :deep(.el-menu-item:hover) {
  color: #007AFF;
  transform: translateY(-1px);
}

.header-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  color: white;
  font-weight: 600;
  box-shadow: 
    0 4px 16px rgba(0, 122, 255, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

/* Sub-menu styling */
.header-menu :deep(.el-sub-menu__title) {
  border-radius: 14px;
  padding: 10px 20px;
  margin: 0 4px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.7);
  transition: all 0.25s ease;
}

.header-menu :deep(.el-sub-menu__title:hover) {
  color: #007AFF;
  background: rgba(0, 122, 255, 0.08);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: rgba(0, 0, 0, 0.8);
  padding: 10px 16px;
  border-radius: 20px;
  font-weight: 500;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.dropdown-icon {
  margin-left: 4px;
  font-size: 12px;
  opacity: 0.6;
}

/* Dropdown styling */
:deep(.el-dropdown-menu) {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.12),
    0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 8px;
}

:deep(.el-dropdown-menu__item) {
  border-radius: 12px;
  padding: 10px 16px;
  font-weight: 500;
  transition: all 0.2s ease;
}

:deep(.el-dropdown-menu__item:hover) {
  background: rgba(0, 122, 255, 0.1);
  color: #007AFF;
}

/* Sub-menu popover */
:deep(.el-menu--popup) {
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.12),
    0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 8px;
}

:deep(.el-menu--popup .el-menu-item) {
  border-radius: 14px;
  padding: 10px 20px;
  margin: 4px 0;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.7);
  transition: all 0.2s ease;
}

:deep(.el-menu--popup .el-menu-item:hover) {
  background: rgba(0, 122, 255, 0.1);
  color: #007AFF;
}
</style>
