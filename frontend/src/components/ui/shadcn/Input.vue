<template>
  <input
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :readonly="readonly"
    :disabled="disabled"
    :maxlength="maxlength"
    class="shadcn-input"
    v-bind="$attrs"
    @input="onInput"
  />
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue?: string | number
  type?: string
  placeholder?: string
  readonly?: boolean
  disabled?: boolean
  maxlength?: number
}>(), {
  modelValue: '',
  type: 'text',
  placeholder: '',
  readonly: false,
  disabled: false,
  maxlength: undefined
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const onInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<style scoped>
.shadcn-input {
  width: 100%;
  height: 38px;
  padding: 0 12px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #fff;
  color: #0a0a0a;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
}

.shadcn-input::placeholder {
  color: #9ca3af;
}

.shadcn-input:hover {
  border-color: #9ca3af;
}

.shadcn-input:focus {
  border-color: #0a0a0a;
  box-shadow: 0 0 0 3px rgba(10, 10, 10, 0.12);
}

.shadcn-input:disabled,
.shadcn-input:read-only {
  background: #f9fafb;
  color: #6b7280;
}
</style>
