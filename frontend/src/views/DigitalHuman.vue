<template>
  <div class="digital-human invert-on-light">
    <div class="header">
      <h1>数字人演讲</h1>
      <div class="header-right">
        <UiButton variant="ghost" size="sm" @click="handleBack">
          <span>返回</span>
        </UiButton>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧：形象选择 -->
      <div class="avatar-panel">
        <!-- 分类标签 -->
        <div class="avatar-tabs">
          <button
            :class="['avatar-tab', { active: avatarTab === 'builtin' }]"
            @click="avatarTab = 'builtin'"
          >
            <User :size="14" />
            <span>内置模板</span>
          </button>
          <button
            :class="['avatar-tab', { active: avatarTab === 'custom' }]"
            @click="avatarTab = 'custom'"
          >
            <Upload :size="14" />
            <span>自定义形象</span>
          </button>
        </div>

        <!-- 内置模板列表 -->
        <div v-if="avatarTab === 'builtin'" class="avatar-list">
          <div
            v-for="(item, idx) in builtinAvatars"
            :key="idx"
            :class="['avatar-card', { selected: selectedAvatar?.id === item.id }]"
            @click="selectAvatar(item)"
          >
            <div class="avatar-card-img">
              <User :size="28" />
            </div>
            <div class="avatar-card-info">
              <span class="avatar-card-name">{{ item.name }}</span>
              <span class="avatar-card-desc">{{ item.desc }}</span>
            </div>
            <div v-if="selectedAvatar?.id === item.id" class="avatar-card-check">
              <CheckCircle2 :size="16" />
            </div>
          </div>
        </div>

        <!-- 自定义形象上传 -->
        <div v-else class="custom-upload-area">
          <div class="upload-section">
            <label class="upload-label">
              <User :size="16" />
              <span>半身照</span>
              <span class="required">*</span>
            </label>
            <el-upload
              :auto-upload="false"
              :show-file-list="false"
              :limit="1"
              accept=".png,.jpg,.jpeg,.gif,.webp,.bmp"
              :on-change="(f) => handleFileChange('photo', f)"
              :on-exceed="handleExceed"
              drag
            >
              <div class="mini-drag-area">
                <Upload :size="16" />
                <span>{{ files.photo ? files.photo.name : '拖拽或点击上传半身照' }}</span>
              </div>
            </el-upload>
          </div>

          <div class="upload-section">
            <label class="upload-label">
              <Mic :size="16" />
              <span>语音文件</span>
              <span class="required">*</span>
            </label>
            <el-upload
              :auto-upload="false"
              :show-file-list="false"
              :limit="1"
              accept=".mp3,.wav,.m4a,.ogg,.flac,.aac"
              :on-change="(f) => handleFileChange('audio', f)"
              :on-exceed="handleExceed"
              drag
            >
              <div class="mini-drag-area">
                <Upload :size="16" />
                <span>{{ files.audio ? files.audio.name : '拖拽或点击上传语音' }}</span>
              </div>
            </el-upload>
          </div>
        </div>

        <!-- PPT上传（始终显示） -->
        <div class="upload-section ppt-section">
          <label class="upload-label">
            <FileText :size="16" />
            <span>PPT文件</span>
            <span class="required">*</span>
          </label>
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            :limit="1"
            accept=".pptx,.ppt"
            :on-change="(f) => handleFileChange('ppt', f)"
            :on-exceed="handleExceed"
            drag
          >
            <div class="mini-drag-area">
              <Upload :size="16" />
              <span>{{ files.ppt ? files.ppt.name : '拖拽或点击上传PPT' }}</span>
            </div>
          </el-upload>
        </div>

        <!-- 开始生成按钮 -->
        <StarButton
          text="开始生成演讲稿"
          :disabled="!canStartScript"
          @click="startGenerateScript"
        />
      </div>

      <!-- 右侧：进度与预览区 -->
      <div class="progress-panel">
        <!-- 演讲稿生成进度 -->
        <div v-if="scriptPhase !== 'idle'" class="phase-section">
          <h2 class="panel-title">
            <FileText :size="16" />
            <span>{{ scriptPhase === 'generating' ? '正在生成演讲稿...' : '演讲稿生成完成' }}</span>
          </h2>

          <!-- 进度条（生成中显示） -->
          <div v-if="scriptPhase === 'generating'" class="progress-bar-wrap">
            <div class="progress-bar">
              <div class="progress-bar-fill" :style="{ width: scriptProgress + '%' }"></div>
            </div>
            <span class="progress-text">{{ scriptProgress }}%</span>
          </div>

          <!-- 步骤条（生成中显示） -->
          <div v-if="scriptPhase === 'generating'" class="steps-list">
            <div
              v-for="(step, idx) in scriptSteps"
              :key="idx"
              class="step-item"
              :class="step.status"
            >
              <div class="step-icon">
                <CheckCircle2 v-if="step.status === 'completed'" :size="16" />
                <Loader2 v-else-if="step.status === 'in-progress'" :size="16" class="spin" />
                <Circle v-else :size="16" />
              </div>
              <span class="step-text">{{ step.text }}</span>
            </div>
          </div>

          <!-- 日志（生成中显示） -->
          <div v-if="scriptPhase === 'generating'" ref="scriptLogRef" class="log-box">
            <div v-for="(log, idx) in scriptLogs" :key="idx" class="log-line">
              <span class="log-time">[{{ log.time }}]</span>
              <span class="log-msg">{{ log.msg }}</span>
            </div>
          </div>

          <!-- 完成后操作 -->
          <div v-if="scriptPhase === 'done' && videoPhase === 'idle'" class="phase-actions">
            <StarButton text="确认并生成讲解视频" @click="startGenerateVideo" />
          </div>

          <!-- 内嵌演讲稿预览（点击生成视频后隐藏） -->
          <div v-if="scriptPhase === 'done' && videoPhase === 'idle'" class="inline-preview">
            <div v-if="previewLoading" class="preview-loading">
              <Loader2 :size="32" class="spin" />
              <span>加载预览中...</span>
            </div>
            <div v-else-if="previewError" class="error-container">
              <p>{{ previewError }}</p>
            </div>
            <div v-else class="editor-container">
              <div id="script-onlyoffice-editor"></div>
            </div>
          </div>
        </div>

        <!-- 视频生成进度 -->
        <div v-if="videoPhase !== 'idle'" class="phase-section">
          <h2 class="panel-title">
            <Video :size="16" />
            <span>{{ videoPhase === 'generating' ? '正在生成讲解视频...' : '讲解视频生成完成' }}</span>
          </h2>

          <!-- 进度条（仅生成中显示） -->
          <div v-if="videoPhase === 'generating'" class="progress-bar-wrap">
            <div class="progress-bar">
              <div class="progress-bar-fill video-fill" :style="{ width: videoProgress + '%' }"></div>
            </div>
            <span class="progress-text">{{ videoProgress }}%</span>
          </div>

          <!-- 步骤条（仅生成中显示） -->
          <div v-if="videoPhase === 'generating'" class="steps-list">
            <div
              v-for="(step, idx) in videoSteps"
              :key="idx"
              class="step-item"
              :class="step.status"
            >
              <div class="step-icon">
                <CheckCircle2 v-if="step.status === 'completed'" :size="16" />
                <Loader2 v-else-if="step.status === 'in-progress'" :size="16" class="spin" />
                <Circle v-else :size="16" />
              </div>
              <span class="step-text">{{ step.text }}</span>
            </div>
          </div>

          <!-- 日志（仅生成中显示） -->
          <div v-if="videoPhase === 'generating'" ref="videoLogRef" class="log-box">
            <div v-for="(log, idx) in videoLogs" :key="idx" class="log-line">
              <span class="log-time">[{{ log.time }}]</span>
              <span class="log-msg">{{ log.msg }}</span>
            </div>
          </div>

          <!-- 视频预览 -->
          <div v-if="videoPhase === 'done' && videoUrl" class="video-preview">
            <video
              ref="videoPlayerRef"
              controls
              controlslist="nodownload"
              autoplay
              muted
              playsinline
              preload="auto"
              class="video-player"
              @loadeddata="onVideoLoaded"
              @error="handleVideoError"
            >
              <source :src="videoUrl" type="video/mp4">
              您的浏览器不支持视频播放
            </video>
            <div v-if="videoError" class="video-error-tip">
              <p>{{ videoError }}</p>
            </div>
          </div>

          <!-- 完成后操作 -->
          <div v-if="videoPhase === 'done'" class="phase-actions">
            <StarButton text="下载视频" @click="downloadVideo" />
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="scriptPhase === 'idle' && videoPhase === 'idle'" class="empty-state">
          <User :size="48" class="empty-icon" />
          <p>请上传素材后点击"开始生成演讲稿"</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/services/api'
import {
  User, Mic, FileText, Upload, Play, CheckCircle2, Circle,
  Loader2, Eye, Video, Download
} from 'lucide-vue-next'
import StarButton from '@/components/ui/StarButton.vue'

const router = useRouter()

// ── 形象选择 ──
const avatarTab = ref('builtin')
const selectedAvatar = ref(null)

const builtinAvatars = [
  { id: 'female_teacher', name: '女教师', desc: '专业知性，适合课程讲解', gender: 'female', style: 'professional' },
  { id: 'male_teacher', name: '男教师', desc: '沉稳大气，适合学术报告', gender: 'male', style: 'professional' },
  { id: 'female_student', name: '女学生', desc: '青春活泼，适合学习分享', gender: 'female', style: 'casual' },
  { id: 'male_student', name: '男学生', desc: '阳光开朗，适合课堂演示', gender: 'male', style: 'casual' },
  { id: 'female_host', name: '女主持人', desc: '优雅大方，适合正式场合', gender: 'female', style: 'formal' },
  { id: 'male_host', name: '男主持人', desc: '稳重得体，适合会议主持', gender: 'male', style: 'formal' },
]

const selectAvatar = (item) => {
  selectedAvatar.value = item
  // 选择内置模板时清空自定义上传
  files.value.photo = null
  files.value.audio = null
}

// ── 文件上传 ──
const files = ref({ photo: null, audio: null, ppt: null })

const handleFileChange = (type, file) => {
  files.value[type] = file.raw
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const canStartScript = computed(() => {
  if (!files.value.ppt) return false
  // 内置模板：只需选模板+PPT
  if (avatarTab.value === 'builtin' && selectedAvatar.value) return true
  // 自定义形象：需要半身照+语音+PPT
  if (avatarTab.value === 'custom' && files.value.photo && files.value.audio) return true
  return false
})

// ── 演讲稿生成 ──
const scriptPhase = ref('idle') // idle | generating | done
const scriptProgress = ref(0)
const scriptSteps = ref([])
const scriptLogs = ref([])
const scriptLogRef = ref(null)
const scriptTaskId = ref(null)

const startGenerateScript = async () => {
  // 上传文件
  try {
    const formData = new FormData()
    formData.append('photo', files.value.photo)
    formData.append('audio', files.value.audio)
    formData.append('ppt', files.value.ppt)
    await api.post('/digital-human/upload/', formData)
  } catch (e) {
    ElMessage.error('文件上传失败')
    return
  }

  // 开始生成
  scriptPhase.value = 'generating'
  scriptProgress.value = 0
  scriptSteps.value = []
  scriptLogs.value = []

  try {
    const res = await api.post('/digital-human/generate-script/', {
      ppt_name: files.value.ppt.name
    })
    scriptTaskId.value = res.data.task_id
    pollScriptTask()
  } catch (e) {
    ElMessage.error('启动生成失败')
    scriptPhase.value = 'idle'
  }
}

const pollScriptTask = () => {
  if (!scriptTaskId.value) return
  const timer = setInterval(async () => {
    try {
      const res = await api.get(`/digital-human/task/${scriptTaskId.value}/`)
      const data = res.data
      scriptProgress.value = data.progress
      scriptSteps.value = data.steps
      scriptLogs.value = data.logs

      // 自动滚动日志
      nextTick(() => {
        if (scriptLogRef.value) {
          scriptLogRef.value.scrollTop = scriptLogRef.value.scrollHeight
        }
      })

      if (data.status === 'completed') {
        clearInterval(timer)
        scriptPhase.value = 'done'
        ElMessage.success('演讲稿生成完成！')
        // 自动加载预览
        previewScript()
      } else if (data.status === 'failed') {
        clearInterval(timer)
        scriptPhase.value = 'idle'
        ElMessage.error('生成失败: ' + (data.error || '未知错误'))
      }
    } catch (e) {
      clearInterval(timer)
      scriptPhase.value = 'idle'
    }
  }, 1000)
}

// ── 视频生成 ──
const videoPhase = ref('idle')
const videoProgress = ref(0)
const videoSteps = ref([])
const videoLogs = ref([])
const videoLogRef = ref(null)
const videoTaskId = ref(null)
const videoUrl = ref(null)
const videoError = ref(null)
const videoPlayerRef = ref(null)

const onVideoLoaded = () => {
  // 视频数据加载完成，尝试取消静音并播放
  const video = videoPlayerRef.value
  if (video) {
    video.muted = false
    video.play().catch(() => {
      // 浏览器阻止了有声自动播放，保持静音播放
      video.muted = true
      video.play().catch(() => {})
    })
  }
}

const handleVideoError = (e) => {
  const video = e.target
  let msg = '视频加载失败'
  if (video.error) {
    switch (video.error.code) {
      case MediaError.MEDIA_ERR_ABORTED:
        msg = '视频加载被中止'
        break
      case MediaError.MEDIA_ERR_NETWORK:
        msg = '网络错误导致视频加载失败'
        break
      case MediaError.MEDIA_ERR_DECODE:
        msg = '视频解码失败，文件可能已损坏'
        break
      case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
        msg = '视频格式不支持或地址无效'
        break
    }
  }
  videoError.value = msg
  console.error('Video error:', msg, video.error)
}

const startGenerateVideo = async () => {
  videoPhase.value = 'generating'
  videoProgress.value = 0
  videoSteps.value = []
  videoLogs.value = []
  videoError.value = null

  try {
    const res = await api.post('/digital-human/generate-video/', {
      ppt_name: files.value.ppt.name
    })
    videoTaskId.value = res.data.task_id
    pollVideoTask()
  } catch (e) {
    ElMessage.error('启动视频生成失败')
    videoPhase.value = 'idle'
  }
}

const pollVideoTask = () => {
  if (!videoTaskId.value) return
  const timer = setInterval(async () => {
    try {
      const res = await api.get(`/digital-human/task/${videoTaskId.value}/`)
      const data = res.data
      videoProgress.value = data.progress
      videoSteps.value = data.steps
      videoLogs.value = data.logs

      nextTick(() => {
        if (videoLogRef.value) {
          videoLogRef.value.scrollTop = videoLogRef.value.scrollHeight
        }
      })

      if (data.status === 'completed') {
        clearInterval(timer)
        videoPhase.value = 'done'
        videoUrl.value = data.result?.video_url || null
        ElMessage.success('讲解视频生成完成！')
      } else if (data.status === 'failed') {
        clearInterval(timer)
        videoPhase.value = 'idle'
        videoUrl.value = null
        ElMessage.error('视频生成失败: ' + (data.error || '未知错误'))
      }
    } catch (e) {
      clearInterval(timer)
      videoPhase.value = 'idle'
    }
  }, 1000)
}

// ── 演讲稿预览 ──
const previewLoading = ref(false)
const previewError = ref(null)
let scriptDocEditor = null

const previewScript = async () => {
  previewLoading.value = true
  previewError.value = null

  try {
    const res = await api.get(`/digital-human/preview/${scriptTaskId.value}/`)
    const cfg = res.data

    await nextTick()
    setTimeout(() => initScriptEditor(cfg), 300)
  } catch (e) {
    previewError.value = '加载预览失败'
    ElMessage.error(previewError.value)
  } finally {
    previewLoading.value = false
  }
}

const initScriptEditor = (cfg) => {
  // 销毁旧编辑器
  if (scriptDocEditor) {
    try { scriptDocEditor.destroyEditor() } catch (e) {}
    scriptDocEditor = null
  }

  const onlyofficeUrl = cfg.onlyoffice_url || 'http://localhost:80'
  const existingScript = document.querySelector('script[src*="api/documents/api.js"]')

  const doInit = () => {
    const doc = cfg.document || {
      fileType: 'docx',
      key: cfg.key + '_' + Date.now(),
      title: cfg.file_name,
      url: cfg.file_url,
      permissions: { edit: true, download: true, print: true }
    }

    const editorCfg = cfg.editor_config || {
      lang: 'zh-CN',
      mode: 'edit',
      user: { id: 'user', name: 'User' }
    }

    const config = {
      type: 'desktop',
      documentType: 'word',
      document: doc,
      editorConfig: editorCfg,
      width: '100%',
      height: '100%',
      containerId: 'script-onlyoffice-editor'
    }

    if (cfg.token) config.token = cfg.token

    if (window.DocsAPI) {
      scriptDocEditor = new window.DocsAPI.DocEditor('script-onlyoffice-editor', config)
    } else {
      previewError.value = 'OnlyOffice 未加载'
    }
  }

  if (existingScript) {
    doInit()
  } else {
    const script = document.createElement('script')
    script.src = `${onlyofficeUrl}/web-apps/apps/api/documents/api.js`
    script.onload = doInit
    script.onerror = () => { previewError.value = '无法加载编辑器' }
    document.head.appendChild(script)
  }
}

// ── 下载视频 ──
const downloadVideo = async () => {
  try {
    const res = await api.get(`/digital-human/file/video/${videoTaskId.value}/`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = '讲解视频.mp4'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

const handleBack = () => router.back()

onUnmounted(() => {
  if (scriptDocEditor) {
    try { scriptDocEditor.destroyEditor() } catch (e) {}
  }
})
</script>

<style scoped>
.digital-human {
  min-height: 100vh;
  background: #0a0a0a;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #111111;
  border-bottom: 1px solid #2a2a2a;
}

.header h1 {
  margin: 0;
  font-size: 22px;
  color: #f3f4f6;
  font-weight: 700;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-content {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 20px;
  padding: 20px 24px;
  min-height: calc(100vh - 65px);
}

/* ── 形象选择面板 ── */
.avatar-panel {
  background: #121212;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
  max-height: calc(100vh - 105px);
}

.avatar-tabs {
  display: flex;
  gap: 6px;
  background: #1a1a1a;
  border-radius: 8px;
  padding: 3px;
}

.avatar-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: rgba(255, 255, 255, 0.45);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.avatar-tab:hover {
  color: rgba(255, 255, 255, 0.7);
}

.avatar-tab.active {
  background: #2a2a2e;
  color: #f3f4f6;
  font-weight: 500;
}

/* ── 内置模板列表 ── */
.avatar-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.avatar-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.avatar-card:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
}

.avatar-card.selected {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.3);
}

.avatar-card-img {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: #1e1e1e;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

.avatar-card.selected .avatar-card-img {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
}

.avatar-card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.avatar-card-name {
  font-size: 14px;
  color: #f3f4f6;
  font-weight: 500;
}

.avatar-card-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.avatar-card-check {
  flex-shrink: 0;
  color: #3b82f6;
}

/* ── 自定义上传区 ── */
.custom-upload-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ppt-section {
  margin-top: 4px;
  padding-top: 14px;
  border-top: 1px solid #2a2a2a;
}

.panel-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #f3f4f6;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.upload-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  color: #d1d5db;
}

.required {
  color: #ef4444;
}

.mini-drag-area {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.5);
  background: #2a2a2a;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.mini-drag-area :deep(.el-upload-dragger),
:deep(.el-upload-dragger) {
  padding: 0;
  border: none;
  background: transparent;
  min-height: auto;
  border-radius: 6px;
}

/* ── 进度面板 ── */
.progress-panel {
  background: #121212;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  padding: 20px;
  overflow-y: auto;
}

.phase-section {
  margin-bottom: 24px;
}

.phase-section:last-child {
  margin-bottom: 0;
}

/* ── 进度条 ── */
.progress-bar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #1e1e1e;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.video-fill {
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
}

.progress-text {
  font-size: 13px;
  color: #9ca3af;
  min-width: 36px;
  text-align: right;
}

/* ── 步骤条 ── */
.steps-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #6b7280;
  transition: color 0.3s;
}

.step-item.in-progress {
  color: #60a5fa;
}

.step-item.completed {
  color: #34d399;
}

.step-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ── 日志 ── */
.log-box {
  background: #0a0a0a;
  border: 1px solid #1e1e1e;
  border-radius: 8px;
  padding: 12px;
  height: 200px;
  overflow-y: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  margin-bottom: 16px;
}

.log-line {
  display: flex;
  gap: 8px;
  line-height: 1.6;
}

.log-time {
  color: #6b7280;
  flex-shrink: 0;
}

.log-msg {
  color: #d1d5db;
}

/* ── 操作按钮 ── */
.phase-actions {
  display: flex;
  gap: 10px;
}

/* ── 内嵌预览 ── */
.inline-preview {
  margin-top: 16px;
  border-top: 1px solid #2a2a2a;
  padding-top: 16px;
}

.editor-container {
  height: 75vh;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
}

.preview-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 75vh;
  gap: 12px;
  color: #6b7280;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 75vh;
  color: #ef4444;
}

/* ── 空状态 ── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: #4b5563;
}

.empty-icon {
  opacity: 0.3;
}

.empty-state p {
  font-size: 14px;
}

/* ── 视频预览 ── */
.video-preview {
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
  background: #000;
}

.video-player {
  width: 100%;
  aspect-ratio: 16 / 9;
  max-height: 70vh;
  border-radius: 8px;
  outline: none;
  background: #000;
  object-fit: contain;
}

.video-error-tip {
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border-top: 1px solid rgba(239, 68, 68, 0.2);
}

.video-error-tip p {
  margin: 0;
  color: #ef4444;
  font-size: 13px;
}
</style>
