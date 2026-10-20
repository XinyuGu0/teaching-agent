<template>
  <div ref="rootRef" class="shadcn-combobox" :class="{ 'is-open': open, 'is-disabled': disabled }">
    <div class="control" @click="focusInput">
      <div class="value-area" :class="{ multiple }">
        <template v-if="multiple">
          <span
            v-for="item in selectedList"
            :key="item"
            class="chip"
          >
            {{ item }}
            <button type="button" class="chip-remove" @click.stop="removeItem(item)">×</button>
          </span>
        </template>

        <input
          ref="inputRef"
          v-model="query"
          class="input"
          :placeholder="multiple && selectedList.length ? '' : placeholder"
          :disabled="disabled"
          @focus="openDropdown"
          @input="handleInput"
          @keydown.enter.prevent="handleEnter"
          @keydown.down.prevent="openDropdown"
          @keydown.esc.prevent="open = false"
          @keydown.backspace="handleBackspace"
        />
      </div>

      <div class="actions">
        <button
          v-if="clearable && canClear"
          type="button"
          class="icon-btn"
          @click.stop="clearAll"
          aria-label="清空"
        >
          ×
        </button>
        <button type="button" class="icon-btn" @click.stop="toggleOpen" aria-label="切换下拉">
          ▾
        </button>
      </div>
    </div>

    <div v-if="open" class="panel">
      <button
        v-for="option in shownOptions"
        :key="option"
        type="button"
        class="option"
        :class="{ selected: isSelected(option) }"
        @mousedown.prevent
        @click="selectOption(option)"
      >
        {{ option }}
      </button>

      <button
        v-if="allowCreate && query.trim() && !hasExactMatch"
        type="button"
        class="option create"
        @mousedown.prevent
        @click="selectOption(query.trim())"
      >
        创建 “{{ query.trim() }}”
      </button>

      <div v-if="!shownOptions.length && !(allowCreate && query.trim() && !hasExactMatch)" class="empty">
        无匹配项
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  modelValue?: string | string[]
  options?: string[]
  multiple?: boolean
  allowCreate?: boolean
  placeholder?: string
  clearable?: boolean
  disabled?: boolean
  fetchSuggestions?: (query: string) => Promise<string[]>
}>(), {
  modelValue: '',
  options: () => [],
  multiple: false,
  allowCreate: false,
  placeholder: '请选择',
  clearable: false,
  disabled: false,
  fetchSuggestions: undefined
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | string[]): void
}>()

const rootRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)
const open = ref(false)
const query = ref('')
const remoteOptions = ref<string[]>([])
let reqId = 0

const selectedList = computed<string[]>(() => {
  if (!props.multiple) return []
  return Array.isArray(props.modelValue) ? props.modelValue : []
})

const mergedOptions = computed(() => {
  const set = new Set<string>([...(props.options || []), ...remoteOptions.value])
  return Array.from(set)
})

const shownOptions = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return mergedOptions.value
  return mergedOptions.value.filter((item) => item.toLowerCase().includes(q))
})

const hasExactMatch = computed(() => mergedOptions.value.includes(query.value.trim()))

const canClear = computed(() => {
  if (props.multiple) return selectedList.value.length > 0 || !!query.value
  return !!String(props.modelValue || '')
})

const openDropdown = () => {
  if (props.disabled) return
  open.value = true
}

const toggleOpen = () => {
  if (props.disabled) return
  open.value = !open.value
  if (open.value) inputRef.value?.focus()
}

const focusInput = () => {
  if (props.disabled) return
  inputRef.value?.focus()
  openDropdown()
}

const isSelected = (option: string) => {
  if (props.multiple) return selectedList.value.includes(option)
  return String(props.modelValue || '') === option
}

const selectOption = (option: string) => {
  if (props.multiple) {
    const next = new Set(selectedList.value)
    if (next.has(option)) {
      next.delete(option)
    } else {
      next.add(option)
    }
    emit('update:modelValue', Array.from(next))
    query.value = ''
    return
  }

  emit('update:modelValue', option)
  query.value = option
  open.value = false
}

const removeItem = (item: string) => {
  const next = selectedList.value.filter((it) => it !== item)
  emit('update:modelValue', next)
}

const clearAll = () => {
  query.value = ''
  emit('update:modelValue', props.multiple ? [] : '')
}

const handleEnter = () => {
  const value = query.value.trim()
  if (!value) return
  if (shownOptions.value.includes(value) || props.allowCreate) {
    selectOption(value)
  }
}

const handleBackspace = () => {
  if (!props.multiple || query.value) return
  if (!selectedList.value.length) return
  const next = [...selectedList.value]
  next.pop()
  emit('update:modelValue', next)
}

const handleInput = async () => {
  if (!props.multiple) {
    emit('update:modelValue', query.value)
  }

  if (!props.fetchSuggestions) return
  const current = ++reqId
  try {
    const items = await props.fetchSuggestions(query.value)
    if (current === reqId) {
      remoteOptions.value = (items || []).filter(Boolean)
    }
  } catch {
    if (current === reqId) {
      remoteOptions.value = []
    }
  }
}

watch(
  () => props.modelValue,
  (value) => {
    if (props.multiple) return
    if (typeof value === 'string' && value !== query.value && !open.value) {
      query.value = value
    }
  },
  { immediate: true }
)

const handleOutsideClick = (event: MouseEvent) => {
  if (!rootRef.value) return
  if (!rootRef.value.contains(event.target as Node)) {
    open.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
.shadcn-combobox {
  position: relative;
}

.control {
  min-height: 40px;
  width: 100%;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #fff;
  display: flex;
  align-items: stretch;
  gap: 6px;
  padding: 3px 8px;
  transition: all 0.2s ease;
}

.value-area {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.value-area.multiple {
  flex-wrap: wrap;
  align-content: center;
  padding: 1px 0;
}

.shadcn-combobox.is-open .control {
  border-color: #0a0a0a;
  box-shadow: 0 0 0 3px rgba(10, 10, 10, 0.12);
}

.input {
  border: none;
  outline: none;
  flex: 1 1 auto;
  min-width: 90px;
  height: 32px;
  font-size: 14px;
  color: #0a0a0a;
  background: transparent;
}

.value-area.multiple .input {
  flex: 1 1 120px;
}

.input::placeholder {
  color: #9ca3af;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  border-radius: 999px;
  min-height: 24px;
  padding: 0 8px;
  font-size: 12px;
  line-height: 1;
  color: #374151;
}

.actions {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  margin-left: 2px;
}

.chip-remove {
  border: none;
  background: transparent;
  cursor: pointer;
  color: #6b7280;
  line-height: 1;
  padding: 0;
}

.icon-btn {
  border: none;
  background: transparent;
  color: #6b7280;
  width: 30px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
}

.icon-btn:hover {
  color: #374151;
}

.panel {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  max-height: 220px;
  overflow: auto;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
  z-index: 50;
  padding: 6px;
}

.option {
  width: 100%;
  text-align: left;
  border: none;
  background: transparent;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 14px;
  color: #0a0a0a;
  cursor: pointer;
}

.option:hover {
  background: #f3f4f6;
}

.option.selected {
  background: #0a0a0a;
  color: #fff;
}

.option.create {
  color: #2563eb;
}

.empty {
  padding: 10px;
  color: #9ca3af;
  font-size: 13px;
}

.is-disabled {
  opacity: 0.65;
}
</style>
