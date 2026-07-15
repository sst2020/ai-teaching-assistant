<script setup lang="ts">
import { ref } from 'vue'
import { analysisApi } from '@/services/api'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const file = ref<File | null>(null)
const result = ref<any>(null)
const loading = ref(false)

const handleFileChange = (uploadFile: any) => {
  file.value = uploadFile.raw
}

const handleAnalyze = async () => {
  if (!file.value) {
    toast.warning('请选择文件')
    return
  }

  loading.value = true
  try {
    result.value = await analysisApi.analyzeReport(file.value)
    toast.success('分析报告完成')
  } catch (error: any) {
    toast.error(error.response?.data?.detail || '分析失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="report-analysis">
    <h2>报告分析</h2>

    <el-card>
      <el-form label-position="top">
        <el-form-item label="上传报告">
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            accept=".pdf,.docx,.txt"
            :limit="1"
          >
            <el-icon class="el-icon--upload"><Upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleAnalyze">
            <el-icon><DocumentChecked /></el-icon>
            分析报告
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="result" class="result-section">
        <el-divider />
        <h4>分析结果</h4>
        <pre class="result-content">{{ JSON.stringify(result, null, 2) }}</pre>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.report-analysis {
  padding: 20px;
}

.result-section {
  margin-top: 20px;
}

.result-content {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
