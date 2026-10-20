<template>
  <div class="dashboard invert-on-light">
    <AnimatedAIChat use-profile-modal @send-message="handleSendMessage" @open-profile-modal="openProfileModal" />

    <Teleport to="body">
      <Transition name="profile-modal-fade">
        <div v-if="showProfileModal" class="profile-modal-overlay" @click.self="closeProfileModal">
          <div class="profile-modal-panel">
            <UserProfileCenter in-modal @close="closeProfileModal" />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import { ElMessage } from 'element-plus'
import AnimatedAIChat from '@/components/ui/AnimatedAIChat.vue'
import UserProfileCenter from '@/views/UserProfileCenter.vue'

const router = useRouter()
const authStore = useAuthStore()
const showProfileModal = ref(false)

onMounted(async () => {
  try {
    await authStore.fetchCurrentUser()
  } catch (error) {
    ElMessage.error('获取用户信息失败')
    router.push('/login')
  }
})

const handleSendMessage = (messageDataStr) => {
  try {
    // 解析消息数据
    const messageData = JSON.parse(messageDataStr)
    const { message, files } = messageData
    
    // 用户发送消息后，跳转到实际的对话页面，并传递消息和文件
    router.push({
      path: '/chat',
      query: {
        message: encodeURIComponent(message),
        files: files && files.length > 0 ? files.join(',') : undefined,
        timestamp: Date.now()
      }
    })
  } catch (error) {
    console.error('解析消息数据失败:', error)
    // 如果解析失败，直接跳转
    router.push('/chat')
  }
}

const openProfileModal = () => {
  showProfileModal.value = true
  document.body.style.overflow = 'hidden'
}

const closeProfileModal = () => {
  showProfileModal.value = false
  document.body.style.overflow = ''
}
</script>

<style scoped>
.dashboard {
  height: 100vh;
  overflow: hidden;
}

.profile-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(3, 8, 20, 0.55);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.profile-modal-panel {
  width: min(760px, 92vw);
  max-height: 92vh;
  overflow: auto;
  position: relative;
  border-radius: 20px;
  background: transparent;
  box-shadow: none;
}

.profile-modal-fade-enter-active,
.profile-modal-fade-leave-active {
  transition: opacity .2s ease;
}

.profile-modal-fade-enter-from,
.profile-modal-fade-leave-to {
  opacity: 0;
}
</style>
