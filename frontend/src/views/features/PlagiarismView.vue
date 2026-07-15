<script setup lang="ts">
import { ref } from 'vue'
import { analysisApi } from '@/services/api'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const submissionId = ref('')
const result = ref<any>(null)
const loading = ref(false)

const handleCheck = async () => {
  if (!submissionId.value.trim()) {
    toast.warning('请输入提交ID')
    return
  }

  loading.value = true
  try {
    result.value = await analysisApi.checkPlagiarism(submissionId.value)
    toast.success('检测完成')
  } catch (error: any) {
    toast.error(error.response?.data?.detail || '检测失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="plagiarism-view">
    <h2>抄袭检测</h2>

    <el-card>
      <el-form label-position="top">
        <el-form-item label="提交ID">
          <el-input v-model="submissionId" placeholder="请输入提交ID" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleCheck">
            <el-icon><Search /></el-icon>
            检测抄袭
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="result" class="result-section">
        <el-divider />
        <h4>检测结果</h4>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="相似度分数">
            {{ result.similarity_score }}
          </el-descriptions-item>
          <el-descriptions-item label="匹配数量">
            {{ result.matches?.length || 0 }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.plagiarism-view {
  padding: 20px;
}

.result-section {
  margin-top: 20px;
}
</style>
