<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const stats = ref({
  memory: 0,
  requests: 0,
  avgResponseTime: 0
})

const logs = ref<string[]>([])
let interval: number | null = null

onMounted(() => {
  interval = window.setInterval(() => {
    if (performance.memory) {
      stats.value.memory = Math.round((performance as any).memory.usedJSHeapSize / 1024 / 1024)
    }
  }, 1000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})

const clearLogs = () => {
  logs.value = []
}
</script>

<template>
  <div class="performance-monitor">
    <h2>性能监控</h2>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.memory }} MB</div>
            <div class="stat-label">内存使用</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.requests }}</div>
            <div class="stat-label">请求数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.avgResponseTime }}ms</div>
            <div class="stat-label">平均响应时间</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="logs-card">
      <template #header>
        <div class="card-header">
          <span>日志</span>
          <el-button size="small" @click="clearLogs">清空</el-button>
        </div>
      </template>
      <div class="logs">
        <div v-for="(log, index) in logs" :key="index" class="log-item">
          {{ log }}
        </div>
        <el-empty v-if="logs.length === 0" description="暂无日志" />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.performance-monitor {
  padding: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
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

.logs-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logs {
  max-height: 400px;
  overflow-y: auto;
}

.log-item {
  padding: 8px;
  border-bottom: 1px solid #e4e7ed;
  font-family: monospace;
  font-size: 12px;
}
</style>
