<template>
  <div
    :class="containerClass"
    :style="containerStyle"
  >
    <div :class="contentClass">
      <slot></slot>
    </div>
    <div :class="contentClass" aria-hidden="true">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'

/**
 * MarqueeRow Component
 * 
 * A horizontal scrolling marquee component that displays content in an infinite loop.
 * Used for showcasing images, logos, or any content that benefits from continuous scrolling.
 * 
 * @example
 * <MarqueeRow :speed="30" :reverse="true" :gap="16">
 *   <img v-for="src in images" :src="src" />
 * </MarqueeRow>
 */

interface Props {
  /** Animation speed in seconds (lower = faster) */
  speed?: number
  /** Reverse animation direction */
  reverse?: boolean
  /** Pause animation on hover */
  pauseOnHover?: boolean
  /** Gap between items in pixels */
  gap?: number
  /** Additional CSS classes */
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  speed: 40,
  reverse: false,
  pauseOnHover: false,
  gap: 16,
  class: ''
})

const containerStyle = computed(() => ({
  '--duration': `${props.speed}s`,
  '--gap': `${props.gap}px`
}))

const containerClass = computed(() =>
  cn(
    'group flex overflow-hidden [gap:var(--gap)]',
    props.class
  )
)

const contentClass = computed(() =>
  cn(
    'flex min-w-full shrink-0 items-center justify-around gap-[var(--gap)] animate-marquee',
    props.reverse && '[animation-direction:reverse]',
    props.pauseOnHover && 'group-hover:[animation-play-state:paused]'
  )
)
</script>