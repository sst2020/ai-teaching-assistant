<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { assignmentsApi, submissionsApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { Assignment, Submission } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const assignments = ref<Assignment[]>([])
const submissions = ref<Submission[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const studentId = authStore.user?.student_id || ''
    const [assignmentsRes, submissionsRes] = await Promise.all([
      assignmentsApi.getAll(),
      submissionsApi.getStudentSubmissions(studentId)
    ])
    assignments.value = assignmentsRes
    submissions.value = submissionsRes
  } finally {
    loading.value = false
  }
})

const getSubmissionStatus = (assignmentId: string) => {
  const submission = submissions.value.find(s => s.assignment_id === assignmentId)
  if (!submission) return { text: '未提交', type: 'info' }
  if (submission.status === 'graded') return { text: `已批改: ${submission.grade}分`, type: 'success' }
  if (submission.status === 'grading') return { text: '批改中', type: 'warning' }
  return { text: '已提交', type: 'primary' }
}

const submitAssignment = (assignmentId: string) => {
  router.push(`/submit/${assignmentId}`)
}
</script>

<template>
  <div class="dashboard">
    <el-page-header title="学生Dashboard" />

    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ assignments.length }}</div>
            <div class="stat-label">总作业</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ submissions.length }}</div>
            <div class="stat-label">已提交</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">
              {{ submissions.filter(s => s.status === 'graded').length }}
            </div>
            <div class="stat-label">已批改</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="assignments-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>作业列表</span>
        </div>
      </template>

      <el-table :data="assignments" style="width: 100%">
        <el-table-column prop="title" label="作业标题" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="due_date" label="截止日期" width="180">
          <template #default="{ row }">
            {{ new Date(row.due_date).toLocaleDateString() }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getSubmissionStatus(row.id).type as any">
              {{ getSubmissionStatus(row.id).text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="submitAssignment(row.id)">
              {{ getSubmissionStatus(row.id).text === '未提交' ? '提交' : '查看' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-row {
  margin: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  margin-top: 8px;
  color: #909399;
}

.assignments-card {
  margin-top: 20px;
}

.card-header {
  font-weight: bold;
}
</style>
