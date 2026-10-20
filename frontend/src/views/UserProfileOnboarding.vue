<template>
  <div class="profile-page page-shell invert-on-light">
    <div class="page-header glass-card">
      <h1 class="apple-title">欢迎加入，先完善你的教学画像</h1>
      <p class="apple-subtitle">这将帮助AI更有针对性地生成PPT内容与风格</p>
    </div>

    <el-card class="profile-card section-shell">
      <el-steps :active="step" finish-status="success" simple>
        <el-step title="基础信息" />
        <el-step title="学科课程" />
        <el-step title="授课风格" />
      </el-steps>

      <div class="step-body" v-if="step === 0">
        <el-form label-position="top">
          <el-form-item label="1. 教师性别">
            <el-radio-group v-model="form.teacher_gender">
              <el-radio value="male">男</el-radio>
              <el-radio value="female">女</el-radio>
              <el-radio value="other">其他</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="2. 教师年龄">
            <el-input-number v-model="form.teacher_age" :min="18" :max="100" />
          </el-form-item>
          <el-form-item label="3. 所在学校">
            <el-input
              v-model="form.school_name"
              placeholder="请输入所在学校名称"
              clearable
            />
          </el-form-item>
        </el-form>
      </div>

      <div class="step-body" v-if="step === 1">
        <el-form label-position="top">
          <el-form-item label="4. 学科门类">
            <el-radio-group v-model="form.subject_category">
              <el-radio v-for="item in subjectOptions" :key="item" :value="item">{{ item }}</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="5. 具体课程（多选）">
            <el-select v-model="form.courses" multiple filterable allow-create default-first-option style="width: 100%">
              <el-option v-for="item in courseOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <div class="step-body" v-if="step === 2">
        <el-form label-position="top">
          <el-form-item label="6. 授课风格（多选）">
            <el-checkbox-group v-model="form.teaching_styles">
              <el-checkbox v-for="item in styleOptions" :key="item" :label="item">{{ item }}</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </div>

      <div class="step-actions">
        <el-button text :disabled="step === 0" @click="step--">上一步</el-button>
        <el-button v-if="step < 2" type="primary" @click="step++">下一步</el-button>
        <el-button v-else type="primary" :loading="saving" @click="submitProfile">完成并进入系统</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import authService from '@/services/auth'

const router = useRouter()
const saving = ref(false)
const step = ref(0)

const form = ref({
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

const submitProfile = async () => {
  saving.value = true
  try {
    await authService.updateProfile(form.value)
    ElMessage.success('画像信息已保存')
    router.push('/dashboard')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 980px;
  margin: 0 auto;
}

.profile-card {
  margin-top: 18px;
}

.step-body {
  margin-top: 24px;
  min-height: 260px;
}

.step-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 14px;
}
</style>
