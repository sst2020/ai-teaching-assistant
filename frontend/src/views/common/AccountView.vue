<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const authStore = useAuthStore()
const themeStore = useThemeStore()

const user = computed(() => authStore.user)
</script>

<template>
  <div class="account-view">
    <h2>账号设置</h2>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>个人信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="姓名">{{ user?.name }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ user?.email }}</el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag>{{ user?.role === 'student' ? '学生' : user?.role === 'teacher' ? '教师' : '管理员' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="user?.student_id" label="学号">
              {{ user.student_id }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>外观设置</span>
          </template>
          <div class="theme-setting">
            <span>主题</span>
            <el-radio-group v-model="themeStore.theme" @change="themeStore.setTheme">
              <el-radio-button label="light">浅色</el-radio-button>
              <el-radio-button label="dark">深色</el-radio-button>
              <el-radio-button label="auto">跟随系统</el-radio-button>
            </el-radio-group>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.account-view {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
}

.theme-setting {
  display: flex;
  align-items: center;
  gap: 20px;
}
</style>
