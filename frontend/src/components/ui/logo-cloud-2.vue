<template>
  <div class="logo-cloud-section">
    <div class="logo-cloud-container">
      <!-- Section Header -->
      <div class="section-header">
        <h2 class="section-title">{{ title }}</h2>
        <p class="section-description">{{ description }}</p>
      </div>

      <!-- Row 1: Tech Stack -->
      <div class="logo-row">
        <div class="row-header">
          <h2 class="row-title">{{ techTitle }}</h2>
        </div>
        <div class="logo-grid">
          <div
            v-for="(logo, index) in techLogos"
            :key="'tech-' + index"
            class="logo-card"
          >
            <img
              :src="logo.src"
              :alt="logo.alt"
              :style="{ width: logo.width || 'auto', height: logo.height || '36px' }"
              class="logo-img"
            />
          </div>
        </div>
      </div>

      <!-- Row 2: AI & Cloud -->
      <div class="logo-row ai-row">
        <div class="row-header">
          <h2 class="row-title">{{ aiTitle }}</h2>
        </div>
        <div class="logo-grid">
          <div
            v-for="(logo, index) in aiLogos"
            :key="'ai-' + index"
            class="logo-card ai-logo-card"
          >
            <img
              :src="logo.src"
              :alt="logo.alt"
              :style="{ width: logo.width || 'auto', height: logo.height || '36px' }"
              :class="['logo-img', { 'ai-logo-img': !logo.noInvert }]"
            />
            <span v-if="logo.label" class="logo-label ai-logo-label">{{ logo.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import gitSvg from '@/assets/images/logo-intro-tech/git.svg'
import pythonSvg from '@/assets/images/logo-intro-tech/python.svg'
import vuejsSvg from '@/assets/images/logo-intro-tech/vuejs.svg'
import mcpSvg from '@/assets/images/logo-intro-tech/mcp.svg'
import huaweiTextSvg from '@/assets/images/logo-intro-tech/huawei-text.svg'
import mcpTextSvg from '@/assets/images/logo-intro-tech/mcp.svg'
import qwenTextSvg from '@/assets/images/logo-intro-tech/qwen-text.svg'
import zhipuTextSvg from '@/assets/images/logo-intro-tech/zhipu-text.svg'
import officecliPng from '@/assets/images/logo-intro-tech/OfficeCLI.png'

interface LogoItem {
  src: string
  alt: string
  width?: number | string
  height?: number | string
  label?: string
  noInvert?: boolean
}

withDefaults(defineProps<{
  title?: string
  description?: string
  techTitle?: string
  techDescription?: string
  aiTitle?: string
  aiDescription?: string
  techLogos?: LogoItem[]
  aiLogos?: LogoItem[]
}>(), {
  title: '技术架构与智能引擎',
  description: '基于现代化工程体系构建，深度整合行业领先的大模型能力与云基础设施，为智能教学提供坚实的技术保障。',
  techTitle: '技术栈与开发工具',
  techDescription: '采用主流前端框架与后端技术，保障系统的高性能与可扩展性。',
  aiTitle: 'AI引擎与云服务',
  aiDescription: '接入多家头部大模型与云服务平台，打造灵活、强大的智能底座。',
  techLogos: () => [
    { src: vuejsSvg, alt: 'Vue.js', height: '48px' },
    { src: pythonSvg, alt: 'Python', height: '48px' },
    { src: gitSvg, alt: 'Git', height: '48px' },
    
  ],
  aiLogos: () => [
    { src: qwenTextSvg, alt: '通义千问', height: '44px' },
    { src: zhipuTextSvg, alt: '智谱AI', height: '44px' },
    { src: mcpSvg, alt: 'MCP', height: '48px' },
    { src: officecliPng, alt: 'OfficeCLI', height: '44px', label: 'OfficeCLI', noInvert: true },
    { src: huaweiTextSvg, alt: '华为云', height: '44px' },
    
  ],
})
</script>

<style scoped>
.logo-cloud-section {
  width: 100%;
  padding: 5rem 0;
}

.logo-cloud-container {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 0 1.5rem;
}

/* Section Header */
.section-header {
  text-align: center;
}

.section-title {
  font-size: 2.25rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 1rem;
}

@media (min-width: 768px) {
  .section-title {
    font-size: 3rem;
  }
}

@media (min-width: 1024px) {
  .section-title {
    font-size: 3.75rem;
  }
}

.section-description {
  font-size: 1.125rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.72);
  margin-bottom: 3rem;
}

/* Logo Row */
.logo-row {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.row-header {
  text-align: center;
}

.row-title {
  font-size: 2.25rem;
  font-weight: 700;
  background: linear-gradient(to right, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.6));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
}

/* Logo Grid */
.logo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.ai-row .logo-grid {
  grid-template-columns: repeat(5, 1fr);
}

.logo-card {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 1.5rem;
  transition: all 0.25s ease;
  min-height: 100px;
}

.logo-card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.logo-img {
  object-fit: contain;
  filter: brightness(0.9);
  transition: filter 0.25s ease;
}

.logo-card:hover .logo-img {
  filter: brightness(1.1);
}

/* AI Row - Inverted logos (dark bg, white text) */
.ai-logo-card {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.1);
}

.ai-logo-card:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.18);
}

.ai-logo-img {
  filter: brightness(0) invert(1);
  opacity: 0.85;
}

.ai-logo-card:hover .ai-logo-img {
  filter: brightness(0) invert(1);
  opacity: 1;
}

/* Logo Label */
.logo-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  margin-left: 6px;
  white-space: nowrap;
}

.ai-logo-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.35rem;
  font-weight: 600;  text-shadow: 0 0 12px rgba(255, 255, 255, 0.15);}

/* Responsive */
@media (max-width: 768px) {
  .logo-cloud-container {
    gap: 2rem;
    padding: 0 1rem;
  }

  .section-title {
    font-size: 1.25rem;
  }

  .logo-grid {
    grid-template-columns: 1fr;
  }

  .ai-row .logo-grid {
    grid-template-columns: 1fr;
  }

  .logo-card {
    padding: 1.25rem;
    min-height: auto;
  }

  .logo-img {
    height: 36px !important;
  }
}
</style>
