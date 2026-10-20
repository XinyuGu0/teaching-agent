<template>
  <div v-if="visible" class="overlay" @click.self="$emit('close')">
    <div class="panel">
      <h3>导入分享码</h3>
      <p class="tip">支持知识库分享码（示例：KB-A3F9X2K8）</p>

      <div class="row">
        <input
          v-model.trim="localCode"
          class="input"
          placeholder="请输入分享码"
          @keyup.enter="handlePreview"
        />
        <button class="btn" :disabled="loading || !localCode" @click="handlePreview">查询</button>
      </div>

      <div v-if="previewData" class="preview">
        <div class="name">{{ previewData.name }}</div>
        <div class="desc">{{ previewData.description }}</div>
        <div class="meta">作者：{{ previewData.author?.name || '未知' }} ｜ 文件数：{{ previewData.document_count || '-' }}</div>
      </div>

      <div class="footer">
        <button class="btn ghost" @click="$emit('close')">取消</button>
        <button class="btn primary" :disabled="loading || !previewData" @click="$emit('import', localCode)">
          {{ loading ? '导入中...' : '确认导入' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: Boolean,
  loading: Boolean,
  previewData: Object,
  modelValue: String
})

const emit = defineEmits(['close', 'preview', 'import', 'update:modelValue'])

const localCode = ref(props.modelValue || '')

watch(() => props.modelValue, (v) => {
  localCode.value = v || ''
})

watch(localCode, (v) => {
  emit('update:modelValue', v)
})

const handlePreview = () => {
  if (!localCode.value) return
  emit('preview', localCode.value)
}
</script>

<style scoped>
.overlay { position: fixed; inset: 0; background: rgba(2, 8, 23, .65); display: flex; align-items: center; justify-content: center; z-index: 2100; }
.panel { width: min(560px, 92vw); background: #0b1220; border: 1px solid rgba(148, 163, 184, .16); border-radius: 14px; padding: 18px; }
h3 { margin: 0 0 6px; color: #e2e8f0; }
.tip { margin: 0 0 12px; color: #94a3b8; font-size: 13px; }
.row { display: flex; gap: 8px; }
.input { flex: 1; border: 1px solid rgba(148, 163, 184, .24); background: #0f172a; color: #e2e8f0; border-radius: 8px; padding: 9px 12px; }
.btn { border: 1px solid rgba(148, 163, 184, .24); background: #1e293b; color: #e2e8f0; border-radius: 8px; padding: 9px 14px; cursor: pointer; }
.btn.primary { background: #2563eb; border-color: #2563eb; }
.btn.ghost { background: transparent; }
.preview { margin-top: 12px; border: 1px dashed rgba(148, 163, 184, .24); border-radius: 10px; padding: 10px; }
.name { color: #e2e8f0; font-weight: 600; }
.desc { margin-top: 6px; color: #94a3b8; font-size: 13px; }
.meta { margin-top: 6px; color: #64748b; font-size: 12px; }
.footer { margin-top: 14px; display: flex; justify-content: flex-end; gap: 8px; }
</style>
