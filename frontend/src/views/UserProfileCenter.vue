<template>
  <div :class="['profile-page page-shell invert-on-light', { 'in-modal': inModal }]">
    <div class="profile-card">
      <div class="profile-gradient" />

      <div class="profile-avatar-wrap">
        <img :src="profileImage" alt="用户头像" class="profile-avatar" />
        <button type="button" class="avatar-upload-btn" @click="handleThumbnailClick" aria-label="更换头像">
          <ImagePlus :size="16" />
        </button>
        <input ref="fileInputRef" type="file" accept="image/*" class="hidden-input" @change="handleFileChange" />
      </div>

      <div class="profile-body">
        <div class="profile-head-row">
          <div>
            <h1 class="profile-title">编辑教师画像</h1>
            <p class="profile-subtitle">完善信息后，系统将更精准生成符合你授课特征的PPT</p>
          </div>
        </div>

        <el-form label-position="top" class="profile-form-grid">
          <div class="grid-row two-col">
            <el-form-item label="姓名/昵称">
              <UiInput v-model="form.nickname" placeholder="请输入姓名或昵称" maxlength="30" />
            </el-form-item>
            <el-form-item label="学科方向">
              <UiCombobox
                v-model="form.subject_category"
                :options="subjectOptions"
                allow-create
                clearable
                placeholder="可选择或输入学科方向"
              />
            </el-form-item>
          </div>

          <div class="grid-row two-col">
            <el-form-item label="邮箱账号">
              <UiInput :model-value="userEmail" readonly placeholder="邮箱账号" />
            </el-form-item>
            <el-form-item label="头像链接（可选）">
              <UiInput v-model="form.avatar_url" placeholder="https://example.com/avatar.png" />
            </el-form-item>
          </div>

          <div class="grid-row two-col">
            <el-form-item label="学校/单位">
              <UiInput
                v-model="form.school_name"
                placeholder="请输入所在学校名称"
                clearable
              />
            </el-form-item>
            <el-form-item label="年龄">
              <UiNumberInput v-model="form.teacher_age" :min="18" :max="100" />
            </el-form-item>
          </div>

          <div class="grid-row two-col row-courses-style">
            <el-form-item label="任课课程">
              <UiCombobox
                v-model="form.courses"
                :options="courseOptions"
                multiple
                allow-create
                clearable
                placeholder="可多选或输入课程"
              />
            </el-form-item>
            <el-form-item label="授课风格" class="teaching-style-item">
              <UiCombobox
                class="teaching-style-combobox"
                v-model="form.teaching_styles"
                :options="styleOptions"
                multiple
                allow-create
                clearable
                placeholder="可多选或输入风格"
              />
            </el-form-item>
          </div>

          <el-form-item label="性别">
            <UiRadioGroup v-model="form.teacher_gender" :options="genderOptions" />
          </el-form-item>

          <el-form-item label="个人简介">
            <UiTextarea
              :model-value="about"
              :maxlength="maxLength"
              :rows="4"
              placeholder="请输入个人简介（用于辅助生成更贴合的内容）"
              @update:model-value="handleAboutChange"
            />
            <p class="char-counter">还可输入 {{ remainingChars }} 字</p>
          </el-form-item>
        </el-form>
      </div>

      <div class="profile-footer">
        <UiButton variant="outline" @click="handleBack">取消</UiButton>
        <UiButton :loading="saving" @click="saveProfile">保存修改</UiButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ImagePlus } from 'lucide-vue-next'
import UiButton from '@/components/ui/shadcn/Button.vue'
import UiInput from '@/components/ui/shadcn/Input.vue'
import UiTextarea from '@/components/ui/shadcn/Textarea.vue'
import UiCombobox from '@/components/ui/shadcn/Combobox.vue'
import UiRadioGroup from '@/components/ui/shadcn/RadioGroup.vue'
import UiNumberInput from '@/components/ui/shadcn/NumberInput.vue'
import authService from '@/services/auth'
import { useAuthStore } from '@/store/modules/auth'

const router = useRouter()
const authStore = useAuthStore()
const saving = ref(false)

const props = withDefaults(defineProps<{
  inModal?: boolean
}>(), {
  inModal: false
})

const emit = defineEmits<{
  (e: 'close'): void
}>()

const maxLength = 180
const about = ref('')
const remainingChars = computed(() => maxLength - about.value.length)
const userEmail = computed(() => authStore.currentUser?.email || '')

const previewUrl = ref('')
const fileInputRef = ref(null)

const form = ref({
  nickname: '',
  avatar_url: '',
  teacher_gender: '',
  teacher_age: null,
  school_name: 'XX大学',
  subject_category: '',
  courses: [],
  teaching_styles: []
})

const subjectOptions = ['理学', '工学', '文学', '教育学', '医学', '经济学', '管理学', '艺术学']
const courseOptions = ['高等数学', '线性代数', '大学英语', '数据结构', '计算机网络', '市场营销', '中国近现代史']
const styleOptions = ['多理论讲述', '多小组互动', '案例驱动', '项目式学习', '讨论式教学', '实操演示']
const genderOptions = [
  { label: '男', value: 'male' },
  { label: '女', value: 'female' },
  { label: '其他', value: 'other' }
]

const getBackendOrigin = () => {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'
  return apiBase.replace(/\/api\/?$/, '')
}

const profileImage = computed(() => {
  if (previewUrl.value) return previewUrl.value
  const avatarUrl = form.value.avatar_url
  if (!avatarUrl) return 'https://github.com/shadcn.png'
  if (avatarUrl.startsWith('/')) return `${getBackendOrigin()}${avatarUrl}`
  return avatarUrl
})

const handleThumbnailClick = () => {
  fileInputRef.value?.click()
}

const handleFileChange = async (event) => {
  const target = event.target
  const file = target.files?.[0]
  if (!file) return

  // 验证文件类型
  const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持 PNG, JPG, JPEG, GIF, WEBP 格式的图片')
    return
  }

  // 验证文件大小 (最大 5MB)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('图片大小不能超过 5MB')
    return
  }

  // 显示本地预览
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = URL.createObjectURL(file)

  // 上传到服务器
  try {
    const res = await authService.uploadAvatar(file)
    const { avatar_url } = res.data
    form.value.avatar_url = avatar_url
    ElMessage.success('头像上传成功')
    
    // 重新获取用户信息以更新 authStore
    await authStore.fetchCurrentUser()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '头像上传失败')
    // 上传失败,清除预览
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value)
      previewUrl.value = ''
    }
  }
  
  // 清空 input,允许重复选择同一文件
  target.value = ''
}

const handleAboutChange = (value) => {
  about.value = String(value || '').slice(0, maxLength)
}

const loadProfile = async () => {
  try {
    const res = await authService.getProfile()
    const profile = res.data.profile || {}

    // 兼容历史数据：后端可能存在字符串或空值，统一转为数组，避免多选组件异常
    const normalizeArray = (value) => {
      if (Array.isArray(value)) return value
      if (typeof value === 'string' && value.trim()) {
        return value.split(/[，,、;；\n]+/).map((item) => item.trim()).filter(Boolean)
      }
      return []
    }

    Object.assign(form.value, {
      ...profile,
      courses: normalizeArray(profile.courses),
      teaching_styles: normalizeArray(profile.teaching_styles)
    })
  } catch {
    // ignore
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    // 仅提交后端已使用的画像字段
    const payload = {
      nickname: form.value.nickname,
      avatar_url: form.value.avatar_url,
      teacher_gender: form.value.teacher_gender,
      teacher_age: form.value.teacher_age,
      school_name: form.value.school_name,
      subject_category: form.value.subject_category,
      courses: form.value.courses,
      teaching_styles: form.value.teaching_styles
    }

    await authService.updateProfile(payload)
    ElMessage.success('用户信息已保存')
    if (props.inModal) {
      emit('close')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleBack = () => {
  if (props.inModal) {
    emit('close')
    return
  }
  router.back()
}

onBeforeUnmount(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})

onMounted(loadProfile)
</script>

<style scoped>
.profile-page {
  max-width: 980px;
  margin: 0 auto;
}

.profile-page.in-modal {
  max-width: 760px;
}

.profile-card {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  overflow: hidden;
  background: #0b0b0d;
}

.profile-page.in-modal .profile-card {
  border: none;
  background: #fff;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
}

.profile-gradient {
  height: 144px;
  background: radial-gradient(circle, rgba(238, 174, 202, 1) 0%, rgba(148, 187, 233, 1) 100%);
}

.profile-avatar-wrap {
  margin-top: -56px;
  display: flex;
  justify-content: center;
  position: relative;
}

.profile-avatar {
  width: 96px;
  height: 96px;
  border-radius: 9999px;
  border: 4px solid #0b0b0d;
  object-fit: cover;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  background: #111;
}

.profile-page.in-modal .profile-avatar {
  border-color: #f3f4f6;
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.14);
}

.avatar-upload-btn {
  position: absolute;
  right: calc(50% - 48px);
  bottom: 0;
  transform: translate(35%, 15%);
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: rgba(0, 0, 0, 0.65);
  cursor: pointer;
}

.avatar-upload-btn:hover {
  background: rgba(0, 0, 0, 0.82);
}

.hidden-input {
  display: none;
}

.profile-body {
  padding: 20px 24px;
}

.profile-head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.profile-title {
  margin: 0;
  font-size: 20px;
  color: #f5f5f5;
}

.profile-page.in-modal .profile-title {
  color: #1f2937;
}

.profile-subtitle {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.62);
  font-size: 13px;
}

.profile-page.in-modal .profile-subtitle {
  color: #6b7280;
}

.profile-form-grid {
  margin-top: 10px;
}

.grid-row {
  display: grid;
  gap: 12px;
}

.two-col {
  grid-template-columns: 1fr 1fr;
}

.row-courses-style {
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
}

.row-courses-style > * {
  min-width: 0;
}

.teaching-style-item :deep(.shadcn-combobox) {
  margin-right: 8px;
}

:deep(.teaching-style-combobox .chip),
:deep(.teaching-style-combobox .option) {
  white-space: nowrap;
}

:deep(.teaching-style-combobox .option) {
  overflow: hidden;
  text-overflow: ellipsis;
}

.char-counter {
  margin: 6px 2px 0;
  text-align: right;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.48);
}

.profile-page.in-modal .char-counter {
  color: #9ca3af;
}

.profile-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  background: #0b0b0d;
  padding: 16px 24px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.profile-page.in-modal .profile-footer {
  border-top: 1px solid #e5e7eb;
  background: #fff;
}

:deep(.profile-modal-popper) {
  z-index: 3600 !important;
}

@media (max-width: 768px) {
  .two-col {
    grid-template-columns: 1fr;
  }

  .profile-head-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
