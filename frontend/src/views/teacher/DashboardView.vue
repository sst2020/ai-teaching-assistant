<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { assignmentsApi, submissionsApi } from '@/services/api'
import type { Assignment } from '@/types'

const router = useRouter()
const assignments = ref<Assignment[]>([])
const pendingCount = ref(0)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await assignmentsApi.getAll()
    assignments.value = Array.isArray(res) ? res : (res.items ?? [])
    // Count submissions for all assignments
    let total = 0
    for (const a of assignments.value) {
      try {
        const subs = await submissionsApi.getByAssignment(a.id)
        const items = Array.isArray(subs) ? subs : (subs.items ?? [])
        total += items.length
      } catch { /* ignore per-assignment errors */ }
    }
    pendingCount.value = total
  } finally {
    loading.value = false
  }
})

const goTo = (path: string) => router.push(path)
</script>

<template>
  <div class="teacher-dashboard">
    <h2>教师 Dashboard</h2>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card @click="goTo('/manage-assignments')" class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ assignments.length }}</div>
            <div class="stat-label">作业总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card @click="goTo('/grading')" class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ pendingCount }}</div>
            <div class="stat-label">待批改</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card @click="goTo('/question-queue')" class="stat-card">
          <div class="stat-item">
            <el-icon class="stat-icon"><ChatDotRound /></el-icon>
            <div class="stat-label">问题队列</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="quick-actions">
      <template #header>
        <div class="card-header">
          <span>快捷操作</span>
        </div>
      </template>
      <div class="actions">
        <el-button type="primary" @click="goTo('/manage-assignments')">
          <el-icon><Plus /></el-icon>
          创建作业
        </el-button>
        <el-button @click="goTo('/grading')">
          <el-icon><EditPen /></el-icon>
          批改作业
        </el-button>
        <el-button @click="goTo('/code-analysis')">
          <el-icon><Monitor /></el-icon>
          代码分析
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.teacher-dashboard {
  padding: 20px;
}

.stats-row {
  margin: 20px 0;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
}

.stat-icon {
  font-size: 36px;
  color: #409eff;
}

.stat-label {
  margin-top: 8px;
  color: #606266;
}

.quick-actions {
  margin-top: 20px;
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.actions .el-icon {
  margin-right: 4px;
}
</style>
