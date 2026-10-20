<template>
  <button class="anim-btn" :disabled="disabled" @click="$emit('click')">
    <span class="anim-btn-bg"></span>
    <span class="anim-btn-text">{{ text }}</span>
  </button>
</template>

<script setup>
defineProps({
  text: { type: String, default: 'Button' },
  disabled: { type: Boolean, default: false }
})
defineEmits(['click'])
</script>

<style scoped>
.anim-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 24px;
  font-size: 14px;
  font-weight: 500;
  color: #181818;
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  overflow: hidden;
  transition: background 0.3s ease;
  line-height: 1.5;
}

.anim-btn:hover:not(:disabled) {
  background: #ffffff;
}

.anim-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.anim-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* Sliding background */
.anim-btn-bg {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 192px;
  height: 192px;
  border-radius: 50%;
  background: #7c3aed;
  transform: translateX(-100%) translateY(100%) rotate(-40deg);
  transition: all 0.5s ease-out;
  margin-bottom: 36px;
  margin-left: 36px;
  z-index: 0;
}

.anim-btn:hover:not(:disabled) .anim-btn-bg {
  margin-left: 0;
  margin-bottom: 128px;
  transform: translateX(0) translateY(100%) rotate(-40deg);
}

/* Text */
.anim-btn-text {
  position: relative;
  z-index: 1;
  width: 100%;
  text-align: left;
  color: #181818;
  transition: color 0.3s ease-in-out;
}

.anim-btn:hover:not(:disabled) .anim-btn-text {
  color: #ffffff;
}
</style>
