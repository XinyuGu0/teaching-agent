<template>
  <div class="community-page invert-on-light">
    <header class="community-header">
      <div class="header-left">
        <h1>资源社区</h1>
        <p>支持 RAG 知识库分享导入 + 模板社区浏览</p>
      </div>
      <div class="header-actions">
        <UiButton variant="default" size="sm" @click="store.showImportDialog = true">
          <ScanLine :size="16" />
          导入分享码
        </UiButton>
        <UiButton variant="outline" size="sm" @click="$router.push('/dashboard')">
          <ArrowLeft :size="16" />
          返回
        </UiButton>
      </div>
    </header>

    <section class="toolbar">
      <div class="toolbar-top">
        <div class="tabs">
          <UiButton :variant="store.activeTab === 'kb' ? 'default' : 'outline'" size="sm" @click="switchTab('kb')">
            <Database :size="14" />
            知识库广场
          </UiButton>
          <UiButton :variant="store.activeTab === 'template' ? 'default' : 'outline'" size="sm" @click="switchTab('template')">
            <LayoutTemplate :size="14" />
            模板广场
          </UiButton>
        </div>

        <div class="search-main">
          <div class="search-wrap">
            <Search :size="14" class="search-icon" />
            <UiInput
              v-if="store.activeTab === 'kb'"
              v-model="store.kbSearch"
              placeholder="搜索知识库名称/标签"
              @input="reloadKb"
            />
            <UiInput
              v-else
              v-model="store.templateSearch"
              placeholder="搜索模板名称/标签"
              @input="reloadTemplates"
            />
          </div>

          <UiButton variant="outline" size="sm" class="advanced-btn" @click="showAdvanced = !showAdvanced">
            <SlidersHorizontal :size="14" />
            高级筛选
          </UiButton>

          <UiButton variant="ghost" size="sm" class="clear-btn" @click="clearCurrentFilters">
            <X :size="14" />
            清空
          </UiButton>
        </div>
      </div>

      <div class="filters" v-if="showAdvanced && store.activeTab === 'kb'">
        <UiSelect v-model="store.kbSort" :options="kbSortOptions" size="sm" @update:model-value="reloadKb" />
      </div>

      <div class="filters" v-if="showAdvanced && store.activeTab === 'template'">
        <UiSelect v-model="store.templateCategory" :options="templateCategoryOptions" size="sm" @update:model-value="reloadTemplates" />
        <UiSelect v-model="store.templateSort" :options="templateSortOptions" size="sm" @update:model-value="reloadTemplates" />
      </div>
    </section>

    <section class="hot-tags" v-if="store.hotTags.length">
      <span class="hot-label">热门标签：</span>
      <UiButton
        v-for="tag in displayedHotTags"
        :key="tag.name"
        variant="ghost"
        size="sm"
        class="tag-btn"
        @click="handleTagClick(tag.name)"
      >
        #{{ tag.name }}
      </UiButton>
      <UiButton
        v-if="store.hotTags.length > 6"
        variant="outline"
        size="sm"
        class="tag-more"
        @click="showAllTags = !showAllTags"
      >
        {{ showAllTags ? '收起' : `更多 ${store.hotTags.length - 6}` }}
      </UiButton>
    </section>

    <section v-if="store.activeTab === 'kb'" class="grid">
      <KbCard v-for="item in store.kbList" :key="item.id" :item="item" @preview="openKbDetail" />
      <div v-if="!store.kbLoading && store.kbList.length === 0" class="empty">暂无数据</div>
    </section>

    <section v-else class="grid template-grid">
      <TemplateCard
        v-for="item in store.templateList"
        :key="item.id"
        :item="item"
        @preview="openTemplateDetail"
        @like="onLike"
        @download="onDownload"
      />
      <div v-if="!store.templateLoading && store.templateList.length === 0" class="empty">暂无数据</div>
    </section>

    <section v-if="store.activeTab === 'template' && store.templateTotal > store.templatePageSize" class="pagination-wrap">
      <el-pagination
        background
        layout="prev, pager, next"
        :current-page="store.templatePage"
        :page-size="store.templatePageSize"
        :total="store.templateTotal"
        @current-change="onTemplatePageChange"
      />
    </section>

    <ImportCodeDialog
      v-model="store.importCode"
      :visible="store.showImportDialog"
      :loading="store.importLoading"
      :preview-data="store.importPreview?.data"
      @close="store.showImportDialog = false"
      @preview="onPreviewCode"
      @import="onImport"
    />
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { ScanLine, ArrowLeft, Database, LayoutTemplate, Search, SlidersHorizontal, X } from 'lucide-vue-next'
import { useCommunityStore } from '@/store/modules/community'
import UiButton from '@/components/ui/shadcn/Button.vue'
import UiInput from '@/components/ui/shadcn/Input.vue'
import UiSelect from '@/components/ui/shadcn/Select.vue'
import KbCard from '@/components/community/KbCard.vue'
import TemplateCard from '@/components/community/TemplateCard.vue'
import ImportCodeDialog from '@/components/community/ImportCodeDialog.vue'

const store = useCommunityStore()
const showAdvanced = ref(false)
const showAllTags = ref(false)

const displayedHotTags = computed(() => {
  if (showAllTags.value) return store.hotTags
  return store.hotTags.slice(0, 6)
})

const kbSortOptions = [
  { label: '最新发布', value: 'latest' },
  { label: '最受欢迎', value: 'popular' }
]

const templateCategoryOptions = [
  { label: '全部分类', value: '' },
  { label: '教育', value: 'education' },
  { label: '科技', value: 'technology' },
  { label: '商务', value: 'business' },
  { label: '创意', value: 'creative' },
  { label: '医疗', value: 'medical' },
  { label: '金融', value: 'finance' },
  { label: '艺术', value: 'art' }
]

const templateSortOptions = [
  { label: '按点赞', value: 'popular' },
  { label: '按下载', value: 'downloads' },
  { label: '按时间', value: 'latest' }
]

const switchTab = async (tab) => {
  store.activeTab = tab
  if (tab === 'kb') {
    await store.loadKbList()
  } else {
    await store.loadTemplateList()
  }
}

const reloadKb = async () => {
  store.kbPage = 1
  await store.loadKbList()
}

const reloadTemplates = async () => {
  store.templatePage = 1
  await store.loadTemplateList()
}

const clearCurrentFilters = async () => {
  if (store.activeTab === 'kb') {
    store.kbSearch = ''
    store.kbSort = 'latest'
    store.kbTagFilter = ''
    await reloadKb()
    return
  }

  store.templateSearch = ''
  store.templateCategory = ''
  store.templateSort = 'popular'
  await reloadTemplates()
}

const handleTagClick = async (name) => {
  if (store.activeTab === 'kb') {
    store.kbTagFilter = name
    await reloadKb()
  } else {
    store.templateSearch = name
    await reloadTemplates()
  }
}

const onPreviewCode = async (code) => {
  await store.previewShareCode(code)
}

const onImport = async (code) => {
  await store.importKb(code)
}

const onLike = (item) => {
  store.toggleLike(item.id)
}

const onDownload = async (item) => {
  await store.downloadTemplate(item.id)
}

const onTemplatePageChange = async (page) => {
  store.templatePage = page
  await store.loadTemplateList()
}

const openKbDetail = (item) => {
  store.openDetail('kb', item)
  ElMessage.info(`演示：查看知识库《${item.name}》`) 
}

const openTemplateDetail = (item) => {
  store.openDetail('template', item)
  ElMessage.info(`演示：查看模板《${item.name}》`)
}

onMounted(async () => {
  await Promise.all([
    store.loadHotTags(),
    store.loadKbList(),
    store.loadTemplateList()
  ])
})
</script>

<style scoped>
.community-page {
  min-height: 100vh;
  background: #0b1220;
  color: #e5e7eb;
  padding: 22px;
}
.community-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  gap: 12px;
}
.header-left h1 { margin: 0; font-size: 28px; }
.header-left p { margin: 6px 0 0; color: #94a3b8; }
.community-header h1 { margin: 0; font-size: 28px; }
.community-header p { margin: 6px 0 0; color: #94a3b8; }
.header-actions { display: flex; gap: 10px; }

.toolbar {
  border: 1px solid rgba(148, 163, 184, .16);
  background: rgba(15, 23, 42, .7);
  border-radius: 14px;
  padding: 12px;
  margin-bottom: 12px;
}

.toolbar-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.tabs { display: flex; gap: 10px; flex-wrap: wrap; }

.tabs :deep(.shadcn-btn.variant-default) {
  background: #ffffff;
  color: #111827;
  border-color: #ffffff;
}

.tabs :deep(.shadcn-btn.variant-outline) {
  background: #111827;
  color: #ffffff;
  border-color: rgba(148, 163, 184, .35);
}

.tabs :deep(.shadcn-btn.variant-default:hover:not(:disabled)) {
  background: #ffffff;
  color: #111827;
}

.tabs :deep(.shadcn-btn.variant-outline:hover:not(:disabled)) {
  background: #111827;
  color: #ffffff;
}

.search-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.search-wrap {
  position: relative;
  min-width: 260px;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  z-index: 1;
}

:deep(.search-wrap .shadcn-input) {
  padding-left: 32px;
  min-width: 260px;
  background: #0f172a;
  border-color: rgba(148, 163, 184, .24);
  color: #e5e7eb;
}

.filters {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding-top: 10px;
  border-top: 1px dashed rgba(148, 163, 184, .2);
}

:deep(.filters .select-trigger) {
  min-width: 140px;
  height: 32px;
  background: #0f172a;
  border-color: rgba(148, 163, 184, .24);
  color: #e5e7eb;
}

.hot-tags { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; }
.hot-label { color: #94a3b8; font-size: 13px; }
.tag-btn {
  border-radius: 999px;
  color: #cbd5e1;
  background: rgba(15, 23, 42, .55);
}

.tag-more {
  border-radius: 999px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
}

.template-grid {
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
}
.empty {
  grid-column: 1 / -1;
  text-align: center;
  color: #94a3b8;
  border: 1px dashed rgba(148, 163, 184, .24);
  border-radius: 12px;
  padding: 24px;
}

.pagination-wrap {
  margin-top: 14px;
  display: flex;
  justify-content: center;
}

:deep(.pagination-wrap .el-pagination) {
  --el-pagination-bg-color: #0f172a;
  --el-pagination-hover-color: #60a5fa;
  --el-pagination-text-color: #cbd5e1;
  --el-pagination-button-color: #cbd5e1;
  --el-pagination-button-bg-color: #0f172a;
}

</style>
