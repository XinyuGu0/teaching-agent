<template>
  <div
    :class="cn(
      'group flex overflow-hidden [--gap:1rem] [gap:var(--gap)]',
      props.class
    )"
    :style="{ '--duration': `${props.speed}s` }"
  >
    <div
      :class="cn(
        'flex min-w-full shrink-0 items-center justify-around gap-[var(--gap)] animate-marquee',
        props.reverse && '[animation-direction:reverse]',
        props.pauseOnHover && 'group-hover:[animation-play-state:paused]'
      )"
    >
      <slot></slot>
    </div>
    <div
      :class="cn(
        'flex min-w-full shrink-0 items-center justify-around gap-[var(--gap)] animate-marquee',
        props.reverse && '[animation-direction:reverse]',
        props.pauseOnHover && 'group-hover:[animation-play-state:paused]'
      )"
      aria-hidden="true"
    >
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  pauseOnHover: {
    type: Boolean,
    default: false
  },
  reverse: {
    type: Boolean,
    default: false
  },
  speed: {
    type: Number,
    default: 40
  },
  class: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
</style>