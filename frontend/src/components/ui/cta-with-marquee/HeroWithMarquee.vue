<template>
  <div class="hero-container">
    <!-- Header -->
    <header class="hero-header">
      <div class="hero-header-inner">
        <h1 class="hero-logo">{{ logoText }}</h1>
        <div class="hero-actions hero-header-actions">
          <button type="button" class="hero-header-button" @click="$emit('login')">{{ loginText }}</button>
          <button type="button" class="hero-header-button hero-header-button-primary" @click="$emit('register')">{{ registerText }}</button>
        </div>
      </div>
    </header>

    <!-- Hero Content -->
    <div class="hero-content">
      <div class="hero-grid">
        <!-- Left: Text Content -->
        <div class="hero-text">
          <h2 class="hero-title" v-html="title"></h2>
          <div class="hero-meta">
            <p class="hero-subtitle">{{ subtitle }}</p>
            <p class="hero-description">{{ description }}</p>
          </div>
          <div class="hero-actions">
            <div class="hero-button-frame">
              <button class="hero-button hero-button-primary" @click="$emit('cta')">
                <span>{{ ctaText }}</span>
              </button>
            </div>
            <button class="hero-button hero-button-ghost" @click="$emit('register')">
              <span>{{ registerText }}</span>
            </button>
          </div>
        </div>

        <!-- Right: Marquee Images -->
        <div class="hero-marquee">
          <MarqueeRow :speed="30" :reverse="true" :gap="16">
            <div
              v-for="(src, idx) in imagesRow1"
              :key="`row1-${idx}`"
              class="marquee-item"
            >
              <img
                :src="src"
                :alt="`教育图片 ${idx + 1}`"
                class="marquee-image"
                loading="lazy"
              />
            </div>
          </MarqueeRow>
          <MarqueeRow :speed="30" :gap="16">
            <div
              v-for="(src, idx) in imagesRow2"
              :key="`row2-${idx}`"
              class="marquee-item"
            >
              <img
                :src="src"
                :alt="`教育图片 ${idx + 5}`"
                class="marquee-image"
                loading="lazy"
              />
            </div>
          </MarqueeRow>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import MarqueeRow from './MarqueeRow.vue'

/**
 * HeroWithMarquee Component
 * 
 * A landing page hero section with animated marquee image rows.
 * Perfect for marketing pages, product launches, or educational platforms.
 * 
 * @example
 * <HeroWithMarquee
 *   title="智能PPT生成"
 *   subtitle="教育科技创新"
 *   :images="customImages"
 *   @cta="handleCta"
 * />
 */

interface Props {
  /** Main hero title */
  title?: string
  /** Subtitle text */
  subtitle?: string
  /** Description text */
  description?: string
  /** CTA button text */
  ctaText?: string
  /** Logo text */
  logoText?: string
  /** Login button text */
  loginText?: string
  /** Register button text */
  registerText?: string
  /** Custom images for first row */
  imagesRow1?: string[]
  /** Custom images for second row */
  imagesRow2?: string[]
}

withDefaults(defineProps<Props>(), {
  title: '智能体赋能备课，<br>让教学更精彩',
  subtitle: '2025年 教育科技创新',
  description: 'AI驱动的智能教学工具',
  ctaText: '立即体验',
  logoText: 'AI互动式教学智能体',
  loginText: '登录',
  registerText: '注册',
  // 本地GIF动图
  imagesRow1: () => [
    '/src/assets/images/first-ppt-aionui.gif',
    '/src/assets/images/designwhatmovesyou.gif',
    '/src/assets/images/move.gif',
    '/src/assets/images/horizon.gif'
  ],
  imagesRow2: () => [
    '/src/assets/images/moridian.gif',
    '/src/assets/images/efforless.gif',
    '/src/assets/images/mars.gif',
    '/src/assets/images/saturn+sun.gif'
  ]
})

defineEmits<{
  (e: 'cta'): void
  (e: 'login'): void
  (e: 'register'): void
}>()
</script>

<style scoped>
.hero-container {
  min-height: 100vh;
  background-color: #050505;
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* Header */
.hero-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background-color: rgba(0, 0, 0, 0.88);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-header-inner {
  width: 100%;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hero-logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f8fafc;
  margin: 0;
}

.hero-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}

.hero-header-actions {
  gap: 0.5rem; /* 减少按钮间距 */
}

.hero-header-button {
  padding: 0.5rem 0.8rem; /* 宽度窄一点 */
  border-radius: 9999px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: transparent;
  color: #f8fafc;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hero-header-button:hover {
  background: rgba(255, 255, 255, 0.08);
}

.hero-header-button-primary {
  background: #ffffff;
  color: #0f172a;
  border-color: transparent;
}

.hero-header-button-primary:hover {
  background: #f3f4f6;
}

.hero-button-frame {
  display: inline-flex;
  padding: 0.125rem;
  border-radius: 14px;
  background-color: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.16);
}

.hero-button {
  border: none;
  cursor: pointer;
  border-radius: 1rem;
  padding: 0.95rem 1.4rem;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.hero-button-primary {
  background-color: #ffffff;
  color: #0f172a;
}

.hero-button-primary:hover {
  background-color: #f3f4f6;
}

.hero-button-ghost {
  background-color: transparent;
  color: #f8fafc;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.hero-button-ghost:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

/* Content */
.hero-content {
  flex: 1;
  display: flex;
  align-items: center;
  padding-top: 4rem;
}

.hero-grid {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 1.5rem;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: center;
}

@media (min-width: 1024px) {
  .hero-grid {
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    padding: 3rem;
  }
}

/* Text Section */
.hero-text {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.hero-title {
  font-size: 2.25rem;
  font-weight: 700;
  line-height: 1.2;
  margin: 0;
}

@media (min-width: 768px) {
  .hero-title {
    font-size: 3rem;
  }
}

@media (min-width: 1024px) {
  .hero-title {
    font-size: 3.75rem;
  }
}

.hero-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  color: rgba(255, 255, 255, 0.72);
}

.hero-subtitle,
.hero-description {
  font-size: 1.125rem;
  margin: 0;
}

/* Marquee Section */
.hero-marquee {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: calc(50vw + 2rem); /* 占据右侧一半空间 */
  display: flex;
  flex-direction: column;
  gap: 0.25rem; /* 再缩小一倍 */
  overflow: hidden;
  padding-right: 4rem; /* 右侧延伸空间 */
  z-index: 1;
}

.marquee-item {
  position: relative;
  width: 16rem;
  height: 16rem;
  border-radius: 1rem;
  overflow: hidden;
  flex-shrink: 0;
}

@media (min-width: 1024px) {
  .marquee-item {
    width: 20rem;
    height: 20rem;
  }
}

.marquee-image {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为contain，让整个GIF完全显示 */
  background-color: #050505; /* 添加背景色填充空白区域 */
  animation: gifFadeInOut 4.2s ease-in-out infinite;
  will-change: opacity;
}

/* GIF 轮播淡入淡出 */
@keyframes gifFadeInOut {
  0% { opacity: 0.62; }
  50% { opacity: 1; }
  100% { opacity: 0.62; }
}

/* 错峰淡入淡出，避免同频闪烁 */
.marquee-item:nth-child(2n) .marquee-image {
  animation-delay: 0.7s;
}

.marquee-item:nth-child(3n) .marquee-image {
  animation-delay: 1.4s;
}
</style>