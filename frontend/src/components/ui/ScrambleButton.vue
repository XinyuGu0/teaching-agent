<template>
  <button
    @mouseenter="scramble"
    @click="handleClick"
    class="px-8 py-3 bg-primary text-primary-foreground rounded-full font-semibold hover:bg-primary/90 transition-colors"
  >
    {{ displayText }}
  </button>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  text: {
    type: String,
    default: '立即体验'
  }
})

const emit = defineEmits(['click'])

const displayText = ref(props.text)
const isScrambling = ref(false)
const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'

const scramble = () => {
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
  }, 30)
}

const handleClick = () => {
  emit('click')
}
</script>

<style scoped>
</style>