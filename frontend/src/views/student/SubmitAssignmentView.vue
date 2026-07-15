<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { submissionsApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const toast = useToastStore()

const assignmentId = route.params.assignmentId as string
const fileList = ref<File[]>([])
const content = ref('')
const loading = ref(false)

const handleFileChange = (files: File[]) => {
  fileList.value = files
}

const handleSubmit = async () => {
  const studentId = authStore.user?.student_id || ''
  if (!studentId) {
    toast.error('无法获取学号，请重新登录')
    return
  }

  loading.value = true
  try {
    await submissionsApi.create({
      student_id: studentId,
      assignment_id: assignmentId,
      content: content.value || undefined,
    })
    toast.success('作业提交成功')
    router.push('/dashboard')
  } catch (error: any) {
    toast.error(error.response?.data?.detail || '提交失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="submit-view">
    <el-page-header title="提交作业" @back="router.back()" />

    <el-card class="submit-card">
      <h3>作业提交</h3>
      <p class="assignment-id">作业ID: {{ assignmentId }}</p>

      <el-upload
        drag
        multiple
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".py,.java,.cpp,.c,.js,.ts,.pdf,.docx,.txt"
      >
        <el-icon class="el-icon--upload"><Upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持代码文件 (.py, .java, .cpp, .js, .ts) 和文档 (.pdf, .docx, .txt)
          </div>
        </template>
      </el-upload>

      <div class="actions">
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          提交作业
        </el-button>
        <el-button @click="router.back()">取消</el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.submit-view {
  padding: 20px;
}

.submit-card {
  margin-top: 20px;
  max-width: 600px;
}

.assignment-id {
  color: #909399;
  margin-bottom: 20px;
}

.actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>
