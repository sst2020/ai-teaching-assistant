<script setup lang="ts">
import { ref } from 'vue'
import { analysisApi } from '@/services/api'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const code = ref('')
const language = ref('python')
const result = ref<any>(null)
const loading = ref(false)

const languages = [
  { label: 'Python', value: 'python' },
  { label: 'Java', value: 'java' },
  { label: 'C++', value: 'cpp' },
  { label: 'JavaScript', value: 'javascript' },
]

const handleAnalyze = async () => {
  if (!code.value.trim()) {
    toast.warning('请输入代码')
    return
  }

  loading.value = true
  try {
    result.value = await analysisApi.analyzeCode(code.value, language.value)
    toast.success('分析完成')
  } catch (error: any) {
    toast.error(error.response?.data?.detail || '分析失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="code-analysis">
    <h2>代码分析</h2>

    <el-card>
      <el-form label-position="top">
        <el-form-item label="编程语言">
          <el-select v-model="language" placeholder="选择语言">
            <el-option
              v-for="lang in languages"
              :key="lang.value"
              :label="lang.label"
              :value="lang.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="代码">
          <el-input
            v-model="code"
            type="textarea"
            rows="15"
            placeholder="请输入要分析的代码..."
            class="code-input"
            font-family="monospace"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleAnalyze">
            <el-icon><Monitor /></el-icon>
            分析代码
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
.code-analysis {
  padding: 20px;
}

.code-input :deep(textarea) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.result-section {
  margin-top: 20px;
}

.result-content {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
