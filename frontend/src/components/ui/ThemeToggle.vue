<template>
  <Teleport to="body">
    <button
      class="theme-toggle-btn"
      :title="themeStore.isDark ? '切换到亮色模式' : '切换到暗色模式'"
      @click="themeStore.toggleTheme()"
    >
      <Moon v-if="themeStore.isDark" :size="16" />
      <Sun v-else :size="16" />
    </button>
  </Teleport>
</template>

<script setup>
import { Sun, Moon } from 'lucide-vue-next'
import { useThemeStore } from '@/store/modules/theme'

const themeStore = useThemeStore()
</script>

<style scoped>
.theme-toggle-btn {
  position: fixed;
  bottom: 24px;
  left: 24px;
  z-index: 9999;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(20, 20, 24, 0.85);
  backdrop-filter: blur(16px);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
}

.theme-toggle-btn:hover {
  background: rgba(30, 30, 36, 0.95);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

:global(:root[data-theme='light']) .theme-toggle-btn {
  border-color: rgba(0, 0, 0, 0.12);
  background: rgba(255, 255, 255, 0.85);
  color: rgba(0, 0, 0, 0.65);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

:global(:root[data-theme='light']) .theme-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  color: rgba(0, 0, 0, 0.85);
  border-color: rgba(0, 0, 0, 0.2);
}
</style>
