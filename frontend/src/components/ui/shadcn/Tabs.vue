<template>
  <div :class="['shadcn-tabs', `variant-${variant}`, `size-${size}`]" role="tablist" :aria-label="ariaLabel">
    <button
      v-for="item in options"
      :key="String(item.value)"
      type="button"
      role="tab"
      :aria-selected="modelValue === item.value"
      :class="['tab-trigger', { 'is-active': modelValue === item.value }]"
      @click="onSelect(item.value)"
    >
      {{ item.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
export interface TabsOption {
  label: string
  value: string | number
}

withDefaults(defineProps<{
  modelValue: string | number
  options: TabsOption[]
  variant?: 'default' | 'underline' | 'pill' | 'rounded' | 'folder'
  size?: 'sm' | 'md'
  ariaLabel?: string
}>(), {
  variant: 'underline',
  size: 'md',
  ariaLabel: 'tabs'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
  (e: 'change', value: string | number): void
}>()

const onSelect = (value: string | number) => {
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<style scoped>
.shadcn-tabs {
  display: inline-flex;
  align-items: center;
}

.tab-trigger {
  border: 0;
  background: transparent;
  color: #94a3b8;
  font-weight: 600;
  cursor: pointer;
  transition: all .18s ease;
  white-space: nowrap;
}

.tab-trigger:hover {
  color: #e2e8f0;
}

.size-sm .tab-trigger {
  font-size: 12px;
  padding: 6px 10px;
}

.size-md .tab-trigger {
  font-size: 13px;
  padding: 8px 12px;
}

/* underline */
.variant-underline {
  gap: 2px;
  border-bottom: 1px solid rgba(148, 163, 184, .22);
}

.variant-underline .tab-trigger {
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.variant-underline .tab-trigger.is-active {
  color: #ffffff;
  border-bottom-color: #60a5fa;
}

/* pill */
.variant-pill {
  background: rgba(30, 41, 59, .55);
  border: 1px solid rgba(148, 163, 184, .28);
  border-radius: 999px;
  padding: 2px;
  gap: 2px;
}

.variant-pill .tab-trigger {
  border-radius: 999px;
}

.variant-pill .tab-trigger.is-active {
  background: #ffffff;
  color: #111827;
}

/* rounded */
.variant-rounded {
  background: rgba(30, 41, 59, .55);
  border: 1px solid rgba(148, 163, 184, .28);
  border-radius: 12px;
  padding: 3px;
  gap: 3px;
}

.variant-rounded .tab-trigger {
  border-radius: 10px;
}

.variant-rounded .tab-trigger.is-active {
  background: rgba(96, 165, 250, .2);
  color: #fff;
}

/* folder */
.variant-folder {
  border-bottom: 1px solid rgba(148, 163, 184, .25);
  gap: 6px;
}

.variant-folder .tab-trigger {
  border: 1px solid transparent;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  margin-bottom: -1px;
}

.variant-folder .tab-trigger.is-active {
  background: #0f172a;
  border-color: rgba(148, 163, 184, .3);
  border-bottom-color: #0f172a;
  color: #fff;
}

/* default */
.variant-default {
  background: rgba(30, 41, 59, .55);
  border: 1px solid rgba(148, 163, 184, .22);
  border-radius: 10px;
  padding: 3px;
  gap: 3px;
}

.variant-default .tab-trigger {
  border-radius: 8px;
}

.variant-default .tab-trigger.is-active {
  background: #ffffff;
  color: #111827;
}
</style>
