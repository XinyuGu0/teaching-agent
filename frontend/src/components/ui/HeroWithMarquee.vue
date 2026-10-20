<template>
  <div class="min-h-screen bg-background text-foreground flex items-center overflow-hidden relative">
    <div class="container mx-auto px-6 lg:px-12">
      <div class="grid lg:grid-cols-2 gap-8 items-center">
        <!-- 左侧内容 -->
        <div class="space-y-6">
          <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">
            {{ title }}
          </h1>
          <div class="space-y-1 text-muted-foreground">
            <p class="text-lg">{{ subtitle }}</p>
            <p class="text-lg">{{ description }}</p>
          </div>
          <ScrambleButton :text="buttonText" @click="handleClick" />
        </div>

        <!-- 右侧 Marquee 网格 -->
        <div class="space-y-4 overflow-hidden">
          <Marquee :speed="30" reverse class="[--gap:1rem]">
            <div
              v-for="(src, idx) in images1"
              :key="idx"
              class="relative w-48 h-48 rounded-2xl overflow-hidden flex-shrink-0"
            >
              <img
                :src="src"
                :alt="`教育图片 ${idx + 1}`"
                class="w-full h-full object-cover"
              />
            </div>
          </Marquee>
          <Marquee :speed="30" class="[--gap:1rem]">
            <div
              v-for="(src, idx) in images2"
              :key="idx"
              class="relative w-48 h-48 rounded-2xl overflow-hidden flex-shrink-0"
            >
              <img
                :src="src"
                :alt="`教育图片 ${idx + 5}`"
                class="w-full h-full object-cover"
              />
            </div>
          </Marquee>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Marquee from './Marquee.vue'
import ScrambleButton from './ScrambleButton.vue'

defineProps({
  title: {
    type: String,
    default: '智能体赋能备课\n让教学更精彩'
  },
  subtitle: {
    type: String,
    default: '2025年 教育科技'
  },
  description: {
    type: String,
    default: 'AI驱动的教学工具'
  },
  buttonText: {
    type: String,
    default: '立即体验'
  }
})

const emit = defineEmits(['click'])

// 教育相关的 Unsplash 图片
const images1 = [
  "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&h=400&fit=crop",
  "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=400&h=400&fit=crop",
  "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=400&h=400&fit=crop",
  "https://images.unsplash.com/photo-1588072432836-e10032774350?w=400&h=400&fit=crop"
]

const images2 = [
  "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400&h=400&fit=crop",
  "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=400&fit=crop",
  "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&h=400&fit=crop",
  "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&h=400&fit=crop"
]

const handleClick = () => {
  emit('click')
}
</script>

<style scoped>
</style>