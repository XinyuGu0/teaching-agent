<template>
  <div class="ppt-onlyoffice-view invert-on-light">
    <div class="preview-bg-glow preview-bg-glow-1"></div>
    <div class="preview-bg-glow preview-bg-glow-2"></div>

    <div class="header">
      <div class="header-left">
        <h1>{{ pptTitle || 'PPT' }}</h1>
      </div>
      <div class="header-actions">
        <button class="header-btn header-btn-primary" @click="downloadPpt" :disabled="downloading || !downloadUrl">
          {{ downloading ? '下载中...' : '下载PPT' }}
        </button>
        <button class="header-btn" @click="goBack">返回</button>
      </div>
    </div>

    <div v-if="loading" class="loading-container" v-loading="loading" element-loading-text="加载中..."></div>
    <div v-else-if="error" class="error-container">
      <div class="error-card">
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button class="header-btn header-btn-primary" @click="goBack">返回</button>
      </div>
    </div>
    <div v-else class="editor-container">
      <div class="editor-frame">
        <div id="onlyoffice-editor"></div>
      </div>
    </div>

    <!-- 右侧 AI 修改面板 -->
    <aside :class="['ai-panel', { 'is-open': showAiPanel }]">
      <div class="ai-panel-header">
        <div class="ai-panel-title-row">
          <Sparkles :size="15" class="ai-panel-icon" />
          <span class="ai-panel-title">AI 修改助手</span>
        </div>
        <button class="ai-panel-close" @click="showAiPanel = false">
          <X :size="16" />
        </button>
      </div>

      <div class="ai-panel-messages" ref="aiMessagesRef">
        <!-- 欢迎消息 -->
        <div v-if="aiMessages.length === 0 && !isModifying" class="ai-welcome">
          <Sparkles :size="28" class="ai-welcome-icon" />
          <p class="ai-welcome-text">描述你想要修改的内容，例如：</p>
          <div class="ai-welcome-examples">
            <button class="ai-example-chip" @click="modifyMessage = '把第3页改成深色主题'">把第3页改成深色主题</button>
            <button class="ai-example-chip" @click="modifyMessage = '在封面增加企业LOGO'">在封面增加企业LOGO</button>
            <button class="ai-example-chip" @click="modifyMessage = '调整正文页字号为18px'">调整正文页字号为18px</button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(msg, idx) in aiMessages"
          :key="idx"
          :class="['ai-msg', `ai-msg-${msg.role}`]"
        >
          <div class="ai-msg-bubble">
            <div v-if="msg.role === 'user'" class="ai-msg-text">{{ msg.content }}</div>
            <div v-else class="ai-msg-text">
              <span v-if="msg.content">{{ msg.content }}</span>
              <!-- 进度条 -->
              <div v-if="msg.showProgress" class="ai-progress-wrap">
                <div class="ai-progress-bar">
                  <div class="ai-progress-indicator" :style="{ transform: `translateX(-${100 - msg.progress}%)` }"></div>
                </div>
                <div class="ai-progress-headline">
                  <span class="ai-progress-percent">{{ Math.round(msg.progress) }}%</span>
                  <span class="ai-progress-text">{{ msg.progressText }}</span>
                </div>
                <!-- 任务条 -->
                <div class="ai-plan-card">
                  <div class="ai-plan-title">修改任务</div>
                  <ul class="ai-plan-list">
                    <li
                      v-for="task in msg.tasks"
                      :key="task.id"
                      :class="['ai-plan-item', `status-${task.status}`]"
                    >
                      <span class="ai-plan-icon">
                        <CheckCircle2 v-if="task.status === 'completed'" :size="14" />
                        <CircleDotDashed v-else-if="task.status === 'in-progress'" :size="14" class="spin" />
                        <Circle v-else :size="14" />
                      </span>
                      <div class="ai-plan-content">
                        <div class="ai-plan-item-title">{{ task.title }}</div>
                      </div>
                      <span class="ai-plan-badge">{{ task.statusLabel }}</span>
                    </li>
                  </ul>
                </div>
                <!-- 日志 -->
                <div v-if="msg.logs.length > 0" class="ai-log-box">
                  <div class="ai-plan-title">过程日志</div>
                  <div class="ai-log-list">
                    <div v-for="(log, logIdx) in msg.logs" :key="logIdx" class="ai-log-item">
                      <span class="ai-log-progress">{{ log.progress }}%</span>
                      <span class="ai-log-message">{{ log.message }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="ai-panel-footer">
        <div class="ai-input-box">
          <textarea
            v-model="modifyMessage"
            class="ai-textarea"
            placeholder="描述修改需求..."
            rows="1"
            @keydown.enter.exact.prevent="sendModifyMessage"
            :disabled="isModifying"
          ></textarea>
          <button
            :class="['ai-send-btn', { active: modifyMessage.trim() }]"
            @click="sendModifyMessage"
            :disabled="!modifyMessage.trim() || isModifying"
          >
            <Loader2 v-if="isModifying" :size="15" class="spin" />
            <Send v-else :size="15" />
          </button>
        </div>
      </div>
    </aside>

    <!-- 打开 AI 面板的浮动按钮 -->
    <button
      v-if="!showAiPanel && !loading && !error"
      class="ai-fab"
      @click="showAiPanel = true"
      title="AI 修改助手"
    >
      <Sparkles :size="18" />
    </button>
  </div>
</template>
<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Sparkles, X, Send, Loader2, CheckCircle2, CircleDotDashed, Circle } from 'lucide-vue-next'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref(null)
const editorConfig = ref(null)
const pptTitle = ref('')
const downloadUrl = ref('')
const downloading = ref(false)
const modifyMessage = ref('')
const showAiPanel = ref(false)
const isModifying = ref(false)
const aiMessages = ref([])
const aiMessagesRef = ref(null)
let docEditor = null

onMounted(async () => {
  await loadEditorConfig()
})

onUnmounted(() => {
  // 销毁编辑器实例
  if (docEditor) {
    docEditor.destroyEditor()
    docEditor = null
  }
})

const loadEditorConfig = async () => {
  try {
    loading.value = true
    error.value = null

    const pptId = route.params.id
    const response = await api.get(`/ppts/${pptId}/wopi`)
    editorConfig.value = response.data
    pptTitle.value = response.data.file_name

    // 设置下载URL
    const baseUrl = response.data.file_url.replace(/\/api\/ppts\/.+$/, '')
    downloadUrl.value = `${baseUrl}/api/ppts/${pptId}/download`

    // 等待DOM更新后初始化编辑器
    await nextTick()
    initOnlyOfficeEditor()
  } catch (err) {
    console.error('Failed to load editor config:', err)
    error.value = err.response?.data?.message || '加载失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const initOnlyOfficeEditor = () => {
  if (!editorConfig.value) return
  
  const onlyofficeUrl = editorConfig.value.onlyoffice_url || 'http://localhost:80'
  
  // 动态加载OnlyOffice的API脚本
  const script = document.createElement('script')
  script.src = `${onlyofficeUrl}/web-apps/apps/api/documents/api.js`
  script.onload = () => {
    initEditor(onlyofficeUrl)
  }
  script.onerror = () => {
    error.value = '无法加载OnlyOffice编辑器，请确保OnlyOffice服务正在运行'
    ElMessage.error(error.value)
  }
  document.head.appendChild(script)
}

const initEditor = (onlyofficeUrl) => {
  const cfg = editorConfig.value
  
  // 使用后端返回的完整config（必须与JWT payload完全一致）
  // document 和 editorConfig 直接使用后端返回的，保证与JWT签名一致
  const document = cfg.document || {
    fileType: 'pptx',
    key: cfg.key,
    title: cfg.file_name,
    url: cfg.file_url,
    permissions: {
      edit: true,
      download: true,
      print: true
    }
  }
  
  const editorCfg = cfg.editor_config || {
    callbackUrl: cfg.callback_url || '',
    lang: 'zh-CN',
    mode: 'edit',
    user: {
      id: 'user',
      name: 'User'
    }
  }
  
  const config = {
    type: 'desktop',
    documentType: 'presentation',
    document: document,
    editorConfig: editorCfg,
    width: '100%',
    height: '100%',
    containerId: 'onlyoffice-editor'
  }

  // JWT token：ONLYOFFICE要求token中的payload与config完全一致
  // 后端已生成包含 document + documentType + editorConfig 的JWT
  if (cfg.token) {
    config.token = cfg.token
  }

  console.log('[OnlyOffice] 初始化editor config:', {
    key: document.key,
    url: document.url,
    hasToken: !!cfg.token,
    callbackUrl: editorCfg.callbackUrl
  })

  // 检查DocsAPI是否可用
  if (window.DocsAPI) {
    docEditor = new window.DocsAPI.DocEditor('onlyoffice-editor', config)
  } else {
    error.value = 'OnlyOffice API未正确加载'
    ElMessage.error(error.value)
  }
}

const downloadPpt = async () => {
  if (!downloadUrl.value) return
  try {
    downloading.value = true
    const token = localStorage.getItem('access_token')
    if (!token) {
      ElMessage.error('请先登录')
      return
    }

    const response = await fetch(downloadUrl.value, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('下载失败')
    }

    const blob = await response.blob()
    const fileName = pptTitle.value || 'ppt.pptx'

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName.endsWith('.pptx') ? fileName : `${fileName}.pptx`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Download failed:', err)
    ElMessage.error(err.message || '下载失败')
  } finally {
    downloading.value = false
  }
}

const goBack = () => {
  router.back()
}

const sendModifyMessage = async () => {
  const content = modifyMessage.value.trim()
  if (!content || isModifying.value) return

  modifyMessage.value = ''

  // 添加用户消息
  aiMessages.value.push({ role: 'user', content })

  // 添加 AI 回复消息（带进度）
  const aiMsg = {
    role: 'assistant',
    content: '',
    showProgress: true,
    progress: 0,
    progressText: '准备中...',
    tasks: [
      { id: 1, title: '解析修改需求', status: 'in-progress', statusLabel: '进行中' },
      { id: 2, title: '定位目标页面', status: 'pending', statusLabel: '等待中' },
      { id: 3, title: '应用样式修改', status: 'pending', statusLabel: '等待中' },
      { id: 4, title: '生成新版本', status: 'pending', statusLabel: '等待中' },
      { id: 5, title: '校验并完成', status: 'pending', statusLabel: '等待中' }
    ],
    logs: []
  }
  aiMessages.value.push(aiMsg)
  isModifying.value = true

  await nextTick()
  scrollAiToBottom()

  // 模拟修改进度（约15秒）
  const steps = [
    { progress: 8, text: '解析修改需求...', taskIdx: 0, taskStatus: 'completed', log: '正在分析用户修改指令' },
    { progress: 18, text: '解析修改需求...', log: '需求解析完成，提取关键参数' },
    { progress: 25, text: '定位目标页面...', taskIdx: 1, taskStatus: 'in-progress', log: '正在定位目标幻灯片' },
    { progress: 35, text: '定位目标页面...', log: '已找到目标页面，读取当前布局' },
    { progress: 42, text: '定位目标页面...', taskIdx: 1, taskStatus: 'completed', log: '页面定位完成' },
    { progress: 50, text: '应用样式修改...', taskIdx: 2, taskStatus: 'in-progress', log: '正在修改文本样式' },
    { progress: 60, text: '应用样式修改...', log: '正在调整配色方案' },
    { progress: 70, text: '应用样式修改...', log: '正在更新布局元素' },
    { progress: 78, text: '应用样式修改...', taskIdx: 2, taskStatus: 'completed', log: '样式修改完成' },
    { progress: 85, text: '生成新版本...', taskIdx: 3, taskStatus: 'in-progress', log: '正在渲染新版本PPT' },
    { progress: 92, text: '生成新版本...', taskIdx: 3, taskStatus: 'completed', log: '新版本生成完成' },
    { progress: 96, text: '校验并完成...', taskIdx: 4, taskStatus: 'in-progress', log: '正在校验修改结果' },
    { progress: 100, text: '修改完成', taskIdx: 4, taskStatus: 'completed', log: '校验通过，修改已应用' }
  ]

  for (const step of steps) {
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 300))
    aiMsg.progress = step.progress
    aiMsg.progressText = step.text

    if (step.log) {
      aiMsg.logs.push({ progress: step.progress, message: step.log })
    }

    if (step.taskIdx !== undefined) {
      aiMsg.tasks[step.taskIdx].status = step.taskStatus
      aiMsg.tasks[step.taskIdx].statusLabel = step.taskStatus === 'completed' ? '已完成' : step.taskStatus === 'in-progress' ? '进行中' : '等待中'
    }

    scrollAiToBottom()
  }

  // 完成
  aiMsg.showProgress = false
  aiMsg.content = '修改已完成！PPT 已更新为新版本。'
  isModifying.value = false
  ElMessage.success('PPT 修改完成')
  scrollAiToBottom()
}

const scrollAiToBottom = () => {
  nextTick(() => {
    if (aiMessagesRef.value) {
      aiMessagesRef.value.scrollTop = aiMessagesRef.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.ppt-onlyoffice-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0a0a0b;
  color: white;
  position: relative;
  overflow: hidden;
}

.preview-bg-glow {
  position: absolute;
  border-radius: 9999px;
  filter: blur(120px);
  pointer-events: none;
  z-index: 0;
}

.preview-bg-glow-1 {
  width: 320px;
  height: 320px;
  left: 5%;
  top: -120px;
  background: rgba(139, 92, 246, 0.15);
}

.preview-bg-glow-2 {
  width: 280px;
  height: 280px;
  right: 8%;
  bottom: -100px;
  background: rgba(99, 102, 241, 0.12);
}

.header {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.header h1 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.92);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-btn {
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.82);
  font-size: 12px;
  font-weight: 500;
  padding: 7px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.header-btn:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.1);
}

.header-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.header-btn-primary {
  border-color: rgba(139, 92, 246, 0.45);
  background: rgba(139, 92, 246, 0.18);
  color: #efe7ff;
}

.loading-container,
.error-container {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-card {
  width: min(480px, 90vw);
  padding: 24px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  text-align: center;
}

.error-card h3 {
  margin: 0 0 8px;
  color: rgba(255, 255, 255, 0.9);
}

.error-card p {
  margin: 0 0 14px;
  color: rgba(255, 255, 255, 0.6);
}

.editor-container {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  min-height: 0;
  padding: 14px;
  transition: padding-right 0.3s ease;
}

.ppt-onlyoffice-view:has(.ai-panel.is-open) .editor-container {
  padding-right: calc(14px + 380px);
}

.editor-frame {
  width: 100%;
  height: 100%;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

#onlyoffice-editor {
  width: 100%;
  height: 100%;
  flex: 1;
}

/* ===== AI Panel ===== */
.ai-panel {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 380px;
  z-index: 10;
  background: #111113;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.ai-panel.is-open {
  transform: translateX(0);
}

.ai-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.ai-panel-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-panel-icon {
  color: rgba(255, 255, 255, 0.6);
}

.ai-panel-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.ai-panel-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  transition: all 0.15s;
}

.ai-panel-close:hover {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.8);
}

/* Messages */
.ai-panel-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 32px 16px;
  text-align: center;
}

.ai-welcome-icon {
  color: rgba(255, 255, 255, 0.2);
}

.ai-welcome-text {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  line-height: 1.5;
}

.ai-welcome-examples {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
  margin-top: 4px;
}

.ai-example-chip {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.55);
  font-size: 12px;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s;
}

.ai-example-chip:hover {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.8);
  border-color: rgba(255, 255, 255, 0.15);
}

/* Message bubbles */
.ai-msg {
  display: flex;
}

.ai-msg-user {
  justify-content: flex-end;
}

.ai-msg-assistant {
  justify-content: flex-start;
}

.ai-msg-bubble {
  max-width: 92%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.6;
}

.ai-msg-user .ai-msg-bubble {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.9);
  border-bottom-right-radius: 4px;
}

.ai-msg-assistant .ai-msg-bubble {
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-bottom-left-radius: 4px;
}

.ai-msg-text {
  word-break: break-word;
}

/* Progress */
.ai-progress-wrap {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-progress-bar {
  height: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.ai-progress-indicator {
  height: 100%;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  transition: transform 0.5s ease;
}

.ai-progress-headline {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-progress-percent {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
}

.ai-progress-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.45);
}

/* Plan card */
.ai-plan-card {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
}

.ai-plan-title {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 8px;
}

.ai-plan-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ai-plan-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.ai-plan-item.status-completed {
  color: rgba(255, 255, 255, 0.7);
}

.ai-plan-item.status-in-progress {
  color: rgba(255, 255, 255, 0.8);
}

.ai-plan-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.ai-plan-content {
  flex: 1;
  min-width: 0;
}

.ai-plan-item-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ai-plan-badge {
  font-size: 11px;
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.35);
}

/* Log box */
.ai-log-box {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
}

.ai-log-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 120px;
  overflow-y: auto;
}

.ai-log-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
}

.ai-log-progress {
  color: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
  min-width: 28px;
}

.ai-log-message {
  color: rgba(255, 255, 255, 0.45);
}

/* Footer input */
.ai-panel-footer {
  padding: 12px 14px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.ai-input-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #141416;
  border: 1px solid #2a2a2e;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.ai-input-box:focus-within {
  border-color: rgba(255, 255, 255, 0.18);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.04);
}

.ai-textarea {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: rgba(255, 255, 255, 0.92);
  font-size: 13px;
  line-height: 1.5;
  resize: none;
  min-height: 20px;
  max-height: 80px;
  padding: 3px 0;
  font-family: inherit;
}

.ai-textarea::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.ai-send-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.ai-send-btn.active {
  background: #ffffff;
  color: #0a0a0a;
  border-color: #ffffff;
}

.ai-send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* FAB */
.ai-fab {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 5;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(20, 20, 24, 0.85);
  backdrop-filter: blur(16px);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
}

.ai-fab:hover {
  background: rgba(30, 30, 36, 0.95);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

/* Spin */
.spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
