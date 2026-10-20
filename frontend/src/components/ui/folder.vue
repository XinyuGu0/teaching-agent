<template>
  <button
    type="button"
    class="folder-card"
    :class="{ 'is-active': active }"
    @click="$emit('select')"
  >
    <div class="folder-3d" aria-hidden="true">
      <div class="work-5" />
      <div class="work-4" />
      <div class="work-3" />
      <div class="work-2" />
      <div class="work-1" />
    </div>

    <div class="folder-meta">
      <div class="folder-title-row">
        <span class="folder-title">{{ title }}</span>
        <span class="folder-count">{{ count }}</span>
      </div>
      <p class="folder-subtitle">{{ subtitle }}</p>
    </div>
  </button>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: '文件夹'
  },
  subtitle: {
    type: String,
    default: ''
  },
  count: {
    type: Number,
    default: 0
  },
  active: {
    type: Boolean,
    default: false
  }
})

defineEmits(['select'])
</script>

<style scoped>
.folder-card {
  width: 100%;
  border: 1px solid #2a2a2a;
  border-radius: 14px;
  background: #121212;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  text-align: left;
  transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease, background .25s ease;
}

.folder-card:hover {
  transform: translateY(-2px);
  border-color: #52525b;
  background: #161616;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
}

.folder-card.is-active {
  border-color: #f3f4f6;
  box-shadow: 0 0 0 1px rgba(243, 244, 246, 0.25) inset;
}

.folder-3d {
  position: relative;
  width: 84px;
  min-width: 84px;
  height: 58px;
  perspective: 1200px;
}

.work-5,
.work-4,
.work-3,
.work-2,
.work-1 {
  position: absolute;
  inset: 0;
  border-radius: 10px;
  transform-origin: bottom;
  transition: transform .3s ease;
}

.work-5 {
  background: #b45309;
  border-top-left-radius: 0;
}

.work-4 {
  inset: 2px;
  background: #52525b;
}

.work-3 {
  inset: 3px;
  background: #71717a;
}

.work-2 {
  inset: 4px;
  background: #a1a1aa;
}

.work-1 {
  inset: 5px 3px 0;
  background: linear-gradient(180deg, #fbbf24 0%, #d97706 100%);
  border-top-right-radius: 0;
}

.folder-card:hover .work-4 {
  transform: rotateX(-16deg);
}

.folder-card:hover .work-3 {
  transform: rotateX(-24deg);
}

.folder-card:hover .work-2 {
  transform: rotateX(-32deg);
}

.folder-card:hover .work-1 {
  transform: rotateX(-40deg) translateY(1px);
}

.folder-meta {
  min-width: 0;
  flex: 1;
}

.folder-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.folder-title {
  font-size: 15px;
  font-weight: 600;
  color: #f3f4f6;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.folder-count {
  padding: 2px 8px;
  border-radius: 9999px;
  background: #1f2937;
  color: #e5e7eb;
  font-size: 12px;
}

.folder-subtitle {
  margin: 6px 0 0;
  color: #9ca3af;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
