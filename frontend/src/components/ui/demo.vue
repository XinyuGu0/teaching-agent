<template>
  <div class="demo-container">
    <AnimatedAIChat />
    <LogoCloud2 />
  </div>
</template>

<script setup lang="ts">
import AnimatedAIChat from './AnimatedAIChat.vue'
import LogoCloud2 from './logo-cloud-2.vue'
</script>

<style scoped>
.demo-container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
