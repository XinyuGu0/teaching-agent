<template>
  <div class="shared-view">
    <div class="shared-background">
      <div class="shared-glow glow-1"></div>
      <div class="shared-glow glow-2"></div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="shared-loading">
      <Loader2 :size="32" class="spin" />
      <p>正在加载分享的对话...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="shared-error">
      <div class="error-icon">
        <XCircle :size="48" />
      </div>
      <h2>无法访问</h2>
      <p>{{ error }}</p>
      <button class="error-btn" @click="$router.push('/')">返回首页</button>
    </div>

    <!-- Password Required -->
    <div v-else-if="needsPassword && !conversationData" class="shared-password">
      <div class="password-card">
        <div class="password-card-header">
          <Lock :size="24" style="color: #60a5fa;" />
          <h2>{{ shareInfo?.title || '受保护的对话' }}</h2>
          <p>此对话需要密码才能访问</p>
        </div>
        <div class="password-card-body">
          <div class="password-input-row">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入访问密码"
              class="password-input"
              @keydown.enter="verifyPassword"
            />
            <button class="password-toggle" @click="showPassword = !showPassword">
              <Eye v-if="!showPassword" :size="16" />
              <EyeOff v-else :size="16" />
            </button>
          </div>
          <button class="password-submit" @click="verifyPassword" :disabled="!password">
            验证并查看
          </button>
          <p v-if="passwordError" class="password-error">{{ passwordError }}</p>
        </div>
        <div class="password-card-footer">
          <span>分享者：{{ shareInfo?.owner?.nickname || '未知用户' }}</span>
        </div>
      </div>
    </div>

    <!-- Conversation Content -->
    <div v-else-if="conversationData" class="shared-conversation">
      <header class="shared-header">
        <div class="shared-header-left">
          <div class="shared-avatar" v-if="ownerInfo">
            <img v-if="ownerInfo.avatar_url" :src="getAvatarUrl(ownerInfo.avatar_url)" alt="" />
            <span v-else class="avatar-fallback">{{ (ownerInfo.nickname || '?')[0] }}</span>
          </div>
          <div class="shared-meta">
            <h1>{{ conversationData.title }}</h1>
            <span class="shared-owner">由 {{ ownerInfo?.nickname || '未知用户' }} 分享</span>
          </div>
        </div>
        <button class="shared-close-btn" @click="$router.push('/')">
          <X :size="16" />
          <span>关闭</span>
        </button>
      </header>

      <div class="shared-messages">
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="['shared-msg', msg.role === 'user' ? 'msg-user' : 'msg-assistant']"
        >
          <div class="msg-avatar">
            <span v-if="msg.role === 'user'" class="avatar-fallback small">U</span>
            <span v-else class="avatar-fallback small ai">AI</span>
          </div>
          <div class="msg-content">
            <div class="msg-role">{{ msg.role === 'user' ? '用户' : 'AI助手' }}</div>
            <!-- AI messages: render markdown -->
            <div v-if="msg.role === 'assistant'" class="msg-text markdown-body" v-html="renderMarkdown(msg.content)"></div>
            <!-- User messages: plain text -->
            <div v-else class="msg-text">{{ msg.content }}</div>
            <time class="msg-time">{{ formatTime(msg.created_at) }}</time>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loader2, XCircle, Lock, Eye, EyeOff, X } from 'lucide-vue-next'
import { Marked } from 'marked'
import hljs from 'highlight.js'
import api from '@/services/api'

// Configure marked with highlight.js
const marked = new Marked({
  renderer: {
    code({ text, lang }) {
      const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext'
      const highlighted = hljs.highlight(text, { language }).value
      return `<pre><code class="hljs language-${language}">${highlighted}</code></pre>`
    }
  }
})

const renderMarkdown = (content) => {
  if (!content) return ''
  try {
    return marked.parse(content)
  } catch {
    return content
  }
}

const route = useRoute()
const router = useRouter()
const token = route.params.token

const isLoading = ref(true)
const error = ref('')
const shareInfo = ref(null)
const needsPassword = ref(false)
const password = ref('')
const showPassword = ref(false)
const passwordError = ref('')
const conversationData = ref(null)
const ownerInfo = ref(null)
const messages = ref([])

const getBackendOrigin = () => {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'
  return apiBase.replace(/\/api\/?$/, '')
}

const getAvatarUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('/')) return `${getBackendOrigin()}${url}`
  return url
}

onMounted(async () => {
  try {
    const res = await api.get(`/shares/access/${token}`)
    shareInfo.value = res.data
    needsPassword.value = res.data.password_required
    ownerInfo.value = res.data.owner

    if (!needsPassword.value) {
      await loadConversation()
    }
  } catch (err) {
    error.value = err.response?.data?.error || '分享链接无效或已失效'
  } finally {
    isLoading.value = false
  }
})

const verifyPassword = async () => {
  passwordError.value = ''
  try {
    const res = await api.post(`/shares/access/${token}/verify`, {
      password: password.value
    })
    conversationData.value = res.data.conversation
    ownerInfo.value = res.data.owner
    messages.value = res.data.messages || []
  } catch (err) {
    passwordError.value = err.response?.data?.error || '密码错误'
  }
}

const loadConversation = async () => {
  try {
    const res = await api.post(`/shares/access/${token}/verify`, {})
    conversationData.value = res.data.conversation
    ownerInfo.value = res.data.owner
    messages.value = res.data.messages || []
  } catch (err) {
    error.value = err.response?.data?.error || '加载对话失败'
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.shared-view {
  min-height: 100vh;
  background: #0a0a0b;
  color: #f3f4f6;
  position: relative;
}

.shared-background {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.shared-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(128px);
}

.glow-1 {
  top: -10%;
  left: 10%;
  width: 24rem;
  height: 24rem;
  background: rgba(96, 165, 250, 0.06);
}

.glow-2 {
  bottom: -10%;
  right: 10%;
  width: 20rem;
  height: 20rem;
  background: rgba(139, 92, 246, 0.06);
}

/* Loading */
.shared-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  gap: 16px;
  position: relative;
  z-index: 1;
}
.shared-loading p { color: #6b7280; font-size: 14px; }

.spin { animation: spin 1s linear infinite; color: #60a5fa; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* Error */
.shared-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  gap: 12px;
  position: relative;
  z-index: 1;
}
.error-icon { color: #ef4444; margin-bottom: 8px; }
.shared-error h2 { font-size: 20px; color: #f3f4f6; margin: 0; }
.shared-error p { color: #6b7280; font-size: 14px; }

.error-btn {
  margin-top: 16px;
  padding: 10px 24px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  color: #f3f4f6;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.error-btn:hover { background: rgba(255, 255, 255, 0.12); }

/* Password */
.shared-password {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

.password-card {
  width: 420px;
  max-width: 90vw;
  background: #111111;
  border: 1px solid #2a2a2a;
  border-radius: 16px;
  overflow: hidden;
}

.password-card-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 24px 16px;
  gap: 8px;
}
.password-card-header h2 { margin: 0; font-size: 18px; color: #f3f4f6; }
.password-card-header p { margin: 0; font-size: 13px; color: #6b7280; }

.password-card-body { padding: 16px 24px 24px; }

.password-input-row {
  display: flex;
  align-items: center;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  padding: 0 12px;
  margin-bottom: 12px;
}

.password-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #f3f4f6;
  font-size: 14px;
  padding: 12px 0;
}
.password-input::placeholder { color: #4b5563; }

.password-toggle {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  display: flex;
}

.password-submit {
  width: 100%;
  padding: 12px;
  background: #60a5fa;
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.password-submit:hover { background: #3b82f6; }
.password-submit:disabled { opacity: 0.4; cursor: not-allowed; }

.password-error { margin: 8px 0 0; font-size: 13px; color: #ef4444; }

.password-card-footer {
  padding: 14px 24px;
  border-top: 1px solid #2a2a2a;
  font-size: 12px;
  color: #6b7280;
  text-align: center;
}

/* Conversation */
.shared-conversation {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.shared-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.shared-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.shared-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  background: #2a2a2a;
  display: flex;
  align-items: center;
  justify-content: center;
}
.shared-avatar img { width: 100%; height: 100%; object-fit: cover; }

.avatar-fallback {
  font-size: 16px;
  color: #9ca3af;
  font-weight: 600;
}
.avatar-fallback.small {
  font-size: 11px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #2a2a2a;
  color: #9ca3af;
}
.avatar-fallback.small.ai {
  background: rgba(96, 165, 250, 0.15);
  color: #60a5fa;
}

.shared-meta h1 { margin: 0; font-size: 18px; font-weight: 600; color: #f3f4f6; }
.shared-owner { font-size: 12px; color: #6b7280; }

.shared-close-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #9ca3af;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.shared-close-btn:hover { background: rgba(255, 255, 255, 0.1); color: #f3f4f6; }

.shared-messages { padding: 20px 0 40px; }

.shared-msg {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.msg-avatar { flex-shrink: 0; }
.msg-content { flex: 1; min-width: 0; }
.msg-role { font-size: 12px; font-weight: 600; color: #9ca3af; margin-bottom: 4px; }

.msg-text {
  font-size: 14px;
  line-height: 1.65;
  color: #d1d5db;
  white-space: pre-wrap;
  word-break: break-word;
}

.msg-time {
  display: block;
  margin-top: 6px;
  font-size: 11px;
  color: #4b5563;
}

/* Markdown styling for AI messages */
.markdown-body :deep(p) {
  margin: 0 0 8px;
  white-space: normal;
}

.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  color: #f3f4f6;
  margin: 16px 0 8px;
  font-weight: 600;
}

.markdown-body :deep(h1) { font-size: 1.4em; }
.markdown-body :deep(h2) { font-size: 1.2em; }
.markdown-body :deep(h3) { font-size: 1.1em; }

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
  white-space: normal;
}

.markdown-body :deep(li) {
  margin: 4px 0;
}

.markdown-body :deep(blockquote) {
  border-left: 3px solid #60a5fa;
  padding-left: 12px;
  margin: 8px 0;
  color: #9ca3af;
}

.markdown-body :deep(code) {
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  color: #e5e7eb;
  font-family: 'Fira Code', 'Consolas', monospace;
}

.markdown-body :deep(pre) {
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  padding: 14px;
  margin: 10px 0;
  overflow-x: auto;
  white-space: pre;
}

.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
  font-size: 13px;
  line-height: 1.5;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #2a2a2a;
  padding: 8px 12px;
  text-align: left;
}

.markdown-body :deep(th) {
  background: rgba(255, 255, 255, 0.05);
  font-weight: 600;
  color: #f3f4f6;
}

.markdown-body :deep(a) {
  color: #60a5fa;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid #2a2a2a;
  margin: 16px 0;
}

.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: 8px;
}

.markdown-body :deep(strong) {
  color: #f3f4f6;
  font-weight: 600;
}

.markdown-body :deep(em) {
  color: #d1d5db;
}
</style>