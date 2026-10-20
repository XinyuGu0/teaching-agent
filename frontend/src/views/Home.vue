<template>
  <div class="home-page invert-on-light">
    <main class="overflow-hidden">
      <!-- Hero Section with Marquee -->
      <HeroWithMarquee
        title="智能体赋能备课，<br>让教学更精彩"
        subtitle="2025年 教育科技创新"
        description="AI驱动的智能教学工具"
        ctaText="立即体验"
        logoText="AI互动式教学智能体"
        loginText="登录"
        registerText="注册"
        @login="$router.push('/login')"
        @register="$router.push('/register')"
        @cta="$router.push('/register')"
      />

      <!-- Scroll Animation Section -->
      <ContainerScroll>
        <img
          src="/src/assets/images/image-2.png"
          alt="hero"
          class="w-full h-full object-cover rounded-2xl"
          style="pointer-events: none;"
        />
      </ContainerScroll>

      <!-- Bento Grid Section -->
      <div class="bento-section">
        <h2 class="section-title">核心功能</h2>
        <p class="section-subtitle">AI赋能教学，让课件制作更高效</p>
        <BentoGrid :items="bentoItems" />
      </div>

      <!-- Logo Cloud Section -->
      <div class="logo-cloud-section">
        <LogoCloud2 />
      </div>

      <!-- Testimonials Section -->
      <TestimonialsSection />

      <!-- Small Footer -->
      <footer class="home-footer">
        <div class="footer-inner">
          <span>© 2026 AI互动式教学智能体</span>
          <div class="footer-links">
            <a href="#" @click.prevent="$router.push('/login')">登录</a>
            <a href="#" @click.prevent="$router.push('/register')">注册</a>
          </div>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup>
import HeroWithMarquee from '@/components/ui/cta-with-marquee/HeroWithMarquee.vue'
import ContainerScroll from '@/components/ui/ContainerScroll.vue'
import TestimonialsSection from '@/components/ui/TestimonialsSection.vue'
import BentoGrid from '@/components/ui/BentoGrid.vue'
import LogoCloud2 from '@/components/ui/logo-cloud-2.vue'
import { Sparkles, FileText, Image, Users } from 'lucide-vue-next'

const bentoItems = [
  {
    title: "智能生成",
    meta: "AI驱动",
    description: "一键生成专业PPT，AI自动排版与内容优化",
    icon: Sparkles,
    iconClass: "text-blue-500",
    status: "运行中",
    tags: ["AI", "自动化", "效率"],
    colSpan: 2,
    hasPersistentHover: true,
  },
  {
    title: "模板中心",
    meta: "100+ 模板",
    description: "海量教学模板，覆盖各学科场景",
    icon: FileText,
    iconClass: "text-emerald-500",
    status: "已更新",
    tags: ["模板", "教学"],
  },
  {
    title: "素材库",
    meta: "持续更新",
    description: "丰富的图片、图标、动画素材，一键插入",
    icon: Image,
    iconClass: "text-purple-500",
    tags: ["素材", "资源"],
    colSpan: 2,
  },
  {
    title: "协作分享",
    meta: "多人协作",
    description: "支持团队协作编辑，一键分享课件",
    icon: Users,
    iconClass: "text-sky-500",
    status: "测试版",
    tags: ["协作", "分享"],
  },
]
</script>

<style scoped>
.home-page {
  min-height: 200vh; /* 增加高度以容纳滚动动画 */
  background-color: #050505;
  color: #f8fafc;
}

.bento-section {
  padding: 5rem 0;
  max-width: 1280px;
  margin: 0 auto;
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

.section-subtitle {
  font-size: 1.125rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.72);
  margin-bottom: 1.5rem;
}

.logo-cloud-section {
  padding: 0 1.5rem;
  max-width: 1280px;
  margin: 0 auto;
}

.home-footer {
  margin-top: 3rem;
  padding: 1rem 1.5rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.footer-inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.55);
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.footer-links a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-links a:hover {
  color: rgba(255, 255, 255, 0.95);
}

@media (max-width: 640px) {
  .footer-inner {
    flex-direction: column;
    justify-content: center;
  }
}
</style>
