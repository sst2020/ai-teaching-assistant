<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const method = ref('GET')
const url = ref('/api/v1/assignments/')
const body = ref('')
const response = ref<any>(null)
const loading = ref(false)
const error = ref('')

const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

const sendRequest = async () => {
  loading.value = true
  error.value = ''
  response.value = null

  try {
    const config: any = {
      method: method.value,
      url: url.value,
      headers: {}
    }

    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    if (['POST', 'PUT', 'PATCH'].includes(method.value) && body.value) {
      config.data = JSON.parse(body.value)
      config.headers['Content-Type'] = 'application/json'
    }

    const res = await axios(config)
    response.value = res.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="api-tester">
    <h2>API 测试工具</h2>

    <el-card>
      <el-form label-position="top">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="方法">
              <el-select v-model="method" style="width: 100%">
                <el-option v-for="m in methods" :key="m" :label="m" :value="m" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="18">
            <el-form-item label="URL">
              <el-input v-model="url" placeholder="/api/v1/..." />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="请求体 (JSON)" v-if="['POST', 'PUT', 'PATCH'].includes(method)">
          <el-input v-model="body" type="textarea" rows="6" placeholder='{"key": "value"}' />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="sendRequest">
            发送请求
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="error" class="error-section">
        <el-divider />
        <h4>错误</h4>
        <el-alert :title="error" type="error" />
      </div>

      <div v-if="response" class="response-section">
        <el-divider />
        <h4>响应</h4>
        <pre class="response-content">{{ JSON.stringify(response, null, 2) }}</pre>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.api-tester {
  padding: 20px;
}

.error-section,
.response-section {
  margin-top: 20px;
}

.response-content {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
