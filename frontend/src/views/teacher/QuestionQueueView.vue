<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { qaApi } from '@/services/api'
import type { QAQuestion } from '@/types'

const questions = ref<QAQuestion[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    questions.value = await qaApi.getQuestions()
  } finally {
    loading.value = false
  }
})

const getStatusType = (status: string) => {
  switch (status) {
    case 'answered': return 'success'
    case 'escalated': return 'danger'
    default: return 'warning'
  }
}
</script>

<template>
  <div class="question-queue">
    <h2>问题队列</h2>

    <el-card v-loading="loading">
      <el-table :data="questions" style="width: 100%">
        <el-table-column prop="question" label="问题" show-overflow-tooltip />
        <el-table-column prop="category" label="类别" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status) as any">
              {{ row.status === 'pending' ? '待处理' : row.status === 'answered' ? '已回答' : '已升级' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.question-queue {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
}
</style>
