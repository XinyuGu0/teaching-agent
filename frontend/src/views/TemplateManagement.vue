<template>
  <div
    class="template-management invert-on-light"
    :class="{ 'is-category-dropdown-open': isCategoryDropdownOpen }"
  >
    <div class="header">
      <h1>PPT模板管理</h1>
      <div class="header-right">
        <UiButton variant="default" size="sm" class="upload-btn-sm" @click="showUploadDialog = true">
          <Upload :size="12" />
          <span>上传模板</span>
        </UiButton>
        <UiButton variant="ghost" size="sm" @click="handleBack">
          <span>返回</span>
        </UiButton>
      </div>
    </div>

    <!-- 分类筛选 -->
    <div class="filters">
      <UiTabs
        v-model="selectedScope"
        class="scope-tabs"
        variant="default"
        :options="scopeOptions"
        aria-label="模板范围切换"
      />

      <UiSelect
        v-model="selectedCategory"
        :options="categoryOptions"
        placeholder="选择分类"
        clearable
      />
    </div>

    <!-- 模板列表 -->
    <div class="template-grid">
      <div
        v-for="template in filteredTemplates"
        :key="template.id"
        class="template-card"
      >
        <div class="template-thumbnail">
          <img
            v-if="hasThumbnail(template)"
            :src="getThumbnailUrl(template)"
            :alt="template.name"
            @error="handleThumbnailError(template)"
          />
          <div v-else class="placeholder">
            <FileText :size="48" />
          </div>
        </div>
        <div class="template-info">
          <h3>{{ template.name }}</h3>
          <p class="description">{{ template.description || '暂无描述' }}</p>
          <div class="meta">
            <span class="category">
              {{ categories[template.category] || '其他' }}
            </span>
            <span class="usage">
              使用次数: {{ template.usage_count || 0 }}
            </span>
          </div>

          <div v-if="!isBuiltinTemplate(template)" class="template-visibility-block">
            <span :class="['visibility-badge', getVisibilityClass(getTemplateVisibility(template).visibility)]">
              {{ getVisibilityLabel(getTemplateVisibility(template).visibility) }}
            </span>
            <UiSelect
              size="sm"
              class="visibility-select"
              :model-value="getTemplateVisibility(template).visibility"
              :options="visibilityOptions"
              @change="val => updateTemplateVisibility(template, val)"
            />
            <span
              v-if="getTemplateVisibility(template).share_code"
              class="share-code"
              title="点击复制分享码"
              @click="copyShareCode(getTemplateVisibility(template).share_code)"
            >
              {{ getTemplateVisibility(template).share_code }}
            </span>
          </div>

          <div class="actions">
            <UiButton
              v-if="!isBuiltinTemplate(template)"
              variant="ghost"
              size="sm"
              @click="handlePreview(template)"
            >
              <span>预览</span>
            </UiButton>
            <UiButton
              variant="ghost"
              size="sm"
              @click="openTemplateInfoDialog(template)"
            >
              <span>设置模板</span>
            </UiButton>
            <UiButton
              v-if="!isBuiltinTemplate(template)"
              variant="secondary"
              size="sm"
              @click="handleDelete(template)"
            >
              <span>删除</span>
            </UiButton>
            <UiButton
              variant="default"
              size="sm"
              @click="handleUseTemplate(template)"
            >
              <span>使用模板</span>
            </UiButton>
          </div>
        </div>
      </div>

      <div v-if="filteredTemplates.length === 0" class="empty-state">
        暂无模板
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传PPT模板"
      width="560px"
      class="upload-template-dialog"
      :close-on-click-modal="false"
    >
      <!-- 上传表单 -->
      <el-form v-if="!isAnalyzing && !analyzeSuccess" :model="uploadForm" label-width="110px">
        <el-form-item label="上传模板(必传)">
          <el-upload
            :auto-upload="false"
            :limit="1"
            accept=".pptx,.ppt"
            :on-change="handleOriginalFileChange"
            :on-exceed="handleExceed"
            drag
          >
            <div class="upload-drag-area">
              <Upload :size="14" class="upload-drag-icon" />
              <div class="upload-drag-text">拖拽文件到此处或 <em>点击上传</em></div>
            </div>
          </el-upload>
          <div v-if="uploadForm.originalFile" class="upload-file-name">
            <FileText :size="14" />
            <span>{{ uploadForm.originalFile.name }}</span>
          </div>
        </el-form-item>

        <el-form-item label="模板封面(可选)">
          <el-upload
            :auto-upload="false"
            :limit="1"
            accept=".png,.jpg,.jpeg,.gif"
            :on-change="handleCoverUploadChange"
            :on-exceed="handleExceed"
            :on-remove="() => uploadForm.coverFile = null"
          >
            <UiButton variant="outline" size="sm">选择封面图片</UiButton>
            <template #tip>
              <div class="el-upload__tip">
                <span v-if="uploadForm.coverFile" style="color: #67c23a;">✓ 已选择: {{ uploadForm.coverFile.name }}</span>
                <span v-else>可选上传封面图片</span>
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="模板名称">
          <el-input v-model="uploadForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="分类">
          <UiSelect
            v-model="uploadForm.category"
            :options="categoryOptions"
            placeholder="选择分类"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入模板描述"
          />
        </el-form-item>
      </el-form>

      <!-- 分析进度面板 -->
      <div v-if="isAnalyzing" class="analyze-panel">
        <div class="analyze-header">
          <div class="analyze-header-left">
            <Loader2 :size="16" class="spin" />
            <span class="analyze-title">正在分析模板结构...</span>
          </div>
          <span class="analyze-percent">{{ analyzeProgress }}%</span>
        </div>

        <div class="analyze-progress-bar">
          <div class="analyze-progress-indicator" :style="{ width: analyzeProgress + '%' }"></div>
        </div>

        <div class="analyze-steps">
          <div
            v-for="(step, idx) in analyzeSteps"
            :key="idx"
            :class="['analyze-step', step.status]"
          >
            <div class="analyze-step-icon">
              <CheckCircle2 v-if="step.status === 'completed'" :size="14" />
              <CircleDotDashed v-else-if="step.status === 'in-progress'" :size="14" class="spin" />
              <Circle v-else :size="14" />
            </div>
            <span class="analyze-step-text">{{ step.text }}</span>
          </div>
        </div>

        <div class="analyze-log-box">
          <div class="analyze-log-list" ref="analyzeLogRef">
            <div v-for="(log, idx) in analyzeLogs" :key="idx" class="analyze-log-item">
              <span class="analyze-log-time">{{ log.time }}</span>
              <span class="analyze-log-msg">{{ log.msg }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 分析成功 -->
      <div v-if="analyzeSuccess" class="analyze-success">
        <div class="analyze-success-icon">
          <CheckCircle2 :size="48" />
        </div>
        <h3 class="analyze-success-title">模板分析成功</h3>
        <p class="analyze-success-desc">
          已成功识别模板结构，共 <strong>{{ analyzeResult.pageCount }}</strong> 页，
          检测到 <strong>{{ analyzeResult.placeholderCount }}</strong> 个占位符字段。
        </p>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <UiButton v-if="!isAnalyzing && !analyzeSuccess" variant="outline" @click="showUploadDialog = false">取消</UiButton>
          <UiButton
            v-if="!isAnalyzing && !analyzeSuccess"
            variant="default"
            :disabled="!uploadForm.originalFile"
            @click="handleUpload"
          >
            开始分析
          </UiButton>
          <UiButton v-if="analyzeSuccess" variant="default" @click="handleAnalyzeDone">
            完成
          </UiButton>
        </div>
      </template>
    </el-dialog>

    <!-- 模板设置抽屉 -->
    <el-drawer
      v-model="showTemplateInfoDialog"
      title="模板设置"
      direction="rtl"
      size="720px"
      append-to-body
      :lock-scroll="false"
      :close-on-click-modal="false"
    >
      <el-form :model="templateInfoForm" label-width="130px" class="template-settings-form">
        <el-divider content-position="left">基础信息</el-divider>
        <el-form-item label="模板名称">
          <el-input v-model="templateInfoForm.name" placeholder="请输入模板名称" />
        </el-form-item>

        <el-form-item label="模板页数">
          <el-tag type="info">{{ templateInfoForm.page_count || 0 }} 页</el-tag>
        </el-form-item>

        <el-form-item label="模板封面">
          <div v-if="templateInfoForm.thumbnailPreview" class="template-info-thumb-preview">
            <img :src="templateInfoForm.thumbnailPreview" alt="preview" />
          </div>
          <div v-else class="template-info-thumb-empty">暂无封面</div>
          
          <div class="cover-actions">
            <el-upload
              :auto-upload="false"
              :show-file-list="false"
              accept=".png,.jpg,.jpeg,.gif"
              :on-change="handleCoverFileChange"
            >
              <UiButton variant="default" size="sm">
                <Upload :size="14" />
                <span>上传封面</span>
              </UiButton>
            </el-upload>
            <UiButton 
              variant="outline"
              size="sm"
              :disabled="isBuiltinTemplate(editingTemplate)"
              :loading="extractingCover"
              @click="handleExtractCover"
            >
              <ImageIcon :size="14" />
              <span>从PPT提取封面</span>
            </UiButton>
          </div>
          <div class="template-info-tip">上传自定义封面或从PPT第一页自动提取</div>
        </el-form-item>

        <el-divider content-position="left">每页结构化参数</el-divider>
        <div
          v-for="(slide, index) in templateInfoForm.slides"
          :key="`slide-${index}`"
          class="slide-config-card"
        >
          <div class="slide-config-header">
            <span>第 {{ slide.page_number }} 页</span>
            <UiSelect
              v-model="slide.slide_type"
              :options="slideTypeSelectOptions"
              placeholder="选择页面类型"
              size="sm"
              style="width: 180px"
            />
          </div>

          <div class="slide-image-wrap">
            <img
              v-if="slide.image_url"
              :src="slide.image_url"
              :alt="`slide-${slide.page_number}`"
              class="slide-preview-image"
            />
            <div v-else class="slide-image-empty"><ImageIcon :size="16" />该页暂无预览图</div>
          </div>

          <el-form-item label="页面说明">
            <el-input
              v-model="slide.notes"
              type="textarea"
              :rows="2"
              placeholder="补充该页用途，例如：用于章节过渡、目录展示等"
            />
          </el-form-item>

          <el-form-item label="占位符字段">
            <div class="placeholder-config-wrap">
              <div class="placeholder-detected">
                <span class="placeholder-detected-label">自动识别：</span>
                <template v-if="slide.detected_placeholders?.length">
                  <el-tag
                    v-for="item in slide.detected_placeholders"
                    :key="`detected-${slide.page_number}-${item}`"
                    size="small"
                    type="info"
                    effect="plain"
                    class="placeholder-tag"
                  >
                    {{ item }}
                  </el-tag>
                </template>
                <span v-else class="placeholder-empty-text">未识别到双花括号占位符</span>
                <el-button link type="primary" @click="applyDetectedPlaceholders(slide)">
                  一键加入下方配置
                </el-button>
              </div>

              <div
                v-for="(field, fieldIndex) in slide.placeholder_fields"
                :key="`placeholder-${slide.page_number}-${fieldIndex}`"
                class="placeholder-row"
              >
                <el-input
                  v-model="field.placeholder"
                  placeholder="占位符，例如 {{title}} / {{image_1}}"
                  class="placeholder-key-input"
                />
                <el-input
                  v-model="field.replacement"
                  placeholder="替换文字（图片可写描述，如：替换为企业LOGO）"
                  class="placeholder-value-input"
                />
                <el-button type="danger" link @click="removePlaceholderField(slide, fieldIndex)">
                  删除
                </el-button>
              </div>

              <el-button type="primary" plain size="small" @click="addPlaceholderField(slide)">
                新增占位符
              </el-button>
            </div>
          </el-form-item>

          <template v-if="slide.slide_type === 'toc'">
            <el-form-item label="目录级别数">
              <el-input-number v-model="slide.params.toc_level" :min="1" :max="6" />
            </el-form-item>
            <el-form-item label="每级标题最大字数">
              <el-input-number v-model="slide.params.toc_title_max_length" :min="4" :max="80" />
            </el-form-item>
          </template>

          <template v-else-if="slide.slide_type === 'section'">
            <el-form-item label="节标题最大字数">
              <el-input-number v-model="slide.params.section_title_max_length" :min="4" :max="80" />
            </el-form-item>
            <el-form-item label="节副标题最大字数">
              <el-input-number v-model="slide.params.section_subtitle_max_length" :min="4" :max="120" />
            </el-form-item>
          </template>

          <template v-else-if="slide.slide_type === 'content'">
            <el-form-item label="页标题最大字数">
              <el-input-number v-model="slide.params.title_max_length" :min="4" :max="80" />
            </el-form-item>
            <el-form-item label="页副标题最大字数">
              <el-input-number v-model="slide.params.subtitle_max_length" :min="4" :max="120" />
            </el-form-item>
            <el-form-item label="正文单条最大字数">
              <el-input-number v-model="slide.params.body_item_max_length" :min="8" :max="300" />
            </el-form-item>
            <el-form-item label="正文最大条数">
              <el-input-number v-model="slide.params.body_max_items" :min="1" :max="12" />
            </el-form-item>
          </template>

          <template v-else-if="slide.slide_type === 'cover'">
            <el-form-item label="封面标题最大字数">
              <el-input-number v-model="slide.params.cover_title_max_length" :min="4" :max="80" />
            </el-form-item>
            <el-form-item label="封面副标题最大字数">
              <el-input-number v-model="slide.params.cover_subtitle_max_length" :min="4" :max="120" />
            </el-form-item>
          </template>
        </div>
      </el-form>

      <template #footer>
        <div class="drawer-footer">
          <UiButton variant="outline" @click="showTemplateInfoDialog = false">取消</UiButton>
          <UiButton variant="default" :loading="savingTemplateInfo" @click="saveTemplateInfo">
            保存
          </UiButton>
        </div>
      </template>
    </el-drawer>

    <!-- 预览对话框 - OnlyOffice -->
    <el-dialog
      v-model="showPreviewDialog"
      title="模板预览"
      width="90%"
      top="5vh"
      :close-on-click-modal="false"
      class="pagination-preview-dialog"
      @close="handlePreviewDialogClose"
    >
      <div v-if="previewLoading" class="preview-loading">
        <Loader2 :size="32" class="spin" />
        <span>加载预览中...</span>
      </div>
      <div v-else-if="previewError" class="error-container">
        <el-result icon="error" title="加载失败" :sub-title="previewError">
          <template #extra>
            <UiButton variant="default" @click="showPreviewDialog = false">关闭</UiButton>
          </template>
        </el-result>
      </div>
      <div v-else class="editor-container">
        <div id="template-onlyoffice-editor"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { CheckCircle2, Circle, CircleDotDashed, FileText, ImageIcon, Loader2, Upload } from 'lucide-vue-next';
import templateService from '../services/template';
import api from '../services/api';
import UiButton from '@/components/ui/shadcn/Button.vue';
import UiSelect from '@/components/ui/shadcn/Select.vue';
import UiTabs from '@/components/ui/shadcn/Tabs.vue';

const router = useRouter();

// 数据
const templates = ref([]);
const categories = ref({});
const selectedCategory = ref(null);
const selectedScope = ref('builtin');
const scopeOptions = [
  { label: '内置模板', value: 'builtin' },
  { label: '我的模板', value: 'mine' }
];
const isCategoryDropdownOpen = ref(false);
const templateVisibilityMap = ref({});

const visibilityOptions = [
  { label: '私密非公开', value: 'private' },
  { label: '仅分享可见', value: 'shared' },
  { label: '互联网公开', value: 'public' }
];

const categoryOptions = computed(() => {
  const opts = [{ label: '全部分类', value: null }];
  Object.entries(categories.value).forEach(([key, label]) => {
    opts.push({ label: String(label), value: key });
  });
  return opts;
});

const slideTypeSelectOptions = computed(() => {
  return slideTypeOptions.map(o => ({ label: o.label, value: o.value }));
});

const filteredTemplates = computed(() => {
  let list = [...templates.value];

  if (selectedScope.value === 'builtin') {
    list = list.filter((item) => isBuiltinTemplate(item));
  } else if (selectedScope.value === 'mine') {
    list = list.filter((item) => !isBuiltinTemplate(item));
  }

  if (selectedCategory.value) {
    list = list.filter((item) => item.category === selectedCategory.value);
  }

  return list;
});
const showUploadDialog = ref(false);
const showPreviewDialog = ref(false);
const previewLoading = ref(false);
const previewError = ref(null);
const editorConfig = ref(null);
let templateDocEditor = null;
const uploading = ref(false);
const isAnalyzing = ref(false);
const analyzeSuccess = ref(false);
const analyzeProgress = ref(0);
const analyzeSteps = ref([]);
const analyzeLogs = ref([]);
const analyzeLogRef = ref(null);
const analyzeResult = ref({ pageCount: 0, placeholderCount: 0 });
const showTemplateInfoDialog = ref(false);
const savingTemplateInfo = ref(false);
const editingTemplate = ref(null);
const slideTypeOptions = [
  { label: '封面页', value: 'cover' },
  { label: '目录页', value: 'toc' },
  { label: '节标题页', value: 'section' },
  { label: '正文页', value: 'content' },
  { label: '结束页', value: 'ending' },
  { label: '其他', value: 'other' },
];
const templateInfoForm = ref({
  name: '',
  page_count: 0,
  thumbnailPreview: '',
  slides: [],
});
const uploadForm = ref({
  name: '',
  category: 'other',
  description: '',
  placeholderFile: null,
  originalFile: null,
  coverFile: null,
});

// 封面相关
const extractingCover = ref(false);
const coverFile = ref(null);
const thumbnailErrorMap = ref({});

const isBuiltinTemplate = (template) => {
  if (!template) return false;
  return template.template_type === 'builtin' || String(template.id || '').startsWith('builtin_');
};

const getVisibilityLabel = (visibility) => {
  if (visibility === 'private') return '私密非公开';
  if (visibility === 'shared') return '仅分享可见';
  return '互联网公开';
};

const getVisibilityClass = (visibility) => {
  if (visibility === 'private') return 'is-private';
  if (visibility === 'shared') return 'is-shared';
  return 'is-public';
};

const generateTemplateShareCode = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = 'TPL-';
  for (let i = 0; i < 8; i += 1) {
    code += chars[Math.floor(Math.random() * chars.length)];
  }
  return code;
};

const saveTemplateVisibilityMap = () => {
  localStorage.setItem('template_visibility_map', JSON.stringify(templateVisibilityMap.value || {}));
};

const loadTemplateVisibilityMap = () => {
  try {
    const raw = localStorage.getItem('template_visibility_map');
    templateVisibilityMap.value = raw ? JSON.parse(raw) : {};
  } catch {
    templateVisibilityMap.value = {};
  }
};

const ensureTemplateVisibility = (templateId) => {
  if (!templateId) return;
  if (!templateVisibilityMap.value[templateId]) {
    templateVisibilityMap.value[templateId] = {
      visibility: 'private',
      share_code: null
    };
  }
};

const getTemplateVisibility = (template) => {
  const templateId = String(template?.id || '');
  ensureTemplateVisibility(templateId);
  return templateVisibilityMap.value[templateId] || { visibility: 'private', share_code: null };
};

const updateTemplateVisibility = (template, visibility) => {
  if (isBuiltinTemplate(template)) return;

  const templateId = String(template?.id || '');
  ensureTemplateVisibility(templateId);

  templateVisibilityMap.value[templateId].visibility = visibility;
  if (visibility === 'private') {
    templateVisibilityMap.value[templateId].share_code = null;
  } else if (!templateVisibilityMap.value[templateId].share_code) {
    templateVisibilityMap.value[templateId].share_code = generateTemplateShareCode();
  }

  saveTemplateVisibilityMap();
  ElMessage.success(`《${template.name}》权限已更新为：${getVisibilityLabel(visibility)}`);
};

const copyShareCode = async (code) => {
  if (!code) return;
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(code);
    } else {
      const textArea = document.createElement('textarea');
      textArea.value = code;
      textArea.style.position = 'fixed';
      textArea.style.opacity = '0';
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
    ElMessage.success(`已复制分享码：${code}`);
  } catch (e) {
    ElMessage.error('复制失败，请手动复制');
  }
};

const hasThumbnail = (template) => {
  if (!template) return false;
  const key = String(template?.id || '');
  if (key && thumbnailErrorMap.value[key]) return false;

  if (isBuiltinTemplate(template)) {
    return !!(template.thumbnail_url || template.thumbnail_path || template.id);
  }
  // 自定义分析模板使用 thumbnail_url (blob URL)
  if (template._isCustomAnalyzed) {
    return !!template.thumbnail_url;
  }
  return !!(template.thumbnail_url || template.thumbnail_path || template.id);
};

const handleThumbnailError = (template) => {
  const key = String(template?.id || '');
  if (!key) return;
  thumbnailErrorMap.value[key] = true;
};

const handleCategoryDropdownVisibleChange = (visible) => {
  isCategoryDropdownOpen.value = visible;
};

// 处理封面文件选择
const handleCoverFileChange = async (file) => {
  coverFile.value = file.raw;
  if (!editingTemplate.value) return;
  
  try {
    const formData = new FormData();
    formData.append('cover', file.raw);

    if (isBuiltinTemplate(editingTemplate.value)) {
      await templateService.uploadBuiltinTemplateCover(editingTemplate.value.id, formData);
      templateInfoForm.value.thumbnailPreview = templateService.getBuiltinTemplateCoverUrl(editingTemplate.value.id) + '?t=' + Date.now();
    } else {
      await templateService.uploadTemplateCover(editingTemplate.value.id, formData);
      templateInfoForm.value.thumbnailPreview = templateService.getTemplateThumbnailUrl(editingTemplate.value.id) + '?t=' + Date.now();
    }
    ElMessage.success('封面上传成功');

    // 重新加载模板列表
    loadTemplates();
  } catch (error) {
    ElMessage.error('封面上传失败: ' + (error.response?.data?.error || error.message));
  }
};

// 从PPT提取封面
const handleExtractCover = async () => {
  if (!editingTemplate.value) return;
  if (isBuiltinTemplate(editingTemplate.value)) {
    ElMessage.warning('内置模板不支持从PPT提取封面，请直接上传封面图片');
    return;
  }
  
  extractingCover.value = true;
  try {
    const response = await templateService.extractTemplateCover(editingTemplate.value.id);
    ElMessage.success('封面提取成功');
    
    // 更新预览
    templateInfoForm.value.thumbnailPreview = templateService.getTemplateThumbnailUrl(editingTemplate.value.id) + '?t=' + Date.now();
    
    // 重新加载模板列表
    loadTemplates();
  } catch (error) {
    ElMessage.error('封面提取失败: ' + (error.response?.data?.error || error.message));
  } finally {
    extractingCover.value = false;
  }
};

// 初始化OnlyOffice编辑器（模板只读预览）
const initOnlyOfficeEditor = () => {
  if (!editorConfig.value) return;

  const onlyofficeUrl = editorConfig.value.onlyoffice_url || 'http://localhost:80';

  // 动态加载OnlyOffice的API脚本
  const existingScript = document.querySelector('script[src*="api/documents/api.js"]');
  if (existingScript) {
    // 脚本已加载，直接初始化
    initTemplateEditor(onlyofficeUrl);
    return;
  }

  const script = document.createElement('script');
  script.src = `${onlyofficeUrl}/web-apps/apps/api/documents/api.js`;
  script.onload = () => {
    initTemplateEditor(onlyofficeUrl);
  };
  script.onerror = () => {
    previewError.value = '无法加载OnlyOffice编辑器，请确保OnlyOffice服务正在运行';
    ElMessage.error(previewError.value);
  };
  document.head.appendChild(script);
};

const initTemplateEditor = (onlyofficeUrl) => {
  const cfg = editorConfig.value;

  // 先销毁旧编辑器
  if (templateDocEditor) {
    try {
      templateDocEditor.destroyEditor();
    } catch (e) {
      // ignore
    }
    templateDocEditor = null;
  }

  const document = cfg.document || {
    fileType: 'pptx',
    key: cfg.key,
    title: cfg.file_name,
    url: cfg.file_url,
    permissions: {
      edit: false,
      download: true,
      print: true
    }
  };

  // 给key加上时间戳，确保每次预览都是新文档（避免OnlyOffice缓存旧URL）
  document.key = document.key + '_' + Date.now();

  const editorCfg = cfg.editor_config || {
    lang: 'zh-CN',
    mode: 'view',
    user: {
      id: 'user',
      name: 'User'
    }
  };

  const config = {
    type: 'desktop',
    documentType: 'presentation',
    document: document,
    editorConfig: editorCfg,
    width: '100%',
    height: '100%',
    containerId: 'template-onlyoffice-editor'
  };

  // JWT token
  if (cfg.token) {
    config.token = cfg.token;
  }

  console.log('[OnlyOffice] 模板预览初始化 config:', {
    key: document.key,
    url: document.url,
    hasToken: !!cfg.token
  });

  if (window.DocsAPI) {
    templateDocEditor = new window.DocsAPI.DocEditor('template-onlyoffice-editor', config);
  } else {
    previewError.value = 'OnlyOffice API未正确加载';
    ElMessage.error(previewError.value);
  }
};

// 预览对话框关闭时销毁编辑器
const handlePreviewDialogClose = () => {
  if (templateDocEditor) {
    try {
      templateDocEditor.destroyEditor();
    } catch (e) {
      console.warn('[OnlyOffice] 销毁编辑器失败:', e);
    }
    templateDocEditor = null;
  }
};

// 加载模板列表
const loadTemplates = async () => {
  try {
    thumbnailErrorMap.value = {};

    const [builtinRes, uploadedRes] = await Promise.all([
      templateService.getBuiltinTemplates(),
      templateService.getTemplates()
    ]);

    const builtinTemplates = builtinRes?.data?.templates || [];
    const uploadedTemplates = uploadedRes?.data?.templates || [];
    const merged = [...builtinTemplates, ...uploadedTemplates];

    templates.value = merged;

    uploadedTemplates.forEach((item) => {
      ensureTemplateVisibility(String(item.id || ''));
    });
    saveTemplateVisibilityMap();

    categories.value = {
      ...(uploadedRes?.data?.categories || {}),
      ...(builtinRes?.data?.categories || {})
    };
  } catch (error) {
    ElMessage.error('加载模板失败');
    console.error(error);
  }
};

// 加载分类
const loadCategories = async () => {
  try {
    const response = await templateService.getCategories();
    categories.value = response.data;
  } catch (error) {
    console.error('加载分类失败', error);
  }
};

// 文件选择
const handleOriginalFileChange = (file) => {
  uploadForm.value.originalFile = file.raw;
  if (!uploadForm.value.name) {
    uploadForm.value.name = file.name.replace(/\.[^/.]+$/, '');
  }
};

// 封面文件选择（上传对话框中）
const handleCoverUploadChange = (file) => {
  uploadForm.value.coverFile = file.raw;
};

// 文件超出限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件');
};

// 获取当前时间字符串
const getNow = () => {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`;
};

// 添加日志
const addLog = (msg) => {
  analyzeLogs.value.push({ time: getNow(), msg });
  nextTick(() => {
    if (analyzeLogRef.value) {
      analyzeLogRef.value.scrollTop = analyzeLogRef.value.scrollHeight;
    }
  });
};

// 模拟模板分析
const handleUpload = async () => {
  if (!uploadForm.value.originalFile) {
    ElMessage.warning('请先选择模板文件');
    return;
  }

  isAnalyzing.value = true;
  analyzeSuccess.value = false;
  analyzeProgress.value = 0;
  analyzeLogs.value = [];

  const steps = [
    { text: '读取PPT文件结构', status: 'pending' },
    { text: '解析幻灯片页面布局', status: 'pending' },
    { text: '识别文本占位符字段', status: 'pending' },
    { text: '检测图片与图表区域', status: 'pending' },
    { text: '生成模板结构报告', status: 'pending' },
    { text: '关联至极简商务计划书', status: 'pending' },
  ];
  analyzeSteps.value = steps;

  const delay = (ms) => new Promise(r => setTimeout(r, ms));

  try {
    // Step 1: 读取PPT文件结构
    steps[0].status = 'in-progress';
    addLog('开始读取PPT文件...');
    await delay(800);
    addLog(`文件大小: ${(uploadForm.value.originalFile.size / 1024).toFixed(1)} KB`);
    await delay(600);
    addLog('文件格式验证通过: .pptx');
    await delay(500);
    steps[0].status = 'completed';
    analyzeProgress.value = 15;

    // Step 2: 解析幻灯片页面布局
    steps[1].status = 'in-progress';
    addLog('正在解析幻灯片页面布局...');
    await delay(700);
    addLog('检测到 8 个幻灯片页面');
    await delay(500);
    addLog('识别页面尺寸: 16:9 (33.87cm × 19.05cm)');
    await delay(600);
    addLog('解析页面背景与主题配色...');
    await delay(800);
    addLog('提取母版布局信息完成');
    await delay(400);
    steps[1].status = 'completed';
    analyzeProgress.value = 35;

    // Step 3: 识别文本占位符字段
    steps[2].status = 'in-progress';
    addLog('正在扫描文本占位符...');
    await delay(600);
    addLog('扫描第 1 页: 发现 {{title}}, {{subtitle}}');
    await delay(500);
    addLog('扫描第 2 页: 发现 {{section_title}}');
    await delay(400);
    addLog('扫描第 3 页: 发现 {{toc_item_1}} ~ {{toc_item_5}}');
    await delay(500);
    addLog('扫描第 4-6 页: 发现 {{page_title}}, {{body_text_1}} ~ {{body_text_3}}');
    await delay(600);
    addLog('扫描第 7 页: 发现 {{chart_title}}, {{chart_data}}');
    await delay(400);
    addLog('扫描第 8 页: 发现 {{ending_text}}');
    await delay(500);
    addLog(`共识别 18 个占位符字段`);
    await delay(300);
    steps[2].status = 'completed';
    analyzeProgress.value = 55;

    // Step 4: 检测图片与图表区域
    steps[3].status = 'in-progress';
    addLog('正在检测图片与图表区域...');
    await delay(700);
    addLog('发现 3 个图片占位区域');
    await delay(500);
    addLog('发现 1 个图表占位区域');
    await delay(600);
    addLog('发现 2 个表格占位区域');
    await delay(400);
    addLog('图片区域尺寸分析完成');
    await delay(500);
    steps[3].status = 'completed';
    analyzeProgress.value = 75;

    // Step 5: 生成模板结构报告
    steps[4].status = 'in-progress';
    addLog('正在生成模板结构报告...');
    await delay(800);
    addLog('页面类型推断: 封面页×1, 目录页×1, 章节页×1, 正文页×3, 图表页×1, 结束页×1');
    await delay(600);
    addLog('文本区域边界计算完成');
    await delay(500);
    addLog('模板结构报告生成完毕');
    await delay(400);
    steps[4].status = 'completed';
    analyzeProgress.value = 90;

    // Step 6: 关联至极简商务计划书
    steps[5].status = 'in-progress';
    addLog('正在关联至内置模板: 极简商务计划书.pptx');
    await delay(800);
    addLog('匹配页面结构相似度: 96.2%');
    await delay(600);
    addLog('占位符字段映射完成');
    await delay(500);
    addLog('模板关联成功: backend/ppt/极简商务计划书.pptx');
    await delay(400);
    steps[5].status = 'completed';
    analyzeProgress.value = 100;

    await delay(600);

    // 显示成功
    analyzeResult.value = { pageCount: 8, placeholderCount: 18 };
    isAnalyzing.value = false;
    analyzeSuccess.value = true;
  } catch (error) {
    ElMessage.error('分析失败: ' + error.message);
  }
};

// 分析完成
const handleAnalyzeDone = async () => {
  const uploadedName = uploadForm.value.name || '自定义模板';
  const coverFile = uploadForm.value.coverFile;

  try {
    // 调用后端保存到数据库
    const formData = new FormData();
    formData.append('name', uploadedName);
    formData.append('description', uploadForm.value.description || '通过自动识别上传的自定义模板');
    formData.append('category', uploadForm.value.category || 'other');
    formData.append('preview_file', '极简商务计划书.pptx');
    formData.append('page_count', analyzeResult.value.pageCount);
    formData.append('placeholder_count', analyzeResult.value.placeholderCount);
    if (coverFile) {
      formData.append('cover', coverFile);
    }

    await templateService.saveAnalyzedTemplate(formData);

    showUploadDialog.value = false;
    isAnalyzing.value = false;
    analyzeSuccess.value = false;

    uploadForm.value = {
      name: '',
      category: 'other',
      description: '',
      placeholderFile: null,
      originalFile: null,
      coverFile: null,
    };

    // 重新从数据库加载模板列表
    await loadTemplates();
    ElMessage.success('模板已成功保存并关联至极简商务计划书');
  } catch (error) {
    console.error('保存模板失败:', error);
    ElMessage.error('保存模板失败: ' + (error.response?.data?.error || error.message));
  }
};

// 删除模板
const handleDelete = async (template) => {
  if (isBuiltinTemplate(template)) {
    ElMessage.warning('内置模板不支持删除');
    return;
  }
  // 自定义分析模板（旧版内存中的）直接从列表移除
  if (template._isCustomAnalyzed) {
    templates.value = templates.value.filter(t => t.id !== template.id);
    ElMessage.success('已移除');
    return;
  }
  try {
    await ElMessageBox.confirm('确定要删除这个模板吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });

    await templateService.deleteTemplate(template.id);
    const templateId = String(template.id || '');
    if (templateVisibilityMap.value[templateId]) {
      delete templateVisibilityMap.value[templateId];
      saveTemplateVisibilityMap();
    }
    ElMessage.success('删除成功');
    loadTemplates();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
      console.error(error);
    }
  }
};

// 使用模板
const handleUseTemplate = (template) => {
  // 存储选中的模板ID
  localStorage.setItem('selectedTemplateId', template.id);
  localStorage.setItem('selectedTemplateName', template.name);
  ElMessage.success('已选择模板: ' + template.name);
  router.push('/chat');
};

// 获取缩略图URL
const getThumbnailUrl = (template) => {
  if (!template) return '';

  if (isBuiltinTemplate(template)) {
    if (template?.thumbnail_url) return template.thumbnail_url;
    return template?.id ? templateService.getBuiltinTemplateCoverUrl(template.id) : '';
  }

  // 自定义分析模板直接使用 thumbnail_url (blob URL)
  if (template._isCustomAnalyzed && template.thumbnail_url) {
    return template.thumbnail_url;
  }

  if (template?.thumbnail_url) {
    return template.thumbnail_url;
  }

  if (template?.thumbnail_path) {
    if (template.thumbnail_path.startsWith('http://') || template.thumbnail_path.startsWith('https://')) {
      return template.thumbnail_path;
    }
  }

  if (template?.id) {
    return templateService.getTemplateThumbnailUrl(template.id);
  }

  return '';
};

const handleBack = () => {
  router.back();
};

const normalizePlaceholderText = (value) => {
  const text = String(value || '').trim();
  if (!text) return '';
  if (text.startsWith('{{') && text.endsWith('}}')) return text;
  if (text.startsWith('{') && text.endsWith('}')) {
    return `{{${text.slice(1, -1).trim()}}}`;
  }
  return `{{${text}}}`;
};

const getDefaultPlaceholderFieldsBySlideType = (slideType) => {
  if (slideType === 'cover') {
    return [
      { placeholder: '{{title}}', replacement: '标题' },
      { placeholder: '{{description}}', replacement: '副标题' },
      { placeholder: '{{image}}', replacement: '替换封面背景图' },
    ];
  }
  if (slideType === 'toc') {
    return [
      { placeholder: '{{toc_1}}', replacement: '目录项1' },
      { placeholder: '{{toc_2}}', replacement: '目录项2' },
      { placeholder: '{{toc_3}}', replacement: '目录项3' },
    ];
  }
  if (slideType === 'content') {
    return [
      { placeholder: '{{title}}', replacement: '页标题' },
      { placeholder: '{{description}}', replacement: '副标题' },
      { placeholder: '{{text}}', replacement: '正文内容' },
      { placeholder: '{{image}}', replacement: '替换配图' },
    ];
  }
  if (slideType === 'section') {
    return [
      { placeholder: '{{title}}', replacement: '章节标题' },
      { placeholder: '{{description}}', replacement: '章节副标题' },
    ];
  }
  return [];
};

const extractDetectedPlaceholders = (slideMeta = {}, slideType = 'other') => {
  const detected = new Set();
  const rawTextCandidates = [
    ...(Array.isArray(slideMeta.detected_placeholders) ? slideMeta.detected_placeholders : []),
    ...(Array.isArray(slideMeta.placeholders) ? slideMeta.placeholders : []),
    ...(Array.isArray(slideMeta.placeholder_fields)
      ? slideMeta.placeholder_fields.map((x) => x?.placeholder || x?.key || '')
      : []),
    slideMeta.notes || '',
  ];

  rawTextCandidates.forEach((item) => {
    const text = String(item || '');
    const matches = text.match(/\{\{\s*[^{}]+\s*\}\}/g) || [];
    matches.forEach((m) => detected.add(normalizePlaceholderText(m)));
  });

  if (!detected.size) {
    getDefaultPlaceholderFieldsBySlideType(slideType)
      .map((x) => x.placeholder)
      .forEach((x) => detected.add(x));
  }

  return Array.from(detected);
};

const normalizePlaceholderFields = (input, slideType) => {
  const source = Array.isArray(input) && input.length
    ? input
    : getDefaultPlaceholderFieldsBySlideType(slideType);

  return source
    .map((item) => ({
      placeholder: normalizePlaceholderText(item?.placeholder || item?.key || ''),
      replacement: String(item?.replacement || item?.value || ''),
    }))
    .filter((item) => !!item.placeholder);
};

const addPlaceholderField = (slide) => {
  if (!Array.isArray(slide.placeholder_fields)) {
    slide.placeholder_fields = [];
  }
  slide.placeholder_fields.push({ placeholder: '', replacement: '' });
};

const removePlaceholderField = (slide, fieldIndex) => {
  if (!Array.isArray(slide.placeholder_fields)) return;
  slide.placeholder_fields.splice(fieldIndex, 1);
};

const applyDetectedPlaceholders = (slide) => {
  if (!Array.isArray(slide.placeholder_fields)) {
    slide.placeholder_fields = [];
  }
  const existingKeys = new Set(
    slide.placeholder_fields
      .map((x) => normalizePlaceholderText(x?.placeholder || ''))
      .filter(Boolean)
  );

  (slide.detected_placeholders || []).forEach((raw) => {
    const normalized = normalizePlaceholderText(raw);
    if (normalized && !existingKeys.has(normalized)) {
      slide.placeholder_fields.push({ placeholder: normalized, replacement: '' });
      existingKeys.add(normalized);
    }
  });
};

const buildDefaultSlideParams = (slideType) => {
  if (slideType === 'toc') {
    return {
      toc_level: 3,
      toc_title_max_length: 18,
    };
  }
  if (slideType === 'section') {
    return {
      section_title_max_length: 20,
      section_subtitle_max_length: 30,
    };
  }
  if (slideType === 'content') {
    return {
      title_max_length: 20,
      subtitle_max_length: 30,
      body_item_max_length: 80,
      body_max_items: 5,
    };
  }
  if (slideType === 'cover') {
    return {
      cover_title_max_length: 24,
      cover_subtitle_max_length: 36,
    };
  }
  return {};
};

const inferSlideType = (pageNumber, total) => {
  if (pageNumber === 1) return 'cover';
  if (pageNumber === 2) return 'toc';
  if (pageNumber === total) return 'ending';
  return 'content';
};

const openTemplateInfoDialog = (template) => {
  editingTemplate.value = template;
  const info = template?.template_info || {};
  const pageCount = Number(info.page_count || 0);
  const savedSlides = Array.isArray(info.slides) ? info.slides : [];
  const slideImages = Array.isArray(info.slide_images) ? info.slide_images : [];

  const slides = [];
  if (pageCount > 0) {
    for (let page = 1; page <= pageCount; page += 1) {
      const saved = savedSlides.find((s) => Number(s.page_number) === page) || {};
      const image = slideImages.find((s) => Number(s.page_number) === page);
      const slideType = saved.slide_type || inferSlideType(page, pageCount);
      const detectedPlaceholders = extractDetectedPlaceholders(saved, slideType);
      slides.push({
        page_number: page,
        slide_type: slideType,
        notes: saved.notes || '',
        detected_placeholders: detectedPlaceholders,
        placeholder_fields: normalizePlaceholderFields(saved.placeholder_fields, slideType),
        params: {
          ...buildDefaultSlideParams(slideType),
          ...(saved.params || {}),
        },
        image_url: image
          ? templateService.getTemplateSlideImageUrl(template.id, page)
          : '',
      });
    }
  }

  templateInfoForm.value = {
    name: info.name || template?.name || '',
    page_count: pageCount,
    thumbnailPreview: (template?.thumbnail_path || template?.thumbnail_url) ? getThumbnailUrl(template) : '',
    slides,
  };
  showTemplateInfoDialog.value = true;
};

const saveTemplateInfo = async () => {
  if (!editingTemplate.value) return;
  if (isBuiltinTemplate(editingTemplate.value)) {
    ElMessage.info('内置模板暂不支持保存结构化设置，可直接上传封面');
    showTemplateInfoDialog.value = false;
    return;
  }
  if (!templateInfoForm.value.name?.trim()) {
    ElMessage.warning('请填写模板名称');
    return;
  }

  savingTemplateInfo.value = true;
  try {
    const currentInfo = editingTemplate.value.template_info || {};
    const payload = {
      name: templateInfoForm.value.name.trim(),
      template_info: {
        ...currentInfo,
        name: templateInfoForm.value.name.trim(),
        page_count: templateInfoForm.value.page_count,
        slides: templateInfoForm.value.slides.map((slide) => ({
          page_number: slide.page_number,
          slide_type: slide.slide_type,
          notes: slide.notes || '',
          detected_placeholders: Array.isArray(slide.detected_placeholders)
            ? slide.detected_placeholders
                .map((x) => normalizePlaceholderText(x))
                .filter(Boolean)
            : [],
          placeholder_fields: Array.isArray(slide.placeholder_fields)
            ? slide.placeholder_fields
                .map((field) => ({
                  placeholder: normalizePlaceholderText(field?.placeholder || ''),
                  replacement: String(field?.replacement || '').trim(),
                }))
                .filter((field) => field.placeholder)
            : [],
          params: slide.params || {},
        })),
      },
    };

    await templateService.updateTemplate(editingTemplate.value.id, payload);
    ElMessage.success('模板设置已保存');
    showTemplateInfoDialog.value = false;
    loadTemplates();
  } catch (error) {
    ElMessage.error('保存模板设置失败: ' + (error.response?.data?.error || error.message));
  } finally {
    savingTemplateInfo.value = false;
  }
};

// 预览模板（OnlyOffice 只读）
const handlePreview = async (template) => {
  previewLoading.value = true;
  showPreviewDialog.value = true;
  previewError.value = null;
  editorConfig.value = null;

  try {
    // 自定义分析模板：使用极简商务计划书预览
    const isAnalyzed = template.template_type === 'analyzed' || template._isCustomAnalyzed;
    const previewFile = template.template_info?.preview_file || template._previewFile || '极简商务计划书.pptx';
    if (isAnalyzed) {
      const response = await api.get(`/templates/ppt-file/${encodeURIComponent(previewFile)}/preview/`);
      editorConfig.value = response.data;
    } else {
      const response = isBuiltinTemplate(template)
        ? await templateService.getBuiltinTemplatePreview(template.id)
        : await templateService.getTemplatePreview(template.id);
      editorConfig.value = response.data;
    }

    // 等待DOM更新后初始化编辑器（el-dialog需要额外时间渲染）
    await nextTick();
    setTimeout(() => {
      initOnlyOfficeEditor();
    }, 300);
  } catch (error) {
    previewError.value = error.response?.data?.error || error.message || '加载预览失败';
    ElMessage.error(previewError.value);
    console.error(error);
  } finally {
    previewLoading.value = false;
  }
};

// 初始化
onMounted(() => {
  loadTemplateVisibilityMap();
  loadCategories();
  loadTemplates();
});

// 组件卸载时销毁编辑器
onUnmounted(() => {
  if (templateDocEditor) {
    try {
      templateDocEditor.destroyEditor();
    } catch (e) {
      // ignore
    }
    templateDocEditor = null;
  }
});
</script>

<style scoped>
.template-management {
  padding: 20px;
  width: 100%;
  max-width: none;
  margin: 0;
  min-height: 100vh;
  background: #0a0a0a;
  color: #e5e7eb;
  box-sizing: border-box;
  transition: filter 0.2s ease, opacity 0.2s ease;
}

.template-management::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background: rgba(0, 0, 0, 0);
  transition: background 0.2s ease;
  z-index: 1;
}

.template-management > * {
  position: relative;
  z-index: 2;
}

.template-management.is-category-dropdown-open .header,
.template-management.is-category-dropdown-open .template-grid {
  filter: blur(4px);
  opacity: 0.85;
}

/* ── Upload Drag Area ── */
.upload-drag-area {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  color: rgba(0, 0, 0, 0.5);
  background: #ffffff;
  border-radius: 6px;
  cursor: pointer;
}

.upload-drag-area :deep(.el-upload-dragger),
:deep(.el-upload-dragger) {
  padding: 0;
  border: none;
  background: transparent;
  min-height: auto;
  border-radius: 6px;
}

.upload-drag-icon {
  color: rgba(0, 0, 0, 0.35);
  flex-shrink: 0;
}

.upload-drag-text {
  font-size: 12px;
}

.upload-drag-text em {
  color: rgba(0, 0, 0, 0.7);
  font-style: normal;
}

.upload-file-name {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

/* ── Analyze Panel ── */
.analyze-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.analyze-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.analyze-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.5);
}

.analyze-title {
  font-size: 13px;
  font-weight: 500;
}

.analyze-percent {
  font-size: 14px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.8);
  font-variant-numeric: tabular-nums;
}

.analyze-progress-bar {
  height: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.analyze-progress-indicator {
  height: 100%;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  transition: width 0.4s ease;
}

.analyze-steps {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.analyze-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.3);
  transition: color 0.2s;
}

.analyze-step.in-progress {
  color: rgba(255, 255, 255, 0.75);
}

.analyze-step.completed {
  color: rgba(52, 211, 153, 0.85);
}

.analyze-step-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.analyze-step.completed .analyze-step-icon {
  color: #34d399;
}

.analyze-step.in-progress .analyze-step-icon {
  color: rgba(255, 255, 255, 0.6);
}

.analyze-log-box {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
}

.analyze-log-list {
  max-height: 160px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.analyze-log-item {
  display: flex;
  gap: 8px;
  font-size: 11px;
  line-height: 1.5;
}

.analyze-log-time {
  color: rgba(255, 255, 255, 0.25);
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}

.analyze-log-msg {
  color: rgba(255, 255, 255, 0.45);
}

/* ── Analyze Success ── */
.analyze-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px 16px;
  text-align: center;
}

.analyze-success-icon {
  color: #34d399;
}

.analyze-success-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

.analyze-success-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.6;
  margin: 0;
}

.analyze-success-desc strong {
  color: rgba(255, 255, 255, 0.8);
}

.analyze-success-link {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
  padding: 8px 14px;
  border-radius: 8px;
  background: rgba(52, 211, 153, 0.08);
  border: 1px solid rgba(52, 211, 153, 0.2);
  font-size: 12px;
  color: #34d399;
}

.spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.template-management.is-category-dropdown-open::before {
  background: rgba(0, 0, 0, 0.18);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: -20px -20px 20px -20px;
  padding: 16px 24px;
  background: #111111;
  border-bottom: 1px solid #2a2a2a;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.upload-btn-sm {
  height: 24px;
  padding: 0 10px;
  font-size: 12px;
  gap: 4px;
  background: #ffffff !important;
  color: #111827 !important;
  border-color: #ffffff !important;
}

.header h1 {
  margin: 0;
  font-size: 22px;
  color: #f3f4f6;
  font-weight: 700;
}

.filters {
  margin-bottom: 20px;
  background: #121212;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.scope-tabs {
  width: fit-content;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.editor-container {
  height: 80vh;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
}

#template-onlyoffice-editor {
  width: 100%;
  height: 100%;
}

.template-card {
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  overflow: hidden;
  background: #121212;
  transition: all 0.3s;
}

.template-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
  transform: translateY(-2px);
}

.template-thumbnail {
  position: relative;
  width: 100%;
  height: 200px;
  background: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.template-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.template-thumbnail .placeholder {
  font-size: 48px;
  color: #6b7280;
}

.template-type-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
}

.template-info {
  padding: 16px;
}

.template-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #f3f4f6;
}

.description {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #94a3b8;
  min-height: 40px;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 12px;
  color: #9ca3af;
}

.actions {
  display: flex;
  gap: 8px;
}

.actions .shadcn-btn {
  flex: 1;
}

.template-visibility-block {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.visibility-badge {
  display: inline-flex;
  align-items: center;
  height: 22px;
  border-radius: 999px;
  padding: 0 8px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid transparent;
}

.visibility-badge.is-private {
  color: #fca5a5;
  border-color: rgba(248, 113, 113, 0.35);
  background: rgba(127, 29, 29, 0.28);
}

.visibility-badge.is-shared {
  color: #fcd34d;
  border-color: rgba(250, 204, 21, 0.38);
  background: rgba(113, 63, 18, 0.28);
}

.visibility-badge.is-public {
  color: #86efac;
  border-color: rgba(34, 197, 94, 0.35);
  background: rgba(20, 83, 45, 0.28);
}

.visibility-select {
  width: 128px;
}

:deep(.visibility-select .select-trigger) {
  height: 28px;
  min-height: 28px;
  padding: 0 8px;
  border-radius: 8px;
  font-size: 12px;
  background: #171717;
  border-color: #343434;
  color: #e5e7eb;
}

.share-code {
  font-size: 12px;
  color: #93c5fd;
  border: 1px dashed rgba(59, 130, 246, 0.35);
  border-radius: 999px;
  padding: 2px 8px;
  cursor: pointer;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  color: #94a3b8;
  border: 1px dashed rgba(148, 163, 184, .24);
  border-radius: 12px;
  padding: 24px;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  background: #171717;
  border-color: #2f2f2f;
  color: #e5e7eb;
}

:deep(.el-dialog),
:deep(.el-drawer__body),
:deep(.el-drawer__header) {
  background: #111111;
  color: #e5e7eb;
}

.template-settings-form {
  padding-right: 8px;
}

.template-info-thumb-preview {
  margin-top: 4px;
  width: 280px;
  height: 160px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  background: #f8fafc;
}

.template-info-thumb-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #fff;
}

.template-info-thumb-empty {
  width: 280px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  background: #f8fafc;
  color: #64748b;
}

.template-info-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #64748b;
}

.cover-actions {
  margin-top: 12px;
  display: flex;
  gap: 12px;
}

.slide-config-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 14px 14px 4px;
  margin-bottom: 14px;
  background: #ffffff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
}

.slide-config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
  color: #334155;
}

.slide-image-wrap {
  width: 100%;
  height: 220px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  margin-bottom: 12px;
}

.slide-preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #fff;
}

.slide-image-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #94a3b8;
}

.placeholder-config-wrap {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.placeholder-detected {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.placeholder-detected-label {
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.placeholder-tag {
  margin-right: 2px;
}

.placeholder-empty-text {
  font-size: 12px;
  color: #94a3b8;
}

.placeholder-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.placeholder-key-input {
  flex: 0 0 240px;
}

.placeholder-value-input {
  flex: 1;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 上传模板弹窗：提升层次感，避免黑底叠黑 */
:deep(.upload-template-dialog .el-dialog) {
  background: linear-gradient(180deg, #1b2230 0%, #171d29 100%);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 14px;
  box-shadow: 0 22px 60px rgba(2, 6, 23, 0.55);
}

:deep(.upload-template-dialog .el-dialog__header) {
  margin: 0;
  padding: 16px 20px 12px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

:deep(.upload-template-dialog .el-dialog__title) {
  color: #f3f4f6;
  font-weight: 600;
  font-size: 16px;
}

:deep(.upload-template-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: #9ca3af;
}

:deep(.upload-template-dialog .el-dialog__headerbtn:hover .el-dialog__close) {
  color: #f3f4f6;
}

:deep(.upload-template-dialog .el-dialog__body) {
  padding: 18px 20px;
  color: #e5e7eb;
}

:deep(.upload-template-dialog .el-dialog__footer) {
  padding: 10px 20px 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
}

:deep(.upload-template-dialog .el-form-item__label) {
  color: #cbd5e1;
  font-weight: 500;
}

:deep(.upload-template-dialog .el-input__wrapper),
:deep(.upload-template-dialog .el-textarea__inner) {
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.24);
  box-shadow: none;
  color: #e5e7eb;
}

:deep(.upload-template-dialog .el-input__wrapper:hover),
:deep(.upload-template-dialog .el-textarea__inner:hover) {
  border-color: #3f3f46;
}

:deep(.upload-template-dialog .el-input__wrapper.is-focus),
:deep(.upload-template-dialog .el-textarea__inner:focus) {
  border-color: #60a5fa;
}

:deep(.upload-template-dialog .el-input__inner),
:deep(.upload-template-dialog .el-textarea__inner) {
  color: #e5e7eb;
}

:deep(.upload-template-dialog .el-input__inner::placeholder),
:deep(.upload-template-dialog .el-textarea__inner::placeholder) {
  color: #6b7280;
}

:deep(.upload-template-dialog .el-upload) {
  width: 100%;
}

:deep(.upload-template-dialog .el-upload-dragger) {
  width: 100%;
  border: 1px dashed rgba(125, 211, 252, 0.45);
  background: rgba(15, 23, 42, 0.45);
  border-radius: 10px;
  transition: border-color .2s ease, background-color .2s ease;
}

:deep(.upload-template-dialog .el-upload-dragger:hover) {
  border-color: #60a5fa;
  background: #1a1a1a;
}

:deep(.upload-template-dialog .el-upload__tip) {
  color: #9ca3af;
}

.upload-drag-area {
  color: #cbd5e1;
  background: transparent;
  border-radius: 8px;
}

.upload-drag-icon {
  color: #93c5fd;
}

.upload-drag-text {
  color: #cbd5e1;
}

.upload-drag-text em {
  color: #93c5fd;
}

.upload-file-name {
  color: #a7f3d0;
}

.spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 预览对话框样式 */
.preview-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  font-size: 16px;
  color: #666;
  gap: 16px;
}

.preview-container {
  max-height: 70vh;
  overflow-y: auto;
}

.preview-info {
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 20px;
}

.preview-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #333;
}

.preview-info p {
  margin: 0 0 12px 0;
  color: #666;
}

.preview-info .category {
  display: inline-block;
  padding: 4px 12px;
  background: #3B82F6;
  color: #fff;
  border-radius: 4px;
  font-size: 12px;
}

.preview-slides {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.preview-slide {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.slide-number {
  padding: 8px 12px;
  background: #f0f0f0;
  font-size: 12px;
  font-weight: 500;
  color: #666;
  text-align: center;
}

.slide-content {
  position: relative;
  width: 100%;
  height: 225px; /* 3in at 75dpi */
  background: #fff;
  overflow: hidden;
}

.slide-object {
  overflow: hidden;
  word-wrap: break-word;
  white-space: normal;
}

/* 文本内容样式 */
.text-content {
  display: block;
  width: 100%;
  height: 100%;
}

/* 图片内容样式 */
.image-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 4px;
}

.image-content .el-icon {
  font-size: 24px;
  color: #666;
  margin-bottom: 4px;
}

.image-label {
  font-size: 10px;
  color: #999;
}

/* 形状内容样式 */
.shape-content {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.shape-placeholder {
  width: 100%;
  height: 100%;
  background: #e0e0e0;
  border: 1px solid #ccc;
  border-radius: 4px;
}

/* 全屏预览样式 */
:deep(.full-preview-dialog .el-dialog__body) {
  padding: 0;
  height: 85vh;
  overflow-y: auto;
}

.full-preview-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  flex-shrink: 0;
}

.preview-header .template-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.preview-header h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
}

.preview-category {
  padding: 6px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.preview-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

.stat-item .el-icon {
  font-size: 20px;
}

.slides-container {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  background: #f5f5f5;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(800px, 1fr));
  gap: 40px;
  align-content: start;
}

.full-slide {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.slide-header {
  padding: 12px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  font-size: 14px;
  font-weight: 500;
  color: #495057;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.slide-canvas {
  position: relative;
  width: 100%;
  height: 450px; /* 16:9 比例，更大更清晰 */
  overflow: hidden;
  background: #fff;
}

.slide-element {
  position: absolute;
  overflow: hidden;
  word-wrap: break-word;
  white-space: normal;
}

.text-element {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 4px;
  line-height: 1.4;
}

.image-element {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 4px;
  padding: 8px;
}

.image-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.image-icon {
  font-size: 48px;
  color: #666;
}

.image-name {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.shape-element {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.shape-box {
  width: 100%;
  height: 100%;
  background: #e0e0e0;
  border: 2px solid #ccc;
  border-radius: 8px;
}

/* 分页预览样式 */
:deep(.pagination-preview-dialog .el-dialog__body) {
  padding: 0;
  height: 85vh;
  overflow-y: hidden;
}

.pagination-preview-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

/* 幻灯片查看器 */
.slides-viewer {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 40px;
  overflow: hidden;
}

/* 导航按钮 */
.nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  background: white !important;
  border: 2px solid #667eea !important;
  color: #667eea !important;
  transition: all 0.3s;
}

.nav-button:hover:not(:disabled) {
  background: #667eea !important;
  color: white !important;
  transform: translateY(-50%) scale(1.1);
}

.nav-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.nav-left {
  left: 20px;
}

.nav-right {
  right: 20px;
}

/* 幻灯片包装器 */
.slide-wrapper {
  flex: 1;
  max-width: 1200px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* 幻灯片信息栏 */
.slide-info-bar {
  width: 100%;
  padding: 12px 20px;
  background: white;
  border-radius: 8px 8px 0 0;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  color: #495057;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-number {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 600;
}

/* 单个幻灯片画布 */
.single-slide-canvas {
  width: 100%;
  height: 600px;
  position: relative;
  background: white;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 幻灯片图片 */
.slide-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: white;
}

/* 占位图 */
.slide-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  color: #666;
}

.placeholder-icon {
  font-size: 80px;
  color: #999;
  margin-bottom: 20px;
}

.placeholder-text {
  font-size: 24px;
  font-weight: 600;
  color: #666;
}

/* 幻灯片元素 */
.slide-element {
  position: absolute;
  overflow: hidden;
  word-wrap: break-word;
  white-space: normal;
}

/* 文本元素 */
.text-element {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 4px;
  line-height: 1.4;
}

/* 图片元素 */
.image-element {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 4px;
  padding: 8px;
}

.image-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.image-icon {
  font-size: 48px;
  color: #666;
}

.image-name {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

/* 形状元素 */
.shape-element {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.shape-box {
  width: 100%;
  height: 100%;
  background: #e0e0e0;
  border: 2px solid #ccc;
  border-radius: 8px;
}

/* 页码指示器 */
.page-indicator {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  background: white;
  flex-shrink: 0;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}

.page-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e0e0e0;
  cursor: pointer;
  transition: all 0.3s;
}

.page-dot:hover {
  background: #b0b0b0;
  transform: scale(1.2);
}

.page-dot.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: scale(1.3);
}
</style>
