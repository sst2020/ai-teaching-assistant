<script setup lang="ts">
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

const getIcon = (type: string) => {
  switch (type) {
    case 'success': return 'CircleCheck'
    case 'error': return 'CircleClose'
    case 'warning': return 'Warning'
    default: return 'InfoFilled'
  }
}
</script>

<template>
  <div class="toast-container">
    <transition-group name="toast">
      <el-alert
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        :title="toast.message"
        :type="toast.type"
        :closable="true"
        @close="toastStore.removeToast(toast.id)"
        show-icon
        class="toast-item"
      >
        <template #icon>
          <el-icon>
            <component :is="getIcon(toast.type)" />
          </el-icon>
        </template>
      </el-alert>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9999;
  width: 350px;
}

.toast-item {
  margin-bottom: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
