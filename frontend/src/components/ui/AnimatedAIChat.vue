<template>
  <div class="ai-chat-container">
    <!-- Background Effects -->
    <div class="background-effects">
      <div class="glow glow-1"></div>
      <div class="glow glow-2"></div>
      <div class="glow glow-3"></div>
    </div>

    <!-- User Menu (Top Right) -->
    <div class="user-menu-wrapper">
      <button class="user-menu-trigger" @click="showUserMenu = !showUserMenu" @blur="handleMenuBlur">
        <div class="user-avatar-small">
          {{ userInitial }}
        </div>
        <span class="user-name">{{ displayName }}</span>
        <ChevronDown :size="14" :class="['chevron-icon', { 'chevron-open': showUserMenu }]" />
      </button>
      <Transition name="dropdown">
        <div v-if="showUserMenu" class="user-dropdown">
          <div class="dropdown-header">
            <div class="dropdown-avatar">{{ userInitial }}</div>
            <div class="dropdown-info">
              <div class="dropdown-name">{{ displayName }}</div>
              <div class="dropdown-email">{{ userEmail }}</div>
            </div>
          </div>
          <div class="dropdown-divider" />
          <button class="dropdown-item" @click="goToProfile">
            <User :size="15" />
            <span>教师画像</span>
          </button>
          <button class="dropdown-item" @click="goToProfileCenter">
            <Settings :size="15" />
            <span>账户设置</span>
          </button>
          <div class="dropdown-divider" />
          <button class="dropdown-item dropdown-item-danger" @click="handleLogout">
            <LogOut :size="15" />
            <span>退出登录</span>
          </button>
        </div>
      </Transition>
    </div>

    <!-- Main Content -->
    <div class="chat-wrapper" :class="{ 'transitioning': isTransitioning }">
      <div class="chat-content">
        <!-- Title Section -->
        <div class="title-section">
          <h1 class="main-title">今天我能为您做什么？</h1>
          <div class="title-underline"></div>
          <p class="subtitle">输入命令或提问</p>
        </div>

        <!-- Chat Box -->
        <div class="chat-box">
          <!-- Command Palette -->
          <Transition name="slide">
            <div v-if="showCommandPalette" class="command-palette">
              <div
                v-for="(suggestion, index) in filteredSuggestions"
                :key="suggestion.prefix"
                :class="['command-item', { active: activeSuggestion === index }]"
                @click="selectCommand(index)"
              >
                <component :is="suggestion.icon" class="command-icon" />
                <span class="command-label">{{ suggestion.label }}</span>
                <span class="command-prefix">{{ suggestion.prefix }}</span>
              </div>
            </div>
          </Transition>

          <!-- Textarea -->
          <div class="textarea-wrapper">
            <textarea
              ref="textareaRef"
              v-model="inputValue"
              @keydown="handleKeyDown"
              @focus="isFocused = true"
              @blur="isFocused = false"
              placeholder="问我任何问题..."
              class="chat-textarea"
              :style="{ height: textareaHeight }"
            ></textarea>
          </div>

          <!-- Attachments -->
          <Transition name="fade">
            <div v-if="attachments.length > 0" class="attachments">
              <div
                v-for="(file, index) in attachments"
                :key="index"
                class="attachment-item"
              >
                <span>{{ file }}</span>
                <button @click="removeAttachment(index)" class="remove-btn">
                  <X :size="12" />
                </button>
              </div>
            </div>
          </Transition>

          <!-- Actions Bar -->
          <div class="actions-bar">
            <div class="left-actions">
              <button @click="addAttachment" class="action-btn">
                <Paperclip :size="16" />
              </button>
              <button
                @click="toggleCommandPalette"
                :class="['action-btn', { active: showCommandPalette }]"
              >
                <Command :size="16" />
              </button>
            </div>

            <button
              @click="sendMessage"
              :disabled="!inputValue.trim() || isTyping"
              :class="['send-btn', { active: inputValue.trim() && !isTyping }]"
            >
              <Loader2 v-if="isTyping" :size="16" class="spin" />
              <Send v-else :size="16" />
              <span>发送</span>
            </button>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
          <button
            v-for="(suggestion, index) in commandSuggestions"
            :key="suggestion.prefix"
            @click="selectCommand(index)"
            class="quick-action-btn"
          >
            <component :is="suggestion.icon" :size="16" />
            <span>{{ suggestion.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Typing Indicator -->
    <Transition name="slide-up">
      <div v-if="isTyping" class="typing-indicator">
        <div class="typing-avatar">AI</div>
        <div class="typing-content">
          <span>思考中</span>
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Mouse Follow Effect -->
    <div
      v-if="isFocused"
      class="mouse-follow"
      :style="{ left: mousePos.x - 400 + 'px', top: mousePos.y - 400 + 'px' }"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import {
  Image as ImageIcon,
  Figma,
  Monitor,
  Sparkles,
  Paperclip,
  Command,
  Send,
  X,
  Loader2,
  FileText,
  Layout,
  User,
  MessageSquare,
  GraduationCap,
  ChevronDown,
  LogOut,
  Settings
} from 'lucide-vue-next'

import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import authService from '@/services/auth'

const authStore = useAuthStore()
const showUserMenu = ref(false)

const displayName = computed(() => authStore.currentUser?.username || '用户')
const userEmail = computed(() => authStore.currentUser?.email || '')
const userInitial = computed(() => {
  const name = displayName.value
  return name ? name.charAt(0).toUpperCase() : 'U'
})

const handleMenuBlur = () => {
  setTimeout(() => { showUserMenu.value = false }, 150)
}

const hasProfileData = (profile: any) => {
  if (!profile || typeof profile !== 'object') return false

  const fields = [
    profile.nickname,
    profile.avatar_url,
    profile.teacher_gender,
    profile.teacher_age,
    profile.school_name,
    profile.subject_category
  ]

  const hasBasic = fields.some(v => v !== null && v !== undefined && String(v).trim() !== '')
  const hasCourses = Array.isArray(profile.courses) && profile.courses.length > 0
  const hasStyles = Array.isArray(profile.teaching_styles) && profile.teaching_styles.length > 0

  return hasBasic || hasCourses || hasStyles
}

const goToProfile = async () => {
  showUserMenu.value = false

  if (props.useProfileModal) {
    emit('open-profile-modal', 'profile')
    return
  }

  try {
    const res = await authService.getProfile()
    const profile = res?.data?.profile

    if (hasProfileData(profile)) {
      router.push('/profile')
    } else {
      router.push('/profile-onboarding')
    }
  } catch {
    // 获取失败时兜底到画像引导页
    router.push('/profile-onboarding')
  }
}

const goToProfileCenter = () => {
  showUserMenu.value = false

  if (props.useProfileModal) {
    emit('open-profile-modal', 'profile-center')
    return
  }

  router.push('/profile-center')
}

const handleLogout = () => {
  showUserMenu.value = false
  authStore.logout()
  router.push('/login')
}

const props = withDefaults(defineProps<{
  useProfileModal?: boolean
}>(), {
  useProfileModal: false
})

const emit = defineEmits<{
  (e: 'send-message', message: string): void
  (e: 'open-profile-modal', source: 'profile' | 'profile-center'): void
}>()

const router = useRouter()
const inputValue = ref('')
const attachments = ref<string[]>([])
const isTyping = ref(false)
const showCommandPalette = ref(false)
const activeSuggestion = ref(-1)
const isFocused = ref(false)
const mousePos = ref({ x: 0, y: 0 })
const textareaRef = ref<HTMLTextAreaElement>()
const textareaHeight = ref('60px')

const commandSuggestions = [
  {
    icon: MessageSquare,
    label: '对话管理',
    prefix: '/chat',
    route: '/chat'
  },
  {
    icon: FileText,
    label: '文档管理',
    prefix: '/documents',
    route: '/documents'
  },
  {
    icon: Layout,
    label: '模板管理',
    prefix: '/templates',
    route: '/templates'
  },
  {
    icon: User,
    label: '数字人',
    prefix: '/avatar',
    route: '/avatar'
  },
  {
    icon: GraduationCap,
    label: '资源社区',
    prefix: '/community',
    route: '/community'
  }
]

const filteredSuggestions = computed(() => {
  if (!inputValue.value.startsWith('/')) return []
  return commandSuggestions.filter(cmd =>
    cmd.prefix.startsWith(inputValue.value)
  )
})

watch(inputValue, (newVal) => {
  // Auto-resize textarea
  if (textareaRef.value) {
    textareaRef.value.style.height = '60px'
    const scrollHeight = textareaRef.value.scrollHeight
    textareaHeight.value = `${Math.min(Math.max(60, scrollHeight), 200)}px`
  }

  // Show command palette
  if (newVal.startsWith('/') && !newVal.includes(' ')) {
    showCommandPalette.value = true
    const matchIndex = commandSuggestions.findIndex(cmd =>
      cmd.prefix.startsWith(newVal)
    )
    activeSuggestion.value = matchIndex
  } else {
    showCommandPalette.value = false
  }
})

function handleKeyDown(e: KeyboardEvent) {
  if (showCommandPalette.value) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      activeSuggestion.value = Math.min(
        activeSuggestion.value + 1,
        filteredSuggestions.value.length - 1
      )
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      activeSuggestion.value = Math.max(activeSuggestion.value - 1, 0)
    } else if (e.key === 'Tab' || e.key === 'Enter') {
      e.preventDefault()
      if (activeSuggestion.value >= 0) {
        selectCommand(activeSuggestion.value)
      }
    } else if (e.key === 'Escape') {
      showCommandPalette.value = false
    }
  } else if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

function selectCommand(index: number) {
  const command = commandSuggestions[index]

  if (props.useProfileModal && command.route === '/profile') {
    emit('open-profile-modal', 'profile')
    inputValue.value = ''
    showCommandPalette.value = false
    return
  }

  // 如果有路由，则跳转到对应页面
  if (command.route) {
    router.push(command.route)
    inputValue.value = ''
    showCommandPalette.value = false
  } else {
    inputValue.value = command.prefix + ' '
    showCommandPalette.value = false
  }
}

function sendMessage() {
  if (!inputValue.value.trim() || isTyping.value) return

  const message = inputValue.value
  const files = [...attachments.value]
  
  // 启动过渡动画
  isTransitioning.value = true
  
  // 延迟跳转，让动画有时间执行
  setTimeout(() => {
    // 清空输入
    inputValue.value = ''
    attachments.value = []
    textareaHeight.value = '60px'
    
    // 直接跳转到对话页面，通过 sessionStorage 传递数据
    sessionStorage.setItem('dashboardMessage', message)
    if (files.length > 0) {
      sessionStorage.setItem('dashboardFiles', JSON.stringify(files))
    }
    router.push('/chat')
  }, 300) // 300ms 的过渡时间
}

const fileInputRef = ref<HTMLInputElement>()
const isTransitioning = ref(false)

function addAttachment() {
  // 创建隐藏的文件输入元素
  if (!fileInputRef.value) {
    const input = document.createElement('input')
    input.type = 'file'
    input.multiple = true
    input.style.display = 'none'
    input.onchange = (e: Event) => {
      const files = (e.target as HTMLInputElement).files
      if (files) {
        Array.from(files).forEach(file => {
          attachments.value.push(file.name)
        })
      }
    }
    document.body.appendChild(input)
    fileInputRef.value = input
  }
  fileInputRef.value.click()
}

function removeAttachment(index: number) {
  attachments.value.splice(index, 1)
}

function toggleCommandPalette() {
  if (!inputValue.value.startsWith('/')) {
    inputValue.value = '/'
  }
  showCommandPalette.value = !showCommandPalette.value
}

onMounted(() => {
  const handleMouseMove = (e: MouseEvent) => {
    mousePos.value = { x: e.clientX, y: e.clientY }
  }
  window.addEventListener('mousemove', handleMouseMove)
  onUnmounted(() => {
    window.removeEventListener('mousemove', handleMouseMove)
  })
})
</script>

<style scoped>
.ai-chat-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #0A0A0B;
  color: white;
  position: relative;
  overflow: hidden;
  padding: 2rem;
}

/* Background Effects */
.background-effects {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.glow {
  position: absolute;
  border-radius: 50%;
  mix-blend-mode: normal;
  filter: blur(128px);
  animation: pulse 4s ease-in-out infinite;
}

.glow-1 {
  top: 0;
  left: 25%;
  width: 24rem;
  height: 24rem;
  background: rgba(139, 92, 246, 0.1);
}

.glow-2 {
  bottom: 0;
  right: 25%;
  width: 24rem;
  height: 24rem;
  background: rgba(99, 102, 241, 0.1);
  animation-delay: 0.7s;
}

.glow-3 {
  top: 25%;
  right: 33%;
  width: 16rem;
  height: 16rem;
  background: rgba(217, 70, 239, 0.1);
  filter: blur(96px);
  animation-delay: 1s;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Chat Wrapper */
.chat-wrapper {
  width: 100%;
  max-width: 42rem;
  position: relative;
  z-index: 10;
}

.chat-content {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

/* Title Section */
.title-section {
  text-align: center;
  animation: fadeIn 0.6s ease-out;
}

.main-title {
  font-size: 1.875rem;
  font-weight: 500;
  background: linear-gradient(to right, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.4));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.25rem;
}

.title-underline {
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: expand 0.8s ease-out 0.5s both;
}

@keyframes expand {
  from { width: 0; opacity: 0; }
  to { width: 100%; opacity: 1; }
}

.subtitle {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 0.75rem;
  animation: fadeIn 0.6s ease-out 0.3s both;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Chat Box */
.chat-box {
  position: relative;
  backdrop-filter: blur(40px);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  animation: scaleIn 0.6s ease-out 0.1s both;
}

@keyframes scaleIn {
  from { transform: scale(0.98); }
  to { transform: scale(1); }
}

/* Command Palette */
.command-palette {
  position: absolute;
  left: 1rem;
  right: 1rem;
  bottom: 100%;
  margin-bottom: 0.5rem;
  backdrop-filter: blur(20px);
  background: rgba(0, 0, 0, 0.9);
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  z-index: 50;
}

.command-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.15s;
}

.command-item:hover,
.command-item.active {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.command-icon {
  width: 1rem;
  height: 1rem;
  color: rgba(255, 255, 255, 0.6);
}

.command-label {
  font-weight: 500;
}

.command-prefix {
  font-size: 0.625rem;
  color: rgba(255, 255, 255, 0.4);
  margin-left: 0.25rem;
}

/* Textarea */
.textarea-wrapper {
  padding: 1rem;
}

.chat-textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  outline: none;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.875rem;
  line-height: 1.5;
  resize: none;
  min-height: 60px;
  max-height: 200px;
}

.chat-textarea::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

/* Attachments */
.attachments {
  padding: 0 1rem 0.75rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.5rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
}

.remove-btn {
  padding: 0;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: white;
}

/* Actions Bar */
.actions-bar {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.left-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  padding: 0.5rem;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.action-btn:hover {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.05);
}

.action-btn.active {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.send-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 0.5rem;
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn.active {
  background: white;
  color: #0A0A0B;
  box-shadow: 0 10px 25px rgba(255, 255, 255, 0.1);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spin {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Quick Actions */
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.5rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-action-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

/* Typing Indicator */
.typing-indicator {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  backdrop-filter: blur(40px);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 9999px;
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.typing-avatar {
  width: 2rem;
  height: 1.75rem;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.typing-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.7);
}

.typing-dots {
  display: flex;
  gap: 0.25rem;
  margin-left: 0.25rem;
}

.typing-dots span {
  width: 0.375rem;
  height: 0.375rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  animation: typing 1.2s ease-in-out infinite;
  box-shadow: 0 0 4px rgba(255, 255, 255, 0.3);
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes typing {
  0%, 100% {
    opacity: 0.3;
    transform: scale(0.85);
  }
  50% {
    opacity: 0.9;
    transform: scale(1.1);
  }
}

/* Mouse Follow Effect */
.mouse-follow {
  position: fixed;
  width: 50rem;
  height: 50rem;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.02;
  background: linear-gradient(to right, #8b5cf6, #d946ef, #6366f1);
  filter: blur(96px);
  transition: all 0.3s ease-out;
}

/* Transition Animation */
.chat-wrapper.transitioning {
  animation: fadeOutUp 0.3s ease-out forwards;
}

@keyframes fadeOutUp {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-20px) scale(0.98);
  }
}

/* Transitions */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.15s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(5px);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translate(-50%, 20px);
}

/* User Menu */
.user-menu-wrapper {
  position: fixed;
  top: 1.25rem;
  right: 1.5rem;
  z-index: 100;
}

.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px 6px 6px;
  border-radius: 9999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
}

.user-menu-trigger:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.user-avatar-small {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.user-name {
  font-weight: 500;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chevron-icon {
  transition: transform 0.2s ease;
  opacity: 0.5;
}

.chevron-open {
  transform: rotate(180deg);
}

/* Dropdown */
.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 240px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(24, 24, 27, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
  padding: 6px;
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
}

.dropdown-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.dropdown-info {
  min-width: 0;
}

.dropdown-name {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-email {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 1px;
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin: 4px 6px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.95);
}

.dropdown-item-danger {
  color: #f87171;
}

.dropdown-item-danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #fca5a5;
}

/* Dropdown transition */
.dropdown-enter-active {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.dropdown-leave-active {
  transition: all 0.15s ease-in;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.96);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}
</style>
