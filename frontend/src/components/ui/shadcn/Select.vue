<template>
  <div
    :class="['shadcn-select', { 'is-open': isOpen, 'is-disabled': disabled }]"
    ref="selectRef"
  >
    <button
      type="button"
      class="select-trigger"
      :disabled="disabled"
      @click="toggleOpen"
    >
      <span v-if="displayLabel" class="select-value">{{ displayLabel }}</span>
      <span v-else class="select-placeholder">{{ placeholder }}</span>
      <ChevronDown :size="15" class="select-arrow" />
    </button>

    <Teleport to="body">
      <div v-if="isOpen" class="select-overlay" @click="close">
        <div
          ref="dropdownRef"
          :class="['select-dropdown', `size-${size}`]"
          :style="dropdownStyle"
          @click.stop
        >
          <div
            v-for="option in options"
            :key="option.value"
            :class="['select-option', { 'is-selected': modelValue === option.value }]"
            @click="selectOption(option)"
          >
            <span>{{ option.label }}</span>
            <Check v-if="modelValue === option.value" :size="14" class="option-check" />
          </div>
          <div v-if="options.length === 0" class="select-empty">暂无选项</div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ChevronDown, Check } from 'lucide-vue-next'

export interface SelectOption {
  label: string
  value: string | number | null
}

const props = withDefaults(defineProps<{
  modelValue?: string | number | null
  options?: SelectOption[]
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
  size?: 'sm' | 'md'
}>(), {
  modelValue: null,
  options: () => [],
  placeholder: '请选择',
  disabled: false,
  clearable: false,
  size: 'md'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number | null): void
  (e: 'change', value: string | number | null): void
}>()

const selectRef = ref<HTMLElement | null>(null)
const dropdownRef = ref<HTMLElement | null>(null)
const isOpen = ref(false)

const displayLabel = computed(() => {
  if (props.modelValue === null || props.modelValue === undefined) return ''
  const found = props.options.find(o => o.value === props.modelValue)
  return found ? found.label : ''
})

const dropdownStyle = computed(() => {
  if (!selectRef.value) return {}
  const rect = selectRef.value.getBoundingClientRect()
  return {
    top: `${rect.bottom + 4}px`,
    left: `${rect.left}px`,
    minWidth: `${Math.max(rect.width, 160)}px`
  }
})

const toggleOpen = () => {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

const close = () => {
  isOpen.value = false
}

const selectOption = (option: SelectOption) => {
  emit('update:modelValue', option.value)
  emit('change', option.value)
  close()
}

const handleClickOutside = (e: MouseEvent) => {
  if (!isOpen.value) return
  const target = e.target as Node
  const clickedTrigger = !!(selectRef.value && selectRef.value.contains(target))
  const clickedDropdown = !!(dropdownRef.value && dropdownRef.value.contains(target))
  if (!clickedTrigger && !clickedDropdown) close()
}

const handleScroll = () => {
  if (isOpen.value) close()
}

const handleResize = () => {
  if (isOpen.value) close()
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
  document.addEventListener('scroll', handleScroll, true)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
  document.removeEventListener('scroll', handleScroll, true)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.shadcn-select {
  position: relative;
  display: inline-flex;
  width: 100%;
}

.select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 38px;
  padding: 0 12px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #fff;
  color: #0a0a0a;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.select-trigger:hover {
  border-color: #9ca3af;
}

.shadcn-select.is-open .select-trigger {
  border-color: #0a0a0a;
  box-shadow: 0 0 0 3px rgba(10, 10, 10, 0.12);
}

.select-trigger:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.select-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-placeholder {
  flex: 1;
  color: #9ca3af;
}

.select-arrow {
  flex-shrink: 0;
  color: #6b7280;
  transition: transform 0.2s;
}

.shadcn-select.is-open .select-arrow {
  transform: rotate(180deg);
}

/* Overlay */
.select-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
}

/* Dropdown */
.select-dropdown {
  position: fixed;
  z-index: 2001;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  padding: 4px;
  max-height: 240px;
  overflow-y: auto;
}

.size-sm .select-trigger {
  height: 34px;
  padding: 0 10px;
  font-size: 13px;
}

.size-sm .select-dropdown {
  font-size: 13px;
}

/* Option */
.select-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 7px;
  font-size: 14px;
  color: #0a0a0a;
  cursor: pointer;
  transition: background 0.15s;
}

.select-option:hover {
  background: #f3f4f6;
}

.select-option.is-selected {
  background: #f3f4f6;
  font-weight: 500;
}

.option-check {
  color: #0a0a0a;
  flex-shrink: 0;
}

.select-empty {
  padding: 16px;
  text-align: center;
  color: #9ca3af;
  font-size: 13px;
}
</style>
