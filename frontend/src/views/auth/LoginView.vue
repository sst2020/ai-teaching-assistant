<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { LoginCredentials } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const credentials = ref<LoginCredentials>({
  username: '',
  password: ''
})

// 验证10位数字
const validateUsername = (value: string): boolean => {
  return /^\d{10}$/.test(value)
}

const loading = ref(false)

onMounted(() => {
  authStore.initAuth()
})

const handleLogin = async () => {
  // 验证学号/职工号
  if (!validateUsername(credentials.value.username)) {
    authStore.error = '学号/职工号必须为10位数字'
    return
  }

  loading.value = true
  const success = await authStore.login(credentials.value)
  loading.value = false

  if (success) {
    const redirect = route.query.redirect as string
    if (redirect) {
      router.push(redirect)
    } else {
      router.push(authStore.userRole === 'student' ? '/dashboard' : '/teacher')
    }
  }
}
</script>

<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2 class="login-title">AI Teaching Assistant</h2>
      <p class="login-subtitle">智能教学助手平台</p>

      <el-alert
        v-if="authStore.error"
        :title="authStore.error"
        type="error"
        closable
        @close="authStore.clearError"
        class="login-error"
      />

      <el-form
        :model="credentials"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="学号/职工号">
          <el-input
            v-model="credentials.username"
            placeholder="请输入10位学号或职工号"
            :prefix-icon="'User'"
            maxlength="10"
            @input="credentials.username = credentials.username.replace(/\D/g, '').slice(0, 10)"
          />
        </el-form-item>

        <el-form-item label="密码">
          <el-input
            v-model="credentials.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="'Lock'"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading || authStore.isLoading"
            class="login-button"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="login-links">
          <router-link to="/register">注册账号</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
  margin: 20px;
}

.login-title {
  text-align: center;
  margin-bottom: 8px;
  color: #303133;
}

.login-subtitle {
  text-align: center;
  margin-bottom: 24px;
  color: #909399;
  font-size: 14px;
}

.login-error {
  margin-bottom: 16px;
}

.login-button {
  width: 100%;
}

.login-links {
  text-align: center;
  margin-top: 16px;
}

.login-links a {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
}

.login-links a:hover {
  text-decoration: underline;
}
</style>
