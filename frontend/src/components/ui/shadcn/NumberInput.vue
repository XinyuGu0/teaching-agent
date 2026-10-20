<template>
  <div class="shadcn-number-input">
    <button type="button" class="step-btn" :disabled="disabled" @click="decrease">−</button>
    <input
      :value="displayValue"
      :disabled="disabled"
      :placeholder="placeholder"
      class="number-field"
      @input="handleInput"
      @blur="normalize"
    />
    <button type="button" class="step-btn" :disabled="disabled" @click="increase">+</button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  modelValue?: number | null
  min?: number
  max?: number
  step?: number
  placeholder?: string
  disabled?: boolean
}>(), {
  modelValue: null,
  min: Number.NEGATIVE_INFINITY,
  max: Number.POSITIVE_INFINITY,
  step: 1,
  placeholder: '',
  disabled: false
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: number | null): void
}>()

const displayValue = computed(() => {
  if (props.modelValue === null || props.modelValue === undefined) return ''
  return String(props.modelValue)
})

const clamp = (value: number) => {
  return Math.min(props.max, Math.max(props.min, value))
}

const increase = () => {
  const base = props.modelValue ?? Math.max(props.min, 0)
  emit('update:modelValue', clamp(base + props.step))
}

const decrease = () => {
  const base = props.modelValue ?? Math.max(props.min, 0)
  emit('update:modelValue', clamp(base - props.step))
}

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const raw = target.value.trim()
  if (!raw) {
    emit('update:modelValue', null)
    return
  }

  const num = Number(raw)
  if (Number.isNaN(num)) return
  emit('update:modelValue', num)
}

const normalize = () => {
  if (props.modelValue === null || props.modelValue === undefined) return
  emit('update:modelValue', clamp(props.modelValue))
}
</script>

<style scoped>
.shadcn-number-input {
  width: 100%;
  height: 38px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #fff;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.step-btn {
  width: 36px;
  height: 100%;
  border: none;
  background: #f9fafb;
  color: #374151;
  font-size: 18px;
  cursor: pointer;
}

.step-btn:hover:not(:disabled) {
  background: #f3f4f6;
}

.number-field {
  flex: 1;
  height: 100%;
  border: none;
  outline: none;
  text-align: center;
  font-size: 14px;
  color: #0a0a0a;
}
</style>
