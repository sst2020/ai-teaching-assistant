import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { ToastMessage } from '@/types'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref<ToastMessage[]>([])
  let idCounter = 0

  const addToast = (message: string, type: ToastMessage['type'] = 'info', duration = 3000) => {
    const id = `toast-${++idCounter}`
    const toast: ToastMessage = {
      id,
      type,
      message,
      duration
    }

    toasts.value.push(toast)

    // Auto remove after duration
    setTimeout(() => {
      removeToast(id)
    }, duration)

    return id
  }

  const removeToast = (id: string) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const success = (message: string, duration?: number) =>
    addToast(message, 'success', duration)

  const error = (message: string, duration?: number) =>
    addToast(message, 'error', duration || 5000)

  const warning = (message: string, duration?: number) =>
    addToast(message, 'warning', duration)

  const info = (message: string, duration?: number) =>
    addToast(message, 'info', duration)

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info
  }
})
