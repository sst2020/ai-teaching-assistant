<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { assignmentsApi } from '@/services/api'
import { useToastStore } from '@/stores/toast'
import type { Assignment } from '@/types'

const toast = useToastStore()
const assignments = ref<Assignment[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
let abortController: AbortController | null = null

const form = ref({
  title: '',
  description: '',
  due_date: '',
  assignment_type: 'code' as 'code' | 'essay' | 'quiz' | 'project',
  course_id: ''
})

onMounted(() => {
  loadAssignments()
})

onUnmounted(() => {
  abortController?.abort()
})

const loadAssignments = async () => {
  abortController?.abort()
  abortController = new AbortController()
  const currentController = abortController

  loading.value = true
  try {
    const res = await assignmentsApi.getAll(currentController.signal)
    assignments.value = Array.isArray(res) ? res : (res.items ?? [])
  } catch (error: any) {
    if (error.name !== 'AbortError' && error.code !== 'ERR_CANCELED') {
      toast.error('加载作业列表失败')
    }
  } finally {
    if (abortController === currentController) {
      loading.value = false
      abortController = null
    }
  }
}

const handleCreate = async () => {
  if (!form.value.title || !form.value.course_id) {
    toast.error('请填写标题和课程ID')
    return
  }
  try {
    const payload = {
      ...form.value,
      assignment_id: `hw-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`
    }
    await assignmentsApi.create(payload)
    toast.success('作业创建成功')
    dialogVisible.value = false
    await loadAssignments()
    form.value = { title: '', description: '', due_date: '', assignment_type: 'code', course_id: '' }
  } catch (error: any) {
    toast.error(error.response?.data?.detail || '创建失败')
  }
}

const handleDelete = async (id: string) => {
  try {
    await assignmentsApi.delete(id)
    toast.success('作业删除成功')
    await loadAssignments()
  } catch (error: any) {
    toast.error(error.response?.data?.detail || '删除失败')
  }
}
</script>

<template>
  <div class="manage-assignments">
    <div class="header">
      <h2>作业管理</h2>
      <el-button type="primary" @click="dialogVisible = true">
        <el-icon><Plus /></el-icon>
        创建作业
      </el-button>
    </div>

    <el-card v-loading="loading">
      <el-table :data="assignments" style="width: 100%">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="assignment_type" label="类型" width="100" />
        <el-table-column prop="course_id" label="课程" width="120" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="due_date" label="截止日期">
          <template #default="{ row }">
            {{ new Date(row.due_date).toLocaleDateString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleDelete(row.assignment_id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="创建作业" width="500px">
      <el-form :model="form" label-position="top">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="请输入作业标题" />
        </el-form-item>
        <el-form-item label="课程ID" required>
          <el-input v-model="form.course_id" placeholder="例如 CS101" />
        </el-form-item>
        <el-form-item label="作业类型">
          <el-select v-model="form.assignment_type" placeholder="选择类型">
            <el-option label="代码" value="code" />
            <el-option label="论文" value="essay" />
            <el-option label="测验" value="quiz" />
            <el-option label="项目" value="project" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" rows="3" placeholder="请输入作业描述" />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="form.due_date" type="datetime" placeholder="选择截止日期" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.manage-assignments {
  padding: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.header h2 {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1d1d1f 0%, #434344 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Glass Card Effect for el-card */
:deep(.el-card) {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04),
    inset 0 0 0 1px rgba(255, 255, 255, 0.6);
  overflow: hidden;
}

:deep(.el-card__body) {
  padding: 24px;
}

/* Primary Button - Liquid style */
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  border: none;
  border-radius: 20px;
  padding: 12px 24px;
  font-weight: 600;
  box-shadow: 
    0 4px 16px rgba(0, 122, 255, 0.35),
    0 1px 3px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.25);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 
    0 6px 24px rgba(0, 122, 255, 0.45),
    0 2px 6px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

:deep(.el-button--danger) {
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.25s ease;
}

/* Table styling */
:deep(.el-table) {
  background: transparent;
  --el-table-border-color: rgba(0, 0, 0, 0.06);
}

:deep(.el-table__header th) {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(12px);
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 16px;
}

:deep(.el-table__row) {
  transition: all 0.2s ease;
}

:deep(.el-table__row:hover) {
  background: rgba(0, 122, 255, 0.05);
}

:deep(.el-table__cell) {
  padding: 16px;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.8);
}

/* Loading overlay */
:deep(.el-loading-mask) {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
}

/* Dialog styling */
:deep(.el-dialog) {
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(32px) saturate(180%);
  -webkit-backdrop-filter: blur(32px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 
    0 24px 64px rgba(0, 0, 0, 0.15),
    0 8px 24px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

:deep(.el-dialog__header) {
  padding: 24px 28px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.el-dialog__title) {
  font-weight: 700;
  font-size: 20px;
  color: #1d1d1f;
}

:deep(.el-dialog__body) {
  padding: 24px 28px;
}

:deep(.el-dialog__footer) {
  padding: 20px 28px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

/* Form inputs */
:deep(.el-input__wrapper) {
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02);
  transition: all 0.25s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(0, 122, 255, 0.4);
}

:deep(.el-input__wrapper.is-focus) {
  background: rgba(255, 255, 255, 0.9);
  border-color: #007AFF;
  box-shadow: 
    0 0 0 4px rgba(0, 122, 255, 0.1),
    inset 0 1px 2px rgba(0, 0, 0, 0.02);
}

:deep(.el-textarea__inner) {
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.08);
  transition: all 0.25s ease;
}

:deep(.el-textarea__inner:focus) {
  background: rgba(255, 255, 255, 0.9);
  border-color: #007AFF;
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
}

/* Date picker */
:deep(.el-date-editor) {
  --el-input-border-radius: 14px;
}
</style>
