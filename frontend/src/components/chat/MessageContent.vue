<template>
  <div class="message-content-wrapper message-bubble">
    <!-- 思考区域 -->
    <div v-if="mergedThinking" class="thinking-section">
      <!-- 思考中：流式展示，左竖线 + 浅色文字 -->
      <div v-if="isThinkingStreaming" class="thinking-streaming">
        <div class="thinking-streaming-body" ref="thinkingBodyRef">
          <div class="thinking-text">{{ mergedThinking }}</div>
        </div>
        <div class="thinking-streaming-footer">
          <span class="thinking-spinner"></span>
          <span class="thinking-label">思考中...</span>
        </div>
      </div>

      <!-- 思考完成：折叠行，可展开 -->
      <div v-else class="thinking-collapsed">
        <button class="thinking-toggle" @click="thinkingExpanded = !thinkingExpanded">
          <span class="thinking-toggle-icon" :class="{ expanded: thinkingExpanded }">›</span>
          <span class="thinking-toggle-label">已深度思考</span>
          <span class="thinking-toggle-hint">{{ thinkingExpanded ? '收起' : '展开' }}</span>
        </button>
        <div v-if="thinkingExpanded" class="thinking-expanded-body">
          <div class="thinking-text">{{ mergedThinking }}</div>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div v-if="mainContent" class="main-content markdown-body" v-html="renderedMain"></div>

    <!-- 联网搜索区域 - 放在底部 -->
    <div v-if="mergedSearchResults.length > 0" class="search-section">
      <!-- 搜索中：流式展示 -->
      <div v-if="isSearchStreaming" class="search-streaming">
        <div class="search-streaming-header">
          <div class="search-spinner"></div>
          <span class="search-label">正在联网搜索...</span>
          <span class="search-count">{{ mergedSearchResults.length }}</span>
        </div>
      </div>

      <!-- 搜索完成：来源摘要按钮 -->
      <div v-else class="search-sources">
        <button class="search-sources-toggle" @click="$emit('showSearchSources', mergedSearchResults)">
          <div class="search-sources-left">
            <Globe :size="14" class="search-sources-globe" />
            <span class="search-sources-label">已搜索 {{ mergedSearchResults.length }} 个网页</span>
          </div>
          <ExternalLink :size="13" class="search-sources-external-icon" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import { Globe, ExternalLink } from 'lucide-vue-next'
import 'highlight.js/styles/github.css'

const props = defineProps({
  content: { type: String, required: true },
  thinkingContent: { type: String, default: '' },
  searchResults: { type: Array, default: () => [] },
  isStreaming: { type: Boolean, default: false },
  isSearchCounting: { type: Boolean, default: false }
})

const emit = defineEmits(['showSearchSources'])

const thinkingExpanded = ref(false)
const thinkingBodyRef = ref(null)

marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try { return hljs.highlight(code, { language: lang }).value } catch (e) {}
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

// 兼容 prop 传入 或 content 中 <thinking> 标签
const parsedFromContent = computed(() => {
  const text = props.content
  const completePattern = /<thinking>([\s\S]*?)<\/thinking>/g
  const matches = [...text.matchAll(completePattern)]
  if (matches.length > 0) {
    return { thinking: matches.map(m => m[1]).join('\n\n'), main: text.replace(completePattern, '').trim(), isOpen: false }
  }
  const openIdx = text.indexOf('<thinking>')
  if (openIdx !== -1) {
    return { thinking: text.slice(openIdx + 10), main: text.slice(0, openIdx).trim(), isOpen: true }
  }
  return { thinking: '', main: text, isOpen: false }
})

const mergedThinking = computed(() => props.thinkingContent || parsedFromContent.value.thinking)
const mainContent = computed(() => parsedFromContent.value.main)

// 思考中：isStreaming 且还没有正文（正文出现说明思考已结束）
const isThinkingStreaming = computed(() =>
  props.isStreaming && !!mergedThinking.value && !mainContent.value
)

// 联网搜索
const mergedSearchResults = computed(() => props.searchResults || [])

// 搜索中：isSearchCounting 为 true（搜索计数阶段）
const isSearchStreaming = computed(() =>
  props.isSearchCounting
)

const renderedMain = computed(() => {
  if (!mainContent.value) return ''
  try { return marked.parse(mainContent.value) } catch { return mainContent.value }
})

// 思考流式时自动滚动到底部
watch(mergedThinking, () => {
  if (isThinkingStreaming.value) {
    nextTick(() => {
      if (thinkingBodyRef.value) {
        thinkingBodyRef.value.scrollTop = thinkingBodyRef.value.scrollHeight
      }
    })
  }
})
</script>

<style scoped>
.message-content-wrapper {
  width: 100%;
}

.message-bubble {
  background: transparent;
  padding: 0;
  border-radius: 0;
  box-shadow: none;
}

/* ── 联网搜索区域 ── */
.search-section {
  margin-top: 14px;
}

.search-streaming {
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
}

.search-streaming-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.search-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.15);
  border-top-color: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

.search-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.search-count {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin-left: 4px;
  font-variant-numeric: tabular-nums;
}

/* DeepSeek 风格来源摘要 */
.search-sources {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 10px;
}

.search-sources-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 0;
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
  transition: color 0.2s;
}

.search-sources-toggle:hover {
  color: rgba(255, 255, 255, 0.65);
}

.search-sources-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.search-sources-globe {
  flex-shrink: 0;
}

.search-sources-label {
  font-weight: 500;
}

.search-sources-external-icon {
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.25);
}

.search-links-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
}

.search-link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.15s;
  cursor: pointer;
}

.search-link-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.search-link-icon {
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.3);
}

.search-link-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.search-link-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.search-link-url {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── 思考流式区域 ── */
.thinking-streaming {
  margin-bottom: 12px;
  border-left: 3px solid #d0d0d0;
  padding-left: 12px;
}

.thinking-streaming-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.thinking-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #d0d0d0;
  border-top-color: #909399;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.thinking-label {
  font-size: 13px;
  color: #aaa;
  font-style: italic;
}

.thinking-streaming-body {
  max-height: 300px;
  overflow-y: auto;
}

.thinking-text {
  font-size: 13px;
  color: #b0b0b0;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

/* ── 思考完成折叠行 ── */
.thinking-collapsed {
  margin-bottom: 16px;
}

.thinking-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 0;
  color: #909399;
  font-size: 13px;
  transition: color 0.2s;
}

.thinking-toggle:hover {
  color: #606266;
}

.thinking-toggle-icon {
  font-size: 16px;
  line-height: 1;
  transition: transform 0.2s;
  display: inline-block;
}

.thinking-toggle-icon.expanded {
  transform: rotate(90deg);
}

.thinking-toggle-label {
  font-weight: 500;
}

.thinking-toggle-hint {
  font-size: 12px;
  color: #c0c4cc;
}

.thinking-expanded-body {
  margin-top: 8px;
  border-left: 3px solid #e4e7ed;
  padding-left: 12px;
  max-height: 400px;
  overflow-y: auto;
}

/* ── 主内容 ── */
.main-content {
  line-height: 1.8;
  color: inherit;
}

/* ── Markdown ── */
.markdown-body { font-size: 15px; color: inherit; }

.markdown-body h1, .markdown-body h2, .markdown-body h3,
.markdown-body h4, .markdown-body h5, .markdown-body h6 {
  margin-top: 24px; margin-bottom: 16px;
  font-weight: 600; line-height: 1.25;
}
.markdown-body h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
.markdown-body h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
.markdown-body h3 { font-size: 1.25em; }
.markdown-body p { margin-top: 0; margin-bottom: 16px; }
.markdown-body ul, .markdown-body ol { margin-top: 0; margin-bottom: 16px; padding-left: 2em; }
.markdown-body li { margin-bottom: 4px; }
.markdown-body code {
  padding: 0.2em 0.4em; font-size: 85%;
  background-color: rgba(27,31,35,0.05); border-radius: 3px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}
.markdown-body pre {
  padding: 16px; overflow: auto; font-size: 85%; line-height: 1.45;
  background-color: #f6f8fa; border-radius: 6px; margin-bottom: 16px;
}
.markdown-body pre code {
  display: inline; padding: 0; overflow: visible;
  line-height: inherit; background-color: transparent; border: 0;
}
.markdown-body blockquote {
  padding: 0 1em; color: #6a737d;
  border-left: 0.25em solid #dfe2e5; margin: 0 0 16px 0;
}
.markdown-body table { border-spacing: 0; border-collapse: collapse; margin-bottom: 16px; width: 100%; }
.markdown-body table th, .markdown-body table td { padding: 6px 13px; border: 1px solid #dfe2e5; }
.markdown-body table th { font-weight: 600; background-color: #f6f8fa; }
.markdown-body table tr { background-color: #fff; border-top: 1px solid #c6cbd1; }
.markdown-body table tr:nth-child(2n) { background-color: #f6f8fa; }
.markdown-body a { color: #0366d6; text-decoration: none; }
.markdown-body a:hover { text-decoration: underline; }
.markdown-body img { max-width: 100%; background-color: #fff; }
.markdown-body hr { height: 0.25em; padding: 0; margin: 24px 0; background-color: #e1e4e8; border: 0; }

/* 滚动条 */
.thinking-streaming-body::-webkit-scrollbar,
.thinking-expanded-body::-webkit-scrollbar { width: 4px; }
.thinking-streaming-body::-webkit-scrollbar-thumb,
.thinking-expanded-body::-webkit-scrollbar-thumb { background-color: #dcdfe6; border-radius: 2px; }
</style>
