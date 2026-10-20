<template>
  <div class="mindmap-container">
    <div class="mindmap-header">
      <h3>思维导图</h3>
      <el-button size="small" @click="downloadSVG">
        <el-icon><Download /></el-icon>
        下载
      </el-button>
    </div>
    <div ref="mindmapRef" class="mindmap-content"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import mermaid from 'mermaid'
import svgPanZoom from 'svg-pan-zoom'
import { Download } from '@element-plus/icons-vue'

const props = defineProps({
  markdown: {
    type: String,
    required: true
  }
})

const mindmapRef = ref(null)
let panZoomInstance = null

const normalizeMarkdownToMindmap = (content) => {
  const lines = content
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0)

  if (lines.length === 0) return ''

  if (lines[0].startsWith('mindmap')) {
    return lines.join('\n')
  }

  const rootLine = lines[0].replace(/^#+\s*/, '')
  const bodyLines = lines.slice(1)

  const normalized = ['mindmap', rootLine]

  bodyLines.forEach((line) => {
    const headingMatch = line.match(/^(#+)\s*(.+)$/)
    if (headingMatch) {
      const depth = Math.min(headingMatch[1].length, 6)
      const text = headingMatch[2].trim()
      normalized.push(`${'  '.repeat(depth)}${text}`)
      return
    }

    const listMatch = line.match(/^(\*|-|\d+\.)\s+(.+)$/)
    if (listMatch) {
      normalized.push(`  ${listMatch[2].trim()}`)
      return
    }

    normalized.push(`  ${line}`)
  })

  return normalized.join('\n')
}

const renderMindmap = async () => {
  if (!mindmapRef.value || !props.markdown) return

  await nextTick()

  try {
    const id = `mindmap-${Math.random().toString(36).slice(2)}`
    const mermaidText = normalizeMarkdownToMindmap(props.markdown)

    if (!mermaidText) return

    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'loose',
      theme: 'default',
      mindmap: {
        useMaxWidth: true
      }
    })

    const { svg } = await mermaid.render(id, mermaidText)

    mindmapRef.value.innerHTML = svg

    const svgEl = mindmapRef.value.querySelector('svg')
    if (!svgEl) return

    svgEl.removeAttribute('height')
    svgEl.removeAttribute('width')
    svgEl.setAttribute('preserveAspectRatio', 'xMidYMid meet')

    if (panZoomInstance) {
      panZoomInstance.destroy()
    }

    panZoomInstance = svgPanZoom(svgEl, {
      zoomEnabled: true,
      controlIconsEnabled: true,
      fit: true,
      center: true,
      minZoom: 0.2,
      maxZoom: 6,
      dblClickZoomEnabled: false
    })
  } catch (error) {
    console.error('Failed to render mindmap:', error)
    if (mindmapRef.value) {
      mindmapRef.value.innerHTML = '<div class="mindmap-error">思维导图渲染失败</div>'
    }
  }
}

const downloadSVG = () => {
  if (!mindmapRef.value) return

  const svg = mindmapRef.value.querySelector('svg')
  if (!svg) return

  const serializer = new XMLSerializer()
  const svgString = serializer.serializeToString(svg)
  const blob = new Blob([svgString], { type: 'image/svg+xml' })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.href = url
  link.download = 'mindmap.svg'
  link.click()

  URL.revokeObjectURL(url)
}

watch(() => props.markdown, () => {
  renderMindmap()
}, { immediate: true })

onMounted(() => {
  renderMindmap()
})
</script>

<style scoped>
.mindmap-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.mindmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.mindmap-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.mindmap-content {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 400px;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
}

.mindmap-content :deep(svg) {
  width: 100%;
  height: 100%;
}

.mindmap-error {
  padding: 24px;
  color: #f56c6c;
  font-size: 14px;
}
</style>


