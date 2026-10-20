<template>
  <span
    :class="[
      'shadcn-tag',
      `variant-${variant}`,
      `size-${size}`
    ]"
  >
    <slot />
  </span>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  variant?: 'default' | 'secondary' | 'outline'
  size?: 'sm' | 'md'
}>(), {
  variant: 'default',
  size: 'sm'
})
</script>

<style scoped>
.shadcn-tag {
  --tag-bg: #0a0a0a;
  --tag-color: #f9fafb;
  --tag-border: #0a0a0a;

  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid var(--tag-border);
  background: var(--tag-bg);
  color: var(--tag-color);
  font-weight: 500;
  line-height: 1;
  white-space: nowrap;
}

.variant-default {
  --tag-bg: #0a0a0a;
  --tag-color: #f9fafb;
  --tag-border: #0a0a0a;
}

.variant-secondary {
  --tag-bg: #f3f4f6;
  --tag-color: #0a0a0a;
  --tag-border: #e5e7eb;
}

.variant-outline {
  --tag-bg: transparent;
  --tag-color: #525252;
  --tag-border: #d1d5db;
}

.size-sm {
  padding: 2px 8px;
  font-size: 11px;
}

.size-md {
  padding: 4px 10px;
  font-size: 12px;
}
</style>
