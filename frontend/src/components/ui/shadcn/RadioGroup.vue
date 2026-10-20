<template>
  <div class="shadcn-radio-group" role="radiogroup">
    <button
      v-for="item in normalizedOptions"
      :key="String(item.value)"
      type="button"
      class="radio-item"
      :class="{ active: item.value === modelValue }"
      role="radio"
      :aria-checked="item.value === modelValue"
      @click="emit('update:modelValue', item.value)"
    >
      <span class="dot" />
      <span>{{ item.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Option = string | { label: string; value: string }

const props = defineProps<{
  modelValue?: string
  options: Option[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const normalizedOptions = computed(() => {
  return (props.options || []).map((item) => {
    if (typeof item === 'string') {
      return { label: item, value: item }
    }
    return item
  })
})
</script>

<style scoped>
.shadcn-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.radio-item {
  border: 1px solid #d1d5db;
  background: #fff;
  color: #374151;
  border-radius: 999px;
  height: 34px;
  padding: 0 12px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.radio-item:hover {
  border-color: #9ca3af;
}

.radio-item .dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  border: 2px solid #9ca3af;
  background: #fff;
}

.radio-item.active {
  border-color: #0a0a0a;
  color: #0a0a0a;
  background: #f9fafb;
}

.radio-item.active .dot {
  border-color: #0a0a0a;
  background: #0a0a0a;
}
</style>
