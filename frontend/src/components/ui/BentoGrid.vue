<template>
  <div class="bento-grid">
    <div
      v-for="(item, index) in items"
      :key="index"
      :class="['bento-card', `col-span-${item.colSpan || 1}`]"
      :style="{ gridColumn: `span ${item.colSpan || 1}` }"
    >
      <div class="card-header">
        <div class="icon-wrapper" :class="item.iconClass">
          <component :is="item.icon" v-if="item.icon" class="icon" />
        </div>
        <div class="card-meta">
          <h3 class="card-title">{{ item.title }}</h3>
          <span v-if="item.meta" class="meta-text">{{ item.meta }}</span>
        </div>
      </div>

      <p class="card-description">{{ item.description }}</p>

      <div v-if="item.tags" class="card-tags">
        <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
      </div>

      <div v-if="item.status" class="card-status">
        <span :class="['status-dot', `status-${item.status.toLowerCase()}`]"></span>
        {{ item.status }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BentoItem } from '@/types/bento'

defineProps<{
  items: BentoItem[]
}>()
</script>

<style scoped>
.bento-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  padding: 2rem;
  max-width: 1280px;
  margin: 0 auto;
}

.bento-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1.5rem;
  padding: 2rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.bento-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.col-span-2 {
  grid-column: span 2;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.icon-wrapper {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
}

.icon {
  width: 1.5rem;
  height: 1.5rem;
}

.card-meta {
  flex: 1;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  color: #f8fafc;
}

.meta-text {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
}

.card-description {
  font-size: 0.875rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 1rem;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tag {
  padding: 0.25rem 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  font-size: 0.75rem;
  color: rgba(255, 255,  255, 0.8);
}

.card-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
}

.status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.status-live {
  background: #10b981;
}

.status-updated {
  background: #3b82f6;
}

.status-beta {
  background: #f59e0b;
}

@media (max-width: 768px) {
  .bento-grid {
    grid-template-columns: 1fr;
  }
  
  .col-span-2 {
    grid-column: span 1;
  }
}
</style>
