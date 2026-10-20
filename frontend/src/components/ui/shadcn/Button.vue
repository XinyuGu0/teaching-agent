<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'shadcn-btn',
      `variant-${variant}`,
      `size-${size}`,
      { 'is-loading': loading }
    ]"
    v-bind="$attrs"
    @click="handleClick"
  >
    <span v-if="loading" class="spinner" aria-hidden="true" />
    <slot />
  </button>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  variant?: 'default' | 'outline' | 'ghost' | 'secondary'
  size?: 'sm' | 'md' | 'lg' | 'icon'
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
  loading?: boolean
}>(), {
  variant: 'default',
  size: 'md',
  type: 'button',
  disabled: false,
  loading: false
})

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

const handleClick = (event: MouseEvent) => {
  emit('click', event)
}
</script>

<style scoped>
.shadcn-btn {
  --btn-bg: #0a0a0a;
  --btn-color: #f9fafb;
  --btn-border: #0a0a0a;

  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 10px;
  border: 1px solid var(--btn-border);
  background: var(--btn-bg);
  color: var(--btn-color);
  font-size: 14px;
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.shadcn-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.02);
}

.shadcn-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.variant-default {
  --btn-bg: #0a0a0a;
  --btn-color: #f9fafb;
  --btn-border: #0a0a0a;
}

.variant-default:hover:not(:disabled) {
  --btn-bg: #1a1a1a;
}

.variant-outline {
  --btn-bg: #ffffff;
  --btn-color: #0a0a0a;
  --btn-border: #d1d5db;
}

.variant-outline:hover:not(:disabled) {
  --btn-bg: #f9fafb;
}

.variant-ghost {
  --btn-bg: transparent;
  --btn-color: #525252;
  --btn-border: transparent;
}

.variant-ghost:hover:not(:disabled) {
  --btn-bg: #f3f4f6;
}

.variant-secondary {
  --btn-bg: #f3f4f6;
  --btn-color: #0a0a0a;
  --btn-border: #e5e7eb;
}

.size-sm {
  height: 34px;
  padding: 0 12px;
  font-size: 13px;
}

.size-md {
  height: 38px;
  padding: 0 14px;
}

.size-lg {
  height: 42px;
  padding: 0 18px;
  font-size: 15px;
}

.size-icon {
  width: 34px;
  height: 34px;
  padding: 0;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 999px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
