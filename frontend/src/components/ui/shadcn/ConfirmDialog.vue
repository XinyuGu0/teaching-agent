<template>
  <Teleport to="body">
    <div v-if="open" class="dialog-overlay" @click.self="handleCancel">
      <div class="dialog-panel confirm-dialog">
        <div class="dialog-header">
          <span class="dialog-title">{{ title }}</span>
          <button class="dialog-close" @click="handleCancel">
            <X :size="18" />
          </button>
        </div>
        <div class="dialog-body">
          <p class="confirm-message">{{ message }}</p>
        </div>
        <div class="dialog-footer">
          <UiButton variant="outline" @click="handleCancel">{{ cancelText }}</UiButton>
          <UiButton variant="default" @click="handleConfirm">{{ confirmText }}</UiButton>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'
import UiButton from './Button.vue'

withDefaults(defineProps<{
  open: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
}>(), {
  title: '提示',
  message: '',
  confirmText: '确定',
  cancelText: '取消'
})

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const handleConfirm = () => emit('confirm')
const handleCancel = () => emit('cancel')
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-panel {
  background: #111111;
  border: 1px solid #2a2a2a;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

.confirm-dialog {
  width: 420px;
  max-width: 90vw;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #2a2a2a;
}

.dialog-title {
  font-size: 16px;
  font-weight: 600;
  color: #f3f4f6;
}

.dialog-close {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  border-radius: 6px;
  transition: all 0.15s;
}

.dialog-close:hover {
  background: #1f1f1f;
  color: #f3f4f6;
}

.dialog-body {
  padding: 20px;
}

.confirm-message {
  margin: 0;
  font-size: 14px;
  color: #d1d5db;
  line-height: 1.6;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 14px 20px;
  border-top: 1px solid #2a2a2a;
}
</style>
