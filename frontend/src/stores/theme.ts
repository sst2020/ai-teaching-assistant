import { ref, watch } from 'vue'
import { defineStore } from 'pinia'

type Theme = 'light' | 'dark' | 'auto'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>('light')
  const isDark = ref(false)

  // Initialize theme from localStorage
  const initTheme = () => {
    const saved = localStorage.getItem('theme') as Theme
    if (saved) {
      theme.value = saved
    }
    applyTheme()
  }

  const setTheme = (newTheme: Theme) => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme()
  }

  const applyTheme = () => {
    const html = document.documentElement

    if (theme.value === 'dark') {
      isDark.value = true
      html.classList.add('dark')
    } else if (theme.value === 'light') {
      isDark.value = false
      html.classList.remove('dark')
    } else {
      // Auto - use system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      isDark.value = prefersDark
      if (prefersDark) {
        html.classList.add('dark')
      } else {
        html.classList.remove('dark')
      }
    }
  }

  const toggleTheme = () => {
    setTheme(isDark.value ? 'light' : 'dark')
  }

  // Watch for system theme changes when in auto mode
  if (typeof window !== 'undefined') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (theme.value === 'auto') {
        applyTheme()
      }
    })
  }

  return {
    theme,
    isDark,
    initTheme,
    setTheme,
    toggleTheme
  }
})
