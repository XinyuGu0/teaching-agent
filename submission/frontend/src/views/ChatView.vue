<!--
  ChatView - AI 对话核心页面
  功能：WebSocket 实时对话、流式消息展示、大纲生成、PPT 触发生成
-->
<template>
  <div class="chat-container">
    <!-- 左侧：对话列表 -->
    <aside class="sidebar">
      <button class="btn-new" @click="createConversation">+ 新对话</button>
      <div
        v-for="conv in conversations"
        :key="conv.id"
        :class="['conv-item', { active: conv.id === currentId }]"
        @click="switchConversation(conv.id)"
      >
        <span class="conv-title">{{ conv.title }}</span>
        <span class="conv-time">{{ formatTime(conv.updated_at) }}</span>
      </div>
    </aside>

    <!-- 右侧：聊天区域 -->
    <main class="chat-main">
      <!-- 消息列表 -->
      <div class="messages" ref="messagesRef">
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="['message', msg.role]"
        >
          <div class="avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
          <div class="bubble">
            <!-- 普通文本消息 -->
            <div v-if="!msg.meta_data?.outline" class="text" v-html="renderMarkdown(msg.content)" />

            <!-- 大纲消息 -->
            <div v-else class="outline-card">
              <h3>{{ msg.meta_data.outline.title || 'PPT 大纲' }}</h3>
              <div v-for="slide in msg.meta_data.outline.slides" :key="slide.slide_number" class="slide-item">
                <strong>第{{ slide.slide_number }}页：</strong>{{ slide.title }}
                <ul>
                  <li v-for="point in slide.content_points" :key="point">{{ point }}</li>
                </ul>
              </div>
              <button class="btn-generate" @click="handleGeneratePpt(msg.meta_data.outline)">
                生成 PPT
              </button>
            </div>
          </div>
        </div>

        <!-- 流式输出中的临时内容 -->
        <div v-if="streamingContent" class="message assistant streaming">
          <div class="avatar">AI</div>
          <div class="bubble">
            <div class="text" v-html="renderMarkdown(streamingContent)" />
            <span class="cursor">▌</span>
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="input-area">
        <textarea
          v-model="inputText"
          placeholder="输入消息，如：帮我生成关于数据库的PPT..."
          @keydown.enter.exact.prevent="handleSend"
          rows="2"
        />
        <button class="btn-send" :disabled="!inputText.trim() || sending" @click="handleSend">
          发送
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ChatWebSocket } from '@/utils/websocket'
import api from '@/utils/api'

const route = useRoute()
const authStore = useAuthStore()

// ---- 状态 ----
const conversations = ref([])
const messages = ref([])
const currentId = ref(route.params.id || '')
const inputText = ref('')
const sending = ref(false)
const streamingContent = ref('')
const messagesRef = ref(null)
let ws = null

// ---- 生命周期 ----
onMounted(async () => {
  await loadConversations()
  if (currentId.value) {
    await loadMessages(currentId.value)
    connectWebSocket(currentId.value)
  }
})

onUnmounted(() => {
  ws?.disconnect()
})

// ---- 对话管理 ----

/** 加载对话列表 */
async function loadConversations() {
  const res = await api.get('/api/conversations')
  conversations.value = res.data.conversations
}

/** 创建新对话 */
async function createConversation() {
  const res = await api.post('/api/conversations', { title: 'New Conversation' })
  const conv = res.data.conversation
  conversations.value.unshift(conv)
  switchConversation(conv.id)
}

/** 切换对话 */
function switchConversation(id) {
  currentId.value = id
  messages.value = []
  streamingContent.value = ''
  loadMessages(id)
  connectWebSocket(id)
}

/** 加载消息历史 */
async function loadMessages(id) {
  const res = await api.get(`/api/conversations/${id}`)
  messages.value = res.data.conversation.messages || []
  await nextTick()
  scrollToBottom()
}

// ---- WebSocket 通信 ----

/** 建立 WebSocket 连接并注册事件 */
function connectWebSocket(conversationId) {
  ws?.disconnect()
  ws = new ChatWebSocket(conversationId, authStore.user?.id)
  ws.connect()

  // 接收完整消息
  ws.on('message_received', (msg) => {
    messages.value.push(msg)
    scrollToBottom()
  })

  // 流式文本片段
  ws.on('message_chunk', (data) => {
    streamingContent.value += data.content
    scrollToBottom()
  })

  // 流式输出结束
  ws.on('streaming_start', () => {
    streamingContent.value = ''
    sending.value = true
  })

  // 大纲生成完成
  ws.on('outline_generated', (data) => {
    if (data.message) {
      messages.value.push(data.message)
    }
    streamingContent.value = ''
    sending.value = false
    scrollToBottom()
  })

  // 错误处理
  ws.on('error', (data) => {
    console.error('[Chat Error]', data.message)
    sending.value = false
  })
}

// ---- 消息发送 ----

/** 发送用户消息 */
function handleSend() {
  const text = inputText.value.trim()
  if (!text || sending.value) return

  // 本地立即显示用户消息
  messages.value.push({
    id: Date.now().toString(),
    conversation_id: currentId.value,
    role: 'user',
    content: text,
    created_at: new Date().toISOString(),
  })

  ws.sendMessage(text)
  inputText.value = ''
  sending.value = true
  scrollToBottom()
}

// ---- PPT 生成 ----

/** 触发 PPT 生成 */
function handleGeneratePpt(outline) {
  ws?.generatePpt()
}

// ---- 工具函数 ----

/** 滚动到底部 */
function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

/** 简易 Markdown 渲染（换行 -> <br>） */
function renderMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/&/g, '&')
    .replace(/</g, '<')
    .replace(/>/g, '>')
    .replace(/\n/g, '<br>')
}

/** 格式化时间 */
function formatTime(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.sidebar {
  width: 260px;
  background: #f7f8fa;
  border-right: 1px solid #e5e7eb;
  padding: 16px;
  overflow-y: auto;
}

.btn-new {
  width: 100%;
  padding: 10px;
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 12px;
  font-size: 14px;
}

.conv-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conv-item:hover { background: #e5e7eb; }
.conv-item.active { background: #e0e7ff; }

.conv-title {
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 150px;
}

.conv-time { font-size: 11px; color: #9ca3af; }

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  display: flex;
  margin-bottom: 16px;
}

.message.user { flex-direction: row-reverse; }

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e0e7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.bubble {
  max-width: 70%;
  margin: 0 12px;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.message.user .bubble { background: #4f46e5; color: #fff; }
.message.assistant .bubble { background: #f3f4f6; color: #1f2937; }

.cursor {
  animation: blink 1s infinite;
  color: #6366f1;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.outline-card { padding: 8px; }
.outline-card h3 { margin-bottom: 12px; }
.slide-item { margin-bottom: 8px; font-size: 13px; }
.slide-item ul { padding-left: 16px; margin: 4px 0; }

.btn-generate {
  margin-top: 12px;
  padding: 8px 20px;
  background: #059669;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.input-area {
  display: flex;
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  gap: 12px;
}

.input-area textarea {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  resize: none;
  font-size: 14px;
  outline: none;
}

.input-area textarea:focus { border-color: #6366f1; }

.btn-send {
  padding: 10px 24px;
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.btn-send:disabled { opacity: 0.5; cursor: not-allowed; }
</style>