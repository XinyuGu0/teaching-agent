<template>
  <textarea
    :value="modelValue"
    :placeholder="placeholder"
    :maxlength="maxlength"
    :rows="rows"
    class="shadcn-textarea"
    v-bind="$attrs"
    @input="onInput"
  />
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  modelValue?: string
  placeholder?: string
  maxlength?: number
  rows?: number
}>(), {
  modelValue: '',
  placeholder: '',
  maxlength: undefined,
  rows: 4
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const onInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<style scoped>
.shadcn-textarea {
  width: 100%;
  min-height: 104px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #fff;
  color: #0a0a0a;
  font-size: 14px;
  line-height: 1.5;
  outline: none;
  resize: vertical;
  transition: all 0.2s ease;
}

.shadcn-textarea::placeholder {
  color: #9ca3af;
}

.shadcn-textarea:hover {
  border-color: #9ca3af;
}

.shadcn-textarea:focus {
  border-color: #0a0a0a;
  box-shadow: 0 0 0 3px rgba(17, 24, 39, 0.12);
}
</style>
