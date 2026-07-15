<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import AppHeader from './components/layout/AppHeader.vue'
import ToastContainer from './components/common/ToastContainer.vue'

const route = useRoute()
const authStore = useAuthStore()
const showHeader = computed(() => !route.meta.hideHeader)

// 应用启动时恢复登录状态
onMounted(async () => {
  if (authStore.token && !authStore.user) {
    await authStore.fetchCurrentUser()
  }
})
</script>

<template>
  <div class="app">
    <ToastContainer />
    <AppHeader v-if="showHeader" />
    <main class="app-main" :class="{ 'no-header': !showHeader }">
      <div class="content-container">
        <RouterView v-slot="{ Component, route: viewRoute }">
          <Transition name="page-fade" mode="out-in">
            <component :is="Component" :key="viewRoute.path" />
          </Transition>
        </RouterView>
      </div>
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f5f7fa;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  padding-top: 80px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  background-image: 
    radial-gradient(at 40% 20%, rgba(120, 119, 198, 0.15) 0px, transparent 50%),
    radial-gradient(at 80% 0%, rgba(227, 133, 133, 0.1) 0px, transparent 50%),
    radial-gradient(at 0% 50%, rgba(128, 202, 231, 0.15) 0px, transparent 50%),
    radial-gradient(at 80% 50%, rgba(199, 134, 199, 0.1) 0px, transparent 50%),
    linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  position: relative;
}

.app-main::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.06) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.app-main.no-header {
  padding-top: 0;
}

.content-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  width: 100%;
  position: relative;
  z-index: 1;
}

/* Page transition animation */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (prefers-reduced-motion: reduce) {
  .page-fade-enter-active,
  .page-fade-leave-active {
    transition: none;
  }
}
</style>
