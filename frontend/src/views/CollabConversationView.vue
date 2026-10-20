<template>
  <div class="collab-view">
    <div class="collab-background">
      <div class="collab-glow glow-1"></div>
      <div class="collab-glow glow-2"></div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="collab-loading">
      <Loader2 :size="32" class="spin" />
      <p>正在加入协作对话...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="collab-error">
      <div class="error-icon">
        <XCircle :size="48" />
      </div>
      <h2>无法加入</h2>
      <p>{{ error }}</p>
      <button class="error-btn" @click="$router.push('/')">返回首页</button>
    </div>

    <!-- Password Required -->
    <div v-else-if="needsPassword" class="collab-password">
      <div class="password-card">
        <div class="password-card-header">
          <Users :size="24" style="color: #a78bfa;" />
          <h2>加入共同协作</h2>
          <p>请输入密码加入「{{ shareInfo?.title || '协作对话' }}」</p>
        </div>
        <div class="password-card-body">
          <div class="password-input-row">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入协作密码"
              class="password-input"
              @keydown.enter="verifyAndJoin"
            />
            <button class="password-toggle" @click="showPassword = !showPassword">
              <Eye v-if="!showPassword" :size="16" />
              <EyeOff v-else :size="16" />
            </button>
          </div>
          <button class="password-submit" @click="verifyAndJoin" :disabled="!password || isJoining">
            <Loader2 v-if="isJoining" :size="14" class="spin" />
            <Users v-else :size="14" style="margin-right: 6px;" />
            {{ isJoining ? '加入中...' : '加入共同协作' }}
          </button>
          <p v-if="passwordError" class="password-error">{{ passwordError }}</p>
        </div>
        <div class="password-card-footer">
          <div class="footer-owner">
            <div class="footer-avatar">
              <img v-if="shareInfo?.owner?.avatar_url" :src="getAvatarUrl(shareInfo.owner.avatar_url)" alt="" />
              <span v-else class="avatar-fallback">{{ (shareInfo?.owner?.nickname || '?')[0] }}</span>
            </div>
            <span>创建者：{{ shareInfo?.owner?.nickname || '未知用户' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loader2, XCircle, Users, Eye, EyeOff } from 'lucide-vue-next'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const token = route.params.token

const isLoading = ref(true)
const isJoining = ref(false)
const error = ref('')
const shareInfo = ref(null)
const needsPassword = ref(false)
const password = ref('')
const showPassword = ref(false)
const passwordError = ref('')

const getBackendOrigin = () => {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'
  return apiBase.replace(/\/api\/?$/, '')
}

const getAvatarUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('/')) return `${getBackendOrigin()}${url}`
  return url
}

const redirectToChat = (data) => {
  const conversationId = data.conversation.id
  const ownerName = data.owner?.nickname || ''
  const ownerAvatar = data.owner?.avatar_url || ''
  const ownerId = data.owner?.user_id || ''
  
  router.replace({
    path: `/chat/${conversationId}`,
    query: {
      collab: 'true',
      collab_name: ownerName,
      collab_avatar: ownerAvatar,
      collab_owner_id: ownerId
    }
  })
}

onMounted(async () => {
  try {
    const res = await api.get(`/shares/access/${token}`)
    shareInfo.value = res.data
    needsPassword.value = res.data.password_required

    // No password needed, join directly
    if (!needsPassword.value) {
      isJoining.value = true
      try {
        const verifyRes = await api.post(`/shares/access/${token}/verify`, {})
        redirectToChat(verifyRes.data)
      } catch (err) {
        error.value = err.response?.data?.error || '加入协作失败'
        isLoading.value = false
      }
    } else {
      isLoading.value = false
    }
  } catch (err) {
    error.value = err.response?.data?.error || '协作链接无效或已失效'
    isLoading.value = false
  } finally {
    if (needsPassword.value) {
      isLoading.value = false
    }
  }
})

const verifyAndJoin = async () => {
  passwordError.value = ''
  isJoining.value = true
  try {
    const res = await api.post(`/shares/access/${token}/verify`, {
      password: password.value
    })
    redirectToChat(res.data)
  } catch (err) {
    passwordError.value = err.response?.data?.error || '密码错误'
    isJoining.value = false
  }
}
</script>

<style scoped>
.collab-view {
  min-height: 100vh;
  background: #0a0a0b;
  color: #f3f4f6;
  position: relative;
  display: flex;
  flex-direction: column;
}

.collab-background {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.collab-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(128px);
}

.glow-1 {
  top: -10%;
  left: 10%;
  width: 24rem;
  height: 24rem;
  background: rgba(167, 139, 250, 0.06);
}

.glow-2 {
  bottom: -10%;
  right: 10%;
  width: 20rem;
  height: 20rem;
  background: rgba(96, 165, 250, 0.06);
}

/* Loading */
.collab-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.collab-loading p { color: #6b7280; font-size: 14px; }

.spin { animation: spin 1s linear infinite; color: #a78bfa; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* Error */
.collab-error {
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
.collab-error h2 { font-size: 20px; color: #f3f4f6; margin: 0; }
.collab-error p { color: #6b7280; font-size: 14px; }

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
.collab-password {
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
  border: 1px solid rgba(167, 139, 250, 0.2);
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
  background: #a78bfa;
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.password-submit:hover { background: #8b5cf6; }
.password-submit:disabled { opacity: 0.4; cursor: not-allowed; }

.password-error { margin: 8px 0 0; font-size: 13px; color: #ef4444; }

.password-card-footer {
  padding: 14px 24px;
  border-top: 1px solid rgba(167, 139, 250, 0.15);
  font-size: 12px;
  color: #6b7280;
}

.footer-owner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.footer-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  overflow: hidden;
  background: #2a2a2a;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-avatar img { width: 100%; height: 100%; object-fit: cover; }
.avatar-fallback { font-size: 11px; color: #9ca3af; font-weight: 600; }
</style>