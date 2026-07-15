<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { RegisterData } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const form = ref<RegisterData>({
  name: '',
  email: '',
  password: '',
  role: 'student',
  student_id: ''
})

const confirmPassword = ref('')
const loading = ref(false)

const isStudent = () => form.value.role === 'student'

// 验证10位数字
const validateIdNumber = (value: string): boolean => {
  return /^\d{10}$/.test(value)
}

const handleRegister = async () => {
  if (form.value.password !== confirmPassword.value) {
    authStore.error = '两次输入的密码不一致'
    return
  }

  // 验证学号/职工号
  if (!validateIdNumber(form.value.student_id || '')) {
    authStore.error = isStudent() ? '学号必须为10位数字' : '职工号必须为10位数字'
    return
  }

  loading.value = true
  const success = await authStore.register(form.value)
  loading.value = false

  if (success) {
    router.push('/login')
  }
}
</script>

<template>
  <div class="register-page">
    <el-card class="register-card">
      <h2 class="register-title">注册账号</h2>

      <el-alert
        v-if="authStore.error"
        :title="authStore.error"
        type="error"
        closable
        @close="authStore.clearError"
        class="register-error"
      />

      <el-form :model="form" label-position="top" @submit.prevent="handleRegister">
        <el-form-item label="用户类型">
          <el-radio-group v-model="form.role">
            <el-radio label="student">学生</el-radio>
            <el-radio label="teacher">教师</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="请输入姓名" :prefix-icon="'User'" />
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input v-model="form.email" type="email" placeholder="请输入邮箱" :prefix-icon="'Message'" />
        </el-form-item>

        <el-form-item :label="isStudent() ? '学号' : '职工号'">
          <el-input
            v-model="form.student_id"
            :placeholder="isStudent() ? '请输入10位学号' : '请输入10位职工号'"
            :prefix-icon="'Postcard'"
            maxlength="10"
            @input="form.student_id = form.student_id?.replace(/\D/g, '').slice(0, 10)"
          />
        </el-form-item>

        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" :prefix-icon="'Lock'" show-password />
        </el-form-item>

        <el-form-item label="确认密码">
          <el-input v-model="confirmPassword" type="password" placeholder="请再次输入密码" :prefix-icon="'Lock'" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading || authStore.isLoading" class="register-button">
            注册
          </el-button>
        </el-form-item>

        <div class="register-links">
          <router-link to="/login">已有账号？立即登录</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 100%;
  max-width: 400px;
  margin: 20px;
}

.register-title {
  text-align: center;
  margin-bottom: 24px;
  color: #303133;
}

.register-error {
  margin-bottom: 16px;
}

.register-button {
  width: 100%;
}

.register-links {
  text-align: center;
  margin-top: 16px;
}

.register-links a {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
}
</style>
