<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { submissionsApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { Submission } from '@/types'

const authStore = useAuthStore()
const submissions = ref<Submission[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const studentId = authStore.user?.student_id || ''
    submissions.value = await submissionsApi.getStudentSubmissions(studentId)
  } finally {
    loading.value = false
  }
})

const getStatusType = (status: string) => {
  switch (status) {
    case 'graded': return 'success'
    case 'grading': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'graded': return '已批改'
    case 'grading': return '批改中'
    default: return '已提交'
  }
}
</script>

<template>
  <div class="grades-view">
    <h2>我的成绩</h2>

    <el-card v-loading="loading">
      <el-table :data="submissions" style="width: 100%">
        <el-table-column prop="assignment_id" label="作业ID" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status) as any">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="成绩" width="100">
          <template #default="{ row }">
            <span v-if="row.grade !== undefined" class="grade">
              {{ row.grade }}
            </span>
            <span v-else class="no-grade">--</span>
          </template>
        </el-table-column>
        <el-table-column prop="submitted_at" label="提交时间">
          <template #default="{ row }">
            {{ new Date(row.submitted_at).toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.grades-view {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
}

.grade {
  font-weight: bold;
  color: #67c23a;
}

.no-grade {
  color: #909399;
}
</style>
