<template>
  <Teleport to="body">
    <div v-if="open" class="dialog-overlay" @click.self="handleCancel">
      <div class="dialog-panel prompt-dialog">
        <div class="dialog-header">
          <span class="dialog-title">{{ title }}</span>
          <button class="dialog-close" @click="handleCancel">
            <X :size="18" />
          </button>
        </div>
        <div class="dialog-body">
          <p class="prompt-message">{{ message }}</p>
          <UiInput
            ref="inputRef"
            v-model="inputValue"
            class="dark-input"
            :placeholder="inputPlaceholder"
            @keydown.enter="handleConfirm"
          />
          <p v-if="errorMsg" class="input-error">{{ errorMsg }}</p>
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
import { ref, watch, nextTick } from 'vue'
import { X } from 'lucide-vue-next'
import UiButton from './Button.vue'
import UiInput from './Input.vue'

const props = withDefaults(defineProps<{
  open: boolean
  title?: string
  message?: string
  inputValue?: string
  inputPlaceholder?: string
  confirmText?: string
  cancelText?: string
}>(), {
  title: '提示',
  message: '',
  inputValue: '',
  inputPlaceholder: '',
  confirmText: '确定',
  cancelText: '取消'
})

const emit = defineEmits<{
  (e: 'confirm', value: string): void
  (e: 'cancel'): void
}>()

const inputValue = ref(props.inputValue)
const errorMsg = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

watch(() => props.open, (val) => {
  if (val) {
    inputValue.value = props.inputValue
    errorMsg.value = ''
    nextTick(() => {
      inputRef.value?.focus()
      inputRef.value?.select()
    })
  }
})

watch(() => props.inputValue, (val) => {
  if (props.open) inputValue.value = val
})

const handleConfirm = () => {
  if (!inputValue.value.trim()) {
    errorMsg.value = '内容不能为空'
    return
  }
  emit('confirm', inputValue.value.trim())
}

const handleCancel = () => {
  emit('cancel')
}
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

.prompt-dialog {
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
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.prompt-message {
  margin: 0;
  font-size: 14px;
  color: #d1d5db;
  line-height: 1.6;
}

.dark-input :deep(.shadcn-input) {
  background: #171717;
  border-color: #2f2f2f;
  color: #e5e7eb;
}

.dark-input :deep(.shadcn-input::placeholder) {
  color: #6b7280;
}

.dark-input :deep(.shadcn-input:hover) {
  border-color: #4b5563;
}

.dark-input :deep(.shadcn-input:focus) {
  border-color: #6b7280;
  box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.15);
}

.input-error {
  margin: 0;
  font-size: 12px;
  color: #ef4444;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 14px 20px;
  border-top: 1px solid #2a2a2a;
}
</style>
