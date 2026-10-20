<template>
  <Teleport to="body">
    <div v-if="open" class="share-dialog-overlay" @click.self="handleClose">
      <div class="share-dialog-panel">
        <!-- Header -->
        <div class="share-dialog-header">
          <div class="share-dialog-title-row">
            <Share2 :size="18" class="share-dialog-icon" />
            <span class="share-dialog-title">分享对话</span>
          </div>
          <button class="share-dialog-close" @click="handleClose">
            <X :size="18" />
          </button>
        </div>

        <!-- Body -->
        <div class="share-dialog-body">
          <!-- Share Type Selection -->
          <div class="share-type-section">
            <div class="share-type-label">分享方式</div>
            <div class="share-type-options">
              <button
                :class="['share-type-btn', { active: localShareType === 'disabled' }]"
                @click="switchShareType('disabled')"
              >
                <Lock :size="15" />
                <span>关闭分享</span>
              </button>
              <button
                :class="['share-type-btn', { active: localShareType === 'internal' }]"
                @click="switchShareType('internal')"
              >
                <Users :size="15" />
                <span>指定用户</span>
              </button>
              <button
                :class="['share-type-btn', { active: localShareType === 'public' }]"
                @click="switchShareType('public')"
              >
                <Globe :size="15" />
                <span>互联网分享</span>
              </button>
              <button
                :class="['share-type-btn', { active: localShareType === 'collaborate' }]"
                @click="switchShareType('collaborate')"
              >
                <UserPlus :size="15" />
                <span>协同协作</span>
              </button>
            </div>
          </div>

          <!-- Disabled State -->
          <div v-if="localShareType === 'disabled'" class="share-disabled-hint">
            <Lock :size="20" style="color: #6b7280; margin-bottom: 8px;" />
            <p>当前对话未开启分享</p>
            <p class="share-disabled-sub">选择一种分享方式，让其他人查看此对话</p>
          </div>

          <!-- Internal User Selection -->
          <div v-if="localShareType === 'internal'" class="share-internal-section">
            <!-- Search Users -->
            <div class="user-search-box">
              <Search :size="14" class="search-icon" />
              <input
                v-model="userSearchQuery"
                type="text"
                placeholder="搜索用户名或邮箱..."
                class="user-search-input"
                @input="handleUserSearch"
              />
              <Loader2 v-if="isSearchingUsers" :size="14" class="spin search-loading" />
            </div>

            <!-- Search Results -->
            <div v-if="searchResults.length > 0" class="user-search-results">
              <div
                v-for="user in searchResults"
                :key="user.id"
                class="user-result-item"
                @click="addUser(user)"
              >
                <div class="user-result-avatar">
                  <img v-if="user.avatar_url" :src="getUserAvatarUrl(user.avatar_url)" alt="" />
                  <span v-else class="user-avatar-fallback">{{ (user.nickname || user.username || '?')[0] }}</span>
                </div>
                <div class="user-result-info">
                  <span class="user-result-name">{{ user.nickname || user.username }}</span>
                  <span class="user-result-email">{{ user.email }}</span>
                </div>
                <Plus :size="14" class="user-add-icon" />
              </div>
            </div>

            <!-- Selected Users -->
            <div v-if="selectedUsers.length > 0" class="selected-users-section">
              <div class="selected-users-label">已选择 ({{ selectedUsers.length }})</div>
              <div class="selected-users-list">
                <div v-for="user in selectedUsers" :key="user.id" class="selected-user-tag">
                  <span class="selected-user-name">{{ user.nickname || user.username }}</span>
                  <button class="selected-user-remove" @click="removeUser(user.id)">
                    <X :size="10" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Collaborate Settings -->
          <div v-if="localShareType === 'collaborate'" class="share-collaborate-section">
            <div class="collaborate-hint" style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:30px 20px;text-align:center;">
              <UserPlus :size="20" style="color: #a78bfa; margin-bottom: 8px;" />
              <p style="margin:0;color:#6b7280;font-size:14px;">允许其他用户实时参与对话协作</p>
              <p style="margin:4px 0 0;color:#4b5563;font-size:12px;">协作者可通过链接加入对话，共同编辑和讨论</p>
            </div>
          </div>

          <!-- Public Share Settings -->
          <div v-if="localShareType === 'public'" class="share-public-section">
            <div class="password-section">
              <div class="password-label">
                <span>访问密码</span>
                <span class="password-optional">（选填）</span>
              </div>
              <div class="password-input-row">
                <input
                  v-model="localPassword"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="设置密码以保护分享链接"
                  class="password-input"
                />
                <button class="password-toggle" @click="showPassword = !showPassword">
                  <Eye v-if="!showPassword" :size="14" />
                  <EyeOff v-else :size="14" />
                </button>
              </div>
              <p class="password-hint">留空则无需密码即可访问</p>
            </div>
          </div>

          <!-- Share Link (shown after saving) -->
          <div v-if="shareLink && localShareType !== 'disabled'" class="share-link-section">
            <div class="share-link-label">分享链接</div>
            <div class="share-link-box">
              <input :value="shareLink" readonly class="share-link-input" />
              <button class="share-copy-btn" @click="copyLink">
                <CheckCircle2 v-if="copied" :size="14" style="color: #34d399;" />
                <Copy v-else :size="14" />
                <span>{{ copied ? '已复制' : '复制' }}</span>
              </button>
            </div>
            <div v-if="localPassword" class="share-password-display">
              <span class="share-password-label">密码：</span>
              <span class="share-password-value">{{ localPassword }}</span>
              <button class="share-copy-btn small" @click="copyPassword">
                <Copy :size="12" />
              </button>
            </div>
          </div>

          <!-- Share to Platforms -->
          <div v-if="shareLink && localShareType !== 'disabled'" class="share-platforms-section">
            <div class="share-platforms-label">分享到</div>
            <div class="share-platforms-list">
              <button class="platform-btn wechat" title="微信" @click="shareToPlatform('wechat')">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.534c0 2.09.955 3.99 2.52 5.38l-.633 1.912a.5.5 0 00.718.572l2.294-1.148c.82.252 1.69.396 2.593.42a5.556 5.556 0 01-.197-1.462c0-3.659 3.357-6.627 7.5-6.627.256 0 .509.013.759.036C14.848 4.896 12.081 2.188 8.691 2.188zm-2.6 4.17a1.12 1.12 0 110 2.24 1.12 1.12 0 010-2.24zm5.198 0a1.12 1.12 0 110 2.24 1.12 1.12 0 010-2.24zM14.795 9.534c-3.587 0-6.5 2.514-6.5 5.613 0 3.1 2.913 5.613 6.5 5.613.718 0 1.41-.102 2.06-.29l1.76.88a.5.5 0 00.718-.572l-.484-1.464c1.282-1.14 2.07-2.72 2.07-4.467-.2-3-3.113-5.313-6.124-5.313zm-2.28 3.456a.896.896 0 110 1.792.896.896 0 010-1.792zm4.56 0a.896.896 0 110 1.792.896.896 0 010-1.792z"/>
                </svg>
                <span>微信</span>
              </button>
                <!-- <button class="platform-btn weibo" title="微博" @click="shareToPlatform('weibo')">
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                    <path d="M10.098 20.323c-3.977.391-7.414-1.406-7.672-4.02-.259-2.609 2.759-5.047 6.74-5.441 3.979-.394 7.413 1.404 7.671 4.018.259 2.6-2.759 5.049-6.739 5.443z"/>
                    <path d="M20.196 9.4c-.256-.824-.878-1.387-1.63-1.387-.196 0-.393.037-.58.107l-.015.006c-.553.213-.863.79-.688 1.292.178.502.768.755 1.324.545.553-.212 1.224-.027 1.484.398.26.427.061 1.006-.488 1.218-.553.21-.858.789-.684 1.292.175.503.766.756 1.32.544 1.252-.48 1.878-1.792 1.438-3.015zM16.732 4.356c-.468-1.524-1.728-2.349-3.074-2.349-.386 0-.78.067-1.165.215l-.03.012c-1.178.453-1.69 1.65-1.283 2.744.408 1.096 1.6 1.619 2.784 1.177 1.178-.452 2.468.025 2.956.98.49.956.118 2.173-1.06 2.626-1.18.45-1.695 1.647-1.287 2.743.407 1.095 1.603 1.615 2.784 1.174 2.54-.977 3.824-3.726 2.89-6.122z"/>
                  </svg>
                  <span>微博</span>
                </button> -->
              <button class="platform-btn qq" title="QQ" @click="shareToPlatform('qq')">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                </svg>
                <span>QQ</span>
              </button>
              <button class="platform-btn dingtalk" title="钉钉" @click="shareToPlatform('dingtalk')">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5.5 13.5l-2 1.5-.5-.5-2 1.5-.5-1-1.5 1-.5-1.5-1 1v-2l-1.5-1.5L8 13l1-2-1.5-2H9l1.5 1.5L12 9l1.5 1.5L15 9h1.5L15 11l1 2-1.5 1.5 1 2z"/>
                </svg>
                <span>钉钉</span>
              </button>
              <button class="platform-btn link" title="复制链接" @click="copyLink">
                <Link2 :size="18" />
                <span>链接</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="share-dialog-footer">
          <UiButton variant="outline" @click="handleClose">取消</UiButton>
          <UiButton
            variant="default"
            :disabled="isSaving || (localShareType === 'internal' && selectedUsers.length === 0)"
            @click="handleSave"
          >
            <Loader2 v-if="isSaving" :size="14" class="spin" />
            <span>{{ isSaving ? '保存中...' : '保存设置' }}</span>
          </UiButton>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { Share2, X, Lock, Users, Globe, Search, Plus, Copy, CheckCircle2, Eye, EyeOff, Link2, Loader2, UserPlus } from 'lucide-vue-next'
import UiButton from './Button.vue'
import api from '@/services/api'
import { ElMessage } from 'element-plus'

const props = defineProps({
  open: Boolean,
  conversationId: String,
  conversationTitle: String
})

const emit = defineEmits(['close', 'saved'])

// Local state
const localShareType = ref('disabled')
const localPassword = ref('')
const showPassword = ref(false)
const shareLink = ref('')
const copied = ref(false)
const isSaving = ref(false)

// User search state
const userSearchQuery = ref('')
const searchResults = ref([])
const selectedUsers = ref([])
const isSearchingUsers = ref(false)
let searchTimer = null

const getBackendOrigin = () => {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'
  return apiBase.replace(/\/api\/?$/, '')
}

const getUserAvatarUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('/')) return `${getBackendOrigin()}${url}`
  return url
}

// Watch for open changes to load current settings
watch(() => props.open, async (newVal) => {
  if (newVal && props.conversationId) {
    await loadShareSettings()
  }
})

const loadShareSettings = async () => {
  try {
    const res = await api.get(`/shares/${props.conversationId}/share`)
    const data = res.data
    localShareType.value = data.share_type || 'disabled'
    localPassword.value = data.password || ''
    selectedUsers.value = data.allowed_users || []
    shareLink.value = data.share_link || ''
  } catch (err) {
    console.error('加载分享设置失败:', err)
  }
}

const switchShareType = (type) => {
  localShareType.value = type
  if (type === 'disabled') {
    shareLink.value = ''
  }
}

const handleUserSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(async () => {
    if (!userSearchQuery.value.trim()) {
      searchResults.value = []
      return
    }
    isSearchingUsers.value = true
    try {
      const res = await api.get('/shares/users/search', {
        params: { q: userSearchQuery.value.trim() }
      })
      // Filter out already selected users
      const selectedIds = selectedUsers.value.map(u => u.id)
      searchResults.value = (res.data.users || []).filter(u => !selectedIds.includes(u.id))
    } catch (err) {
      console.error('搜索用户失败:', err)
    } finally {
      isSearchingUsers.value = false
    }
  }, 300)
}

const addUser = (user) => {
  if (!selectedUsers.value.find(u => u.id === user.id)) {
    selectedUsers.value.push(user)
  }
  searchResults.value = searchResults.value.filter(u => u.id !== user.id)
  userSearchQuery.value = ''
}

const removeUser = (userId) => {
  selectedUsers.value = selectedUsers.value.filter(u => u.id !== userId)
}

const handleSave = async () => {
  isSaving.value = true
  try {
    const payload = {
      share_type: localShareType.value
    }
    if (localShareType.value === 'internal') {
      payload.allowed_user_ids = selectedUsers.value.map(u => u.id)
    } else if (localShareType.value === 'public') {
      payload.password = localPassword.value || null
    } else if (localShareType.value === 'collaborate') {
      payload.password = localPassword.value || null
    }

    const res = await api.post(`/shares/${props.conversationId}/share`, payload)
    const data = res.data

    if (localShareType.value !== 'disabled') {
      shareLink.value = data.share_link || ''
    } else {
      shareLink.value = ''
    }

    ElMessage.success(data.message || '分享设置已更新')
    emit('saved', data)
  } catch (err) {
    const msg = err.response?.data?.error || '保存失败'
    ElMessage.error(msg)
  } finally {
    isSaving.value = false
  }
}

const copyLink = async () => {
  if (!shareLink.value) return
  try {
    await navigator.clipboard.writeText(shareLink.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
    ElMessage.success('链接已复制到剪贴板')
  } catch {
    // Fallback
    const input = document.createElement('input')
    input.value = shareLink.value
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
    ElMessage.success('链接已复制到剪贴板')
  }
}

const copyPassword = async () => {
  if (!localPassword.value) return
  try {
    await navigator.clipboard.writeText(localPassword.value)
    ElMessage.success('密码已复制')
  } catch {
    const input = document.createElement('input')
    input.value = localPassword.value
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    ElMessage.success('密码已复制')
  }
}

const shareToPlatform = (platform) => {
  const url = encodeURIComponent(shareLink.value)
  const title = encodeURIComponent(props.conversationTitle || '分享的对话')
  let shareUrl = ''

  switch (platform) {
    case 'wechat':
      // WeChat doesn't have a direct share URL, copy link instead
      copyLink()
      ElMessage.info('请打开微信，粘贴链接发送给好友')
      return
    case 'weibo':
      shareUrl = `https://service.weibo.com/share/share.php?url=${url}&title=${title}`
      break
    case 'qq':
      shareUrl = `https://connect.qq.com/widget/shareqq/index.html?url=${url}&title=${title}`
      break
    case 'dingtalk':
      copyLink()
      ElMessage.info('请打开钉钉，粘贴链接发送给好友')
      return
    case 'link':
      copyLink()
      return
  }

  if (shareUrl) {
    window.open(shareUrl, '_blank', 'width=600,height=400')
  }
}

const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.share-dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.share-dialog-panel {
  background: #111111;
  border: 1px solid #2a2a2a;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  width: 520px;
  max-width: 90vw;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.share-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #2a2a2a;
}

.share-dialog-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.share-dialog-icon {
  color: #60a5fa;
}

.share-dialog-title {
  font-size: 16px;
  font-weight: 600;
  color: #f3f4f6;
}

.share-dialog-close {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  border-radius: 6px;
  transition: all 0.15s;
}

.share-dialog-close:hover {
  background: #1f1f1f;
  color: #f3f4f6;
}

.share-dialog-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

/* Share Type */
.share-type-section {
  margin-bottom: 20px;
}

.share-type-label {
  font-size: 13px;
  color: #9ca3af;
  margin-bottom: 10px;
  font-weight: 500;
}

.share-type-options {
  display: flex;
  gap: 8px;
}

.share-type-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 12px;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  color: #9ca3af;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.share-type-btn:hover {
  border-color: #404040;
  color: #d1d5db;
}

.share-type-btn.active {
  background: rgba(96, 165, 250, 0.1);
  border-color: rgba(96, 165, 250, 0.4);
  color: #60a5fa;
}

/* Disabled State */
.share-disabled-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 20px;
  text-align: center;
}

.share-disabled-hint p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.share-disabled-sub {
  font-size: 12px !important;
  margin-top: 4px !important;
  color: #4b5563 !important;
}

/* Internal Sharing */
.share-internal-section {
  margin-top: 4px;
}

.user-search-box {
  position: relative;
  display: flex;
  align-items: center;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  padding: 0 12px;
  transition: border-color 0.2s;
}

.user-search-box:focus-within {
  border-color: rgba(96, 165, 250, 0.4);
}

.search-icon {
  color: #6b7280;
  flex-shrink: 0;
}

.user-search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #f3f4f6;
  font-size: 13px;
  padding: 10px 8px;
}

.user-search-input::placeholder {
  color: #4b5563;
}

.search-loading {
  color: #60a5fa;
}

.user-search-results {
  margin-top: 8px;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  background: #1a1a1a;
  max-height: 180px;
  overflow-y: auto;
}

.user-result-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.user-result-item:hover {
  background: #222222;
}

.user-result-item:not(:last-child) {
  border-bottom: 1px solid #1f1f1f;
}

.user-result-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 10px;
  flex-shrink: 0;
  background: #2a2a2a;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-result-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-avatar-fallback {
  font-size: 13px;
  color: #9ca3af;
  font-weight: 600;
}

.user-result-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.user-result-name {
  font-size: 13px;
  color: #f3f4f6;
  font-weight: 500;
}

.user-result-email {
  font-size: 11px;
  color: #6b7280;
}

.user-add-icon {
  color: #60a5fa;
  flex-shrink: 0;
}

.selected-users-section {
  margin-top: 12px;
}

.selected-users-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.selected-users-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.selected-user-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(96, 165, 250, 0.1);
  border: 1px solid rgba(96, 165, 250, 0.2);
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 12px;
  color: #60a5fa;
}

.selected-user-remove {
  background: none;
  border: none;
  color: #60a5fa;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  opacity: 0.6;
  transition: opacity 0.15s;
}

.selected-user-remove:hover {
  opacity: 1;
}

/* Public Sharing */
.share-public-section {
  margin-top: 4px;
}

.password-section {
  margin-bottom: 16px;
}

.password-label {
  font-size: 13px;
  color: #9ca3af;
  margin-bottom: 8px;
  font-weight: 500;
}

.password-optional {
  color: #4b5563;
  font-weight: 400;
}

.password-input-row {
  display: flex;
  align-items: center;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  padding: 0 12px;
  transition: border-color 0.2s;
}

.password-input-row:focus-within {
  border-color: rgba(96, 165, 250, 0.4);
}

.password-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #f3f4f6;
  font-size: 13px;
  padding: 10px 0;
}

.password-input::placeholder {
  color: #4b5563;
}

.password-toggle {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
}

.password-toggle:hover {
  color: #d1d5db;
}

.password-hint {
  font-size: 11px;
  color: #4b5563;
  margin: 6px 0 0;
}

/* Share Link */
.share-link-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #1f1f1f;
}

.share-link-label {
  font-size: 13px;
  color: #9ca3af;
  margin-bottom: 8px;
  font-weight: 500;
}

.share-link-box {
  display: flex;
  align-items: center;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  overflow: hidden;
}

.share-link-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #d1d5db;
  font-size: 12px;
  padding: 10px 12px;
  min-width: 0;
}

.share-copy-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 10px 14px;
  background: #222222;
  border: none;
  border-left: 1px solid #2a2a2a;
  color: #d1d5db;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
  white-space: nowrap;
}

.share-copy-btn:hover {
  background: #2a2a2a;
}

.share-copy-btn.small {
  padding: 4px 6px;
  border: none;
  border-radius: 4px;
}

.share-password-display {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 12px;
}

.share-password-label {
  color: #6b7280;
}

.share-password-value {
  color: #f3f4f6;
  font-family: monospace;
  letter-spacing: 1px;
}

/* Share Platforms */
.share-platforms-section {
  margin-top: 20px;
}

.share-platforms-label {
  font-size: 13px;
  color: #9ca3af;
  margin-bottom: 10px;
  font-weight: 500;
}

.share-platforms-list {
  display: flex;
  gap: 10px;
}

.platform-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 10px 14px;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  color: #9ca3af;
  font-size: 11px;
  flex: 1;
}

.platform-btn:hover {
  border-color: #404040;
  transform: translateY(-1px);
}

.platform-btn.wechat:hover {
  color: #07c160;
  border-color: rgba(7, 193, 96, 0.3);
}

.platform-btn.weibo:hover {
  color: #e6162d;
  border-color: rgba(230, 22, 45, 0.3);
}

.platform-btn.qq:hover {
  color: #12b7f5;
  border-color: rgba(18, 183, 245, 0.3);
}

.platform-btn.dingtalk:hover {
  color: #3296fa;
  border-color: rgba(50, 150, 250, 0.3);
}

.platform-btn.link:hover {
  color: #a78bfa;
  border-color: rgba(167, 139, 250, 0.3);
}

/* Footer */
.share-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 14px 20px;
  border-top: 1px solid #2a2a2a;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
