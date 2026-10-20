<template>
  <div class="kb-card" @click="$emit('preview', item)">
    <div class="kb-head">
      <h3 class="kb-title">{{ item.name }}</h3>
      <span class="kb-code">{{ item.share_code }}</span>
    </div>

    <p class="kb-desc">{{ item.description }}</p>

    <div class="kb-tags">
      <span v-for="tag in item.tags?.slice(0, 3)" :key="tag" class="tag">#{{ tag }}</span>
    </div>

    <div class="kb-meta">
      <span class="meta-item">
        <FileText :size="13" />
        {{ item.document_count }} 文件
      </span>
      <span class="meta-item">
        <Download :size="13" />
        {{ item.import_count }}
      </span>
      <span class="meta-item">
        <User2 :size="13" />
        {{ item.author?.name || '匿名用户' }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { FileText, Download, User2 } from 'lucide-vue-next'

defineProps({
  item: {
    type: Object,
    required: true
  }
})

defineEmits(['preview'])
</script>

<style scoped>
.kb-card {
  background: rgba(15, 23, 42, .72);
  border: 1px solid rgba(148, 163, 184, .16);
  border-radius: 14px;
  padding: 14px;
  cursor: pointer;
  transition: all .2s ease;
  min-height: 170px;
}
.kb-card:hover { border-color: rgba(59, 130, 246, .45); transform: translateY(-2px); }
.kb-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.kb-title { margin: 0; font-size: 15px; color: #e2e8f0; }
.kb-code { font-size: 11px; color: #60a5fa; background: rgba(59, 130, 246, .1); border: 1px solid rgba(59, 130, 246, .25); border-radius: 999px; padding: 2px 8px; white-space: nowrap; }
.kb-desc { margin: 10px 0; font-size: 13px; color: #94a3b8; line-height: 1.5; }
.kb-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.tag { font-size: 12px; color: #cbd5e1; background: rgba(30, 41, 59, .8); border: 1px solid rgba(148, 163, 184, .14); border-radius: 999px; padding: 2px 8px; }
.kb-meta { display: flex; flex-wrap: wrap; gap: 10px; color: #94a3b8; font-size: 12px; }
.meta-item { display: inline-flex; align-items: center; gap: 4px; }
</style>
