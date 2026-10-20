<template>
  <div class="container-scroll-wrapper">
    <div class="scroll-animation-section" ref="sectionRef">
      <div class="scroll-title">
        <h1 class="text-4xl font-semibold text-white">
          解锁 <br />
          <span class="text-4xl md:text-[6rem] font-bold mt-1 leading-none text-white">
            AI互动的潜能
          </span>
        </h1>
      </div>
      <div class="scroll-card" :style="cardStyle">
        <div class="card-content">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const sectionRef = ref<HTMLElement>()
const scrollY = ref(0)

const handleScroll = () => {
  scrollY.value = window.scrollY
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  handleScroll() // 初始化
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const cardStyle = computed(() => {
  // 计算滚动进度 (0-1)
  const sectionTop = sectionRef.value?.offsetTop || 0
  const sectionHeight = sectionRef.value?.offsetHeight || 0
  const windowHeight = window.innerHeight

  const scrollProgress = Math.max(0, Math.min(1,
    (scrollY.value - sectionTop + windowHeight) / (sectionHeight + windowHeight)
  ))

  // 根据滚动进度计算角度 (从15度到-5度)
  const rotateX = 15 - (scrollProgress * 20)
  const scale = 0.95 + (scrollProgress * 0.05)

  return {
    transform: `perspective(1000px) rotateX(${rotateX}deg) scale(${scale})`
  }
})
</script>

<style scoped>
.container-scroll-wrapper {
  background-color: #050505;
  color: #f8fafc;
  padding: 2rem;
}

.scroll-animation-section {
  height: 40rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.scroll-title {
  text-align: center;
  margin-bottom: 2rem;
  z-index: 2;
}

.scroll-card {
  width: 100%;
  max-width: 80rem;
  height: 70rem;
  border: 4px solid #6C6C6C;
  border-radius: 30px;
  background: #222222;
  box-shadow: 0 0 #0000004d, 0 9px 20px #0000004a, 0 37px 37px #00000042, 0 84px 50px #00000026, 0 149px 60px #0000000a, 0 233px 65px #00000003;
  transform: perspective(1000px) rotateX(15deg) scale(0.95);
  transition: transform 0.1s ease-out;
  overflow: hidden;
}

.card-content {
  height: 100%;
  padding: 0.25rem;
  background: #f8fafc;
  border-radius: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-content img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 18px;
}

@media (min-width: 768px) {
  .scroll-card {
    height: 90rem;
  }

  .card-content {
    padding: 0.5rem;
  }
}
</style>