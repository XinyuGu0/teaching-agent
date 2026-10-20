<template>
  <div class="progress-steps">
    <el-steps :active="stepIndex" finish-status="success" align-center>
      <el-step title="初始化" />
      <el-step title="对话中" />
      <el-step title="生成大纲" />
      <el-step title="生成PPT" />
      <el-step title="PPT已就绪" />
      <el-step title="已完成" />
    </el-steps>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  active: {
    type: Number,
    default: 0
  }
})

const stepIndex = computed(() => {
  return props.active
})
</script>

<style scoped>
.progress-steps {
  width: 100%;
  padding: 10px 0;
  background-color: #fff;
}

.progress-steps :deep(.el-steps) {
  width: 100%;
}

.progress-steps :deep(.el-step) {
  padding: 8px 12px;
}

.progress-steps :deep(.el-step__title) {
  font-size: 12px;
  color: #303133;
  font-weight: 500;
}

.progress-steps :deep(.el-step.is-process) :deep(.el-step__title) {
  color: #409EFF;
  font-weight: 600;
}

.progress-steps :deep(.el-step.is-finish) :deep(.el-step__title) {
  color: #67C23A;
}
</style>