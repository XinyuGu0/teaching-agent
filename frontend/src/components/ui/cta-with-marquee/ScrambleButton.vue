<template>
  <button
    @mouseenter="startScramble"
    @click="handleClick"
    class="scramble-button"
    :class="{ 'scramble-button--scrambling': isScrambling }"
  >
    {{ displayText }}
  </button>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  text?: string
  intervalMs?: number
}

const props = withDefaults(defineProps<Props>(), {
  text: '立即体验',
  intervalMs: 30
})

const emit = defineEmits<{
  (e: 'click'): void
}>()

const displayText = ref(props.text)
const isScrambling = ref(false)
const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'

watch(() => props.text, (newText) => {
  displayText.value = newText
})

const startScramble = () => {
  if (isScrambling.value) return
  isScrambling.value = true
  
  let iteration = 0
  const maxIterations = props.text.length

  const interval = setInterval(() => {
    displayText.value = props.text
      .split('')
      .map((letter, index) => {
        if (index < iteration) {
          return props.text[index]
        }
        return chars[Math.floor(Math.random() * chars.length)]
      })
      .join('')

    if (iteration >= maxIterations) {
      clearInterval(interval)
      isScrambling.value = false
    }

    iteration += 1 / 3
  }, props.intervalMs)
}

const handleClick = () => {
  emit('click')
}
</script>

<style scoped>
.scramble-button {
  padding: 0.75rem 2rem;
  background-color: #409eff;
  color: #ffffff;
  border-radius: 9999px;
  font-weight: 600;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.scramble-button:hover {
  background-color: #66b1ff;
}

.scramble-button:active {
  transform: scale(0.98);
}

.scramble-button--scrambling {
  font-family: monospace;
}
</style>