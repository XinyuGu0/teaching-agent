<template>
  <div :class="['testimonials-column', className]">
    <div class="animate-scroll">
      <div
        v-for="(item, index) in [...testimonials, ...testimonials]"
        :key="index"
        class="testimonial-card"
      >
        <div class="testimonial-text">{{ item.text }}</div>
        <div class="testimonial-author">
          <img
            :src="item.image"
            :alt="item.name"
            class="author-avatar"
          />
          <div class="author-info">
            <div class="author-name">{{ item.name }}</div>
            <div class="author-role">{{ item.role }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface TestimonialItem {
  text: string
  image: string
  name: string
  role: string
}

defineProps<{
  className?: string
  testimonials: TestimonialItem[]
  duration?: number
}>()
</script>

<style scoped>
.testimonials-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.animate-scroll {
  animation: scroll-up v-bind('duration ? `${duration}s` : `10s`') linear infinite;
}

@keyframes scroll-up {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-50%);
  }
}

.testimonial-card {
  padding: 2.5rem;
  margin: 0.5rem;
  border-radius: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  box-shadow: 
    0 10px 25px -5px rgba(0, 0, 0, 0.3),
    0 8px 10px -6px rgba(0, 0, 0, 0.2),
    0 0 20px rgba(255, 255, 255, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  max-width: 20rem;
  width: 100%;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.testimonial-card:hover {
  border-color: rgba(255, 255, 255, 0.25);
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.4),
    0 10px 20px -5px rgba(0, 0, 0, 0.3),
    0 0 30px rgba(255, 255, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.testimonial-text {
  font-size: 0.875rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1.25rem;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.author-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  object-fit: cover;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 500;
  font-size: 0.875rem;
  line-height: 1.25;
  letter-spacing: -0.025em;
}

.author-role {
  font-size: 0.875rem;
  line-height: 1.25;
  opacity: 0.6;
  letter-spacing: -0.025em;
}
</style>
