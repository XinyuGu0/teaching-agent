<template>
  <div class="tpl-card">
    <a
      class="img-preview"
      :href="resolvedLink"
      target="_blank"
      rel="noopener noreferrer"
      @click="onPreview"
    >
      <img :src="resolvedImage" :alt="item.name" @error="onImageError" />
    </a>

    <a
      class="p-title"
      :href="resolvedLink"
      target="_blank"
      rel="noopener noreferrer"
      @click="onPreview"
    >
      {{ item.name }}
    </a>

    <div class="meta clear">
      <span class="left">{{ item.motion_type || '动态' }} - {{ item.slide_count || 0 }}页</span>
      <span class="right" @click="onDownload">{{ item.download_count || 0 }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true }
})

const emit = defineEmits(['preview', 'like', 'download'])

const SOURCE_BASE = 'https://www.ypppt.com'
const DEFAULT_PREVIEW_IMAGE = 'https://www.ypppt.com/uploads/allimg/161126/1-161126124403-lp.jpg'

const toAbsoluteUrl = (url) => {
  if (!url) return '#'
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  if (url.startsWith('//')) return `https:${url}`
  if (url.startsWith('/')) return `${SOURCE_BASE}${url}`
  return `${SOURCE_BASE}/${url}`
}

const resolvedLink = computed(() => toAbsoluteUrl(props.item.source_url || '#'))
const resolvedImage = computed(() => {
  const imageUrl = props.item.thumbnail_url || DEFAULT_PREVIEW_IMAGE
  return toAbsoluteUrl(imageUrl)
})

const onImageError = (event) => {
  const img = event?.target
  if (img && img.src !== DEFAULT_PREVIEW_IMAGE) {
    img.src = DEFAULT_PREVIEW_IMAGE
  }
}

const onPreview = () => {
  emit('preview', props.item)
}

const onDownload = () => {
  emit('download', props.item)
}
</script>

<style scoped>
.tpl-card {
  background: transparent;
  border: none;
  border-radius: 0;
  overflow: hidden;
  transition: opacity .2s ease;
  padding: 0;
}

.tpl-card:hover {
  opacity: .92;
}

.img-preview {
  display: block;
  width: 100%;
  border-radius: 6px;
  overflow: hidden;
  background: #0f172a;
  border: 1px solid rgba(148, 163, 184, .2);
}

.img-preview img {
  width: 100%;
  height: auto;
  object-fit: contain;
  display: block;
}

.placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 13px;
}

.p-title {
  display: block;
  margin-top: 8px;
  color: #e5e7eb;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  line-height: 1.4;
}

.p-title:hover {
  color: #93c5fd;
}

.meta {
  margin-top: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #94a3b8;
}

.right {
  color: #cbd5e1;
  cursor: pointer;
}

.right:hover {
  color: #93c5fd;
}
</style>
