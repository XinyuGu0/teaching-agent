<template>
  <div class="document-library invert-on-light">
    <!-- Header -->
    <header class="dl-header">
      <h1>文档管理</h1>
      <UiButton variant="ghost" size="sm" @click="$router.push('/dashboard')">返回</UiButton>
    </header>

    <!-- Main Content -->
    <main class="dl-main">
      <div class="library-content">
        <div class="dl-card">
          <!-- Card Header -->
          <div class="card-header">
            <div class="header-left">
              <span class="card-title">我的文档</span>
              <UiTag v-if="selectedRows.length > 0" variant="secondary" size="md">
                已选择 {{ selectedRows.length }} 项
              </UiTag>
            </div>

            <div class="header-actions">
              <UiButton
                variant="outline"
                size="sm"
                :disabled="selectedRows.length === 0"
                @click="handleBatchDelete"
              >
                <Trash2 :size="14" />
                <span>批量删除</span>
              </UiButton>
              <UiButton variant="default" size="sm" @click="triggerUpload">
                <Upload :size="14" />
                <span>上传文档</span>
              </UiButton>
              <input
                ref="uploadInput"
                type="file"
                multiple
                class="upload-input-hidden"
                :accept="acceptFileTypes"
                @change="handleFileChange"
              />
            </div>
          </div>

          <!-- Filter Toolbar -->
          <div class="filter-toolbar">
            <div class="search-input-wrap">
              <Search :size="15" class="search-icon" />
              <input
                v-model.trim="searchKeyword"
                class="shadcn-input dark-input"
                placeholder="搜索文档名称"
              />
              <button v-if="searchKeyword" class="clear-btn" @click="searchKeyword = ''">
                <X :size="14" />
              </button>
            </div>

            <div class="date-range-wrap">
              <input
                type="date"
                class="shadcn-input dark-input date-input"
                v-model="startDate"
                placeholder="开始日期"
              />
              <span class="date-sep">至</span>
              <input
                type="date"
                class="shadcn-input dark-input date-input"
                v-model="endDate"
                placeholder="结束日期"
              />
              <button v-if="startDate || endDate" class="clear-btn" @click="startDate = ''; endDate = ''">
                <X :size="14" />
              </button>
            </div>

            <UiButton
              variant="ghost"
              size="sm"
              :disabled="!hasActiveFilters"
              @click="resetFilters"
            >
              重置筛选
            </UiButton>

            <span class="filter-summary">
              共 {{ filteredDocuments.length }} / {{ documents.length }} 条
            </span>
          </div>

          <!-- Folder Grid -->
          <div class="folder-grid">
            <FolderCard
              title="全部文件"
              subtitle="查看所有格式文档"
              :count="documentsAfterBaseFilters.length"
              :active="!selectedFileType"
              @select="selectedFileType = ''"
            />
            <FolderCard
              v-for="folder in fileTypeFolders"
              :key="folder.type"
              :title="folder.label"
              :subtitle="`按 ${folder.label} 格式筛选`"
              :count="folder.count"
              :active="selectedFileType === folder.type"
              @select="selectedFileType = folder.type"
            />
          </div>

          <!-- Table -->
          <div class="table-wrap" v-loading="loading">
            <table class="shadcn-table">
              <thead>
                <tr>
                  <th class="col-check">
                    <input
                      type="checkbox"
                      :checked="isAllSelected"
                      :indeterminate="isIndeterminate"
                      @change="toggleSelectAll"
                      class="shadcn-checkbox"
                    />
                  </th>
                  <th class="col-name">文件名</th>
                  <th class="col-type">类型</th>
                  <th class="col-size">大小</th>
                  <th class="col-status">状态</th>
                  <th class="col-visibility">权限</th>
                  <th class="col-time">上传时间</th>
                  <th class="col-actions">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in filteredDocuments"
                  :key="row.id"
                  :class="{ 'row-selected': selectedIds.has(row.id) }"
                >
                  <td class="col-check">
                    <input
                      type="checkbox"
                      :checked="selectedIds.has(row.id)"
                      @change="toggleRow(row)"
                      class="shadcn-checkbox"
                    />
                  </td>
                  <td class="col-name">{{ row.original_filename }}</td>
                  <td class="col-type">
                    <UiTag variant="secondary" size="sm" class="file-type-tag">
                      <component :is="getFileTypeIcon(row.file_type)" :size="13" class="file-type-icon" />
                      <span class="file-type-text">{{ row.file_type }}</span>
                    </UiTag>
                  </td>
                  <td class="col-size">{{ formatFileSize(row.file_size) }}</td>
                  <td class="col-status">
                    <UiTag variant="default" size="sm">
                      已成功解析
                    </UiTag>
                  </td>
                  <td class="col-visibility">
                    <div class="visibility-cell">
                      <span :class="['visibility-badge', getVisibilityClass(row.visibility)]">
                        {{ getVisibilityLabel(row.visibility) }}
                      </span>
                      <UiSelect
                        size="sm"
                        class="visibility-select"
                        v-model="row.visibility"
                        :options="visibilityOptions"
                        @change="val => updateDocumentVisibility(row, val)"
                      />
                      <span
                        v-if="row.share_code"
                        class="share-code"
                        title="点击复制分享码"
                        @click="copyShareCode(row.share_code)"
                      >
                        {{ row.share_code }}
                      </span>
                    </div>
                  </td>
                  <td class="col-time">{{ formatDate(row.created_at) }}</td>
                  <td class="col-actions">
                    <div class="action-btns">
                      <UiButton variant="default" size="sm" @click="openPreview(row)">
                        <Eye :size="13" />
                        <span>预览</span>
                      </UiButton>
                      <UiButton variant="ghost" size="sm" @click="handleDelete(row)">
                        <Trash2 :size="13" />
                        <span>删除</span>
                      </UiButton>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- Empty State -->
            <div v-if="!loading && filteredDocuments.length === 0" class="empty-state">
              <FileText :size="48" class="empty-icon" />
              <p class="empty-text">暂无符合条件的文档</p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Preview Dialog -->
    <Teleport to="body">
      <div v-if="showPreviewDialog" class="dialog-overlay" @click.self="showPreviewDialog = false">
        <div class="dialog-panel preview-dialog">
          <div class="dialog-header">
            <span class="dialog-title">文件预览</span>
            <button class="dialog-close" @click="showPreviewDialog = false">
              <X :size="18" />
            </button>
          </div>
          <div class="dialog-body">
            <div v-if="previewError" class="preview-error">
              <AlertCircle :size="48" class="error-icon" />
              <h3 class="error-title">预览失败</h3>
              <p class="error-desc">{{ previewError }}</p>
              <UiButton variant="default" size="sm" @click="showPreviewDialog = false">关闭</UiButton>
            </div>
            <div v-else class="preview-container">
              <div v-if="previewType === 'pdf'" class="pdf-preview">
                <div class="pdf-toolbar">
                  <div class="btn-group">
                    <button class="btn-group-item" :disabled="pdfPage <= 1" @click="prevPage">上一页</button>
                    <button class="btn-group-item" :disabled="pdfPage >= pdfPageCount" @click="nextPage">下一页</button>
                  </div>
                  <span class="pdf-page">第 {{ pdfPage }} / {{ pdfPageCount }} 页</span>
                  <input
                    type="range"
                    class="shadcn-slider"
                    v-model.number="pdfScale"
                    min="0.5"
                    max="2"
                    step="0.1"
                  />
                  <span class="pdf-zoom-text">{{ Math.round(pdfScale * 100) }}%</span>
                </div>
                <div class="pdf-pages" ref="pdfContainer"></div>
              </div>
              <div v-else-if="previewType === 'text'" class="text-preview">
                <div class="markdown-body" v-html="markdownHtml"></div>
              </div>
              <div v-else-if="previewType === 'onlyoffice'" class="preview-onlyoffice-container"></div>
              <img v-else-if="previewType === 'image'" :src="previewUrl" class="preview-image" />
              <video v-else-if="previewType === 'video'" :src="previewUrl" class="preview-video" controls />
              <div v-else class="preview-unsupported">
                暂不支持该格式预览，请下载后查看。
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted, watch, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Trash2, Eye, Search, FileText, Image, Video, FolderOpen, BarChart3, BookOpen, X, AlertCircle } from 'lucide-vue-next'
import * as pdfjsLib from 'pdfjs-dist'
import api from '@/services/api'
import FolderCard from '@/components/ui/folder.vue'
import UiButton from '@/components/ui/shadcn/Button.vue'
import UiTag from '@/components/ui/shadcn/Tag.vue'
import UiSelect from '@/components/ui/shadcn/Select.vue'
import { marked } from 'marked'

const documents = ref([])
const loading = ref(false)
const showPreviewDialog = ref(false)
const previewUrl = ref('')
const previewType = ref('iframe')
const previewError = ref('')
const markdownHtml = ref('')

const pdfContainer = ref(null)
const pdfDoc = shallowRef(null)
const pdfPage = ref(1)
const pdfPageCount = ref(0)
const pdfScale = ref(1)
const selectedRows = ref([])
const searchKeyword = ref('')
const selectedFileType = ref('')
const startDate = ref('')
const endDate = ref('')

const acceptFileTypes = '.pdf,.doc,.docx,.txt,.md,.ppt,.pptx,.xls,.xlsx,.jpg,.jpeg,.png'

const fileTypeLabelMap = {
  pdf: 'PDF 文件',
  word: 'Word 文档',
  text: '文本文件',
  ppt: 'PPT 演示',
  excel: 'Excel 表格',
  image: '图片文件',
  video: '视频文件'
}

const visibilityOptions = [
  { label: '私密非公开', value: 'private' },
  { label: '仅分享可见', value: 'shared' },
  { label: '互联网公开', value: 'public' }
]

const documentsAfterBaseFilters = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  const hasDateRange = startDate.value && endDate.value

  let startTime = null
  let endTime = null

  if (hasDateRange) {
    startTime = new Date(startDate.value)
    startTime.setHours(0, 0, 0, 0)

    endTime = new Date(endDate.value)
    endTime.setHours(23, 59, 59, 999)
  }

  return documents.value.filter((doc) => {
    const filename = String(doc.original_filename || '').toLowerCase()

    if (keyword && !filename.includes(keyword)) {
      return false
    }

    if (hasDateRange) {
      const createdAt = doc.created_at ? new Date(doc.created_at) : null
      if (!createdAt || Number.isNaN(createdAt.getTime())) {
        return false
      }
      if (createdAt < startTime || createdAt > endTime) {
        return false
      }
    }

    return true
  })
})

const fileTypeFolders = computed(() => {
  const map = new Map()
  documentsAfterBaseFilters.value.forEach((doc) => {
    const type = String(doc.file_type || 'other').toLowerCase()
    map.set(type, (map.get(type) || 0) + 1)
  })

  return Array.from(map.entries())
    .map(([type, count]) => ({
      type,
      count,
      label: fileTypeLabelMap[type] || `${type.toUpperCase()} 文件`
    }))
    .sort((a, b) => b.count - a.count)
})

const filteredDocuments = computed(() => {
  const type = selectedFileType.value ? String(selectedFileType.value).toLowerCase() : ''
  if (!type) {
    return documentsAfterBaseFilters.value
  }

  return documentsAfterBaseFilters.value.filter((doc) => {
    const fileType = String(doc.file_type || '').toLowerCase()
    return fileType === type
  })
})

const hasActiveFilters = computed(() => {
  const hasKeyword = !!searchKeyword.value.trim()
  const hasType = !!selectedFileType.value
  const hasDate = !!(startDate.value || endDate.value)
  return hasKeyword || hasType || hasDate
})

onMounted(() => {
  fetchDocuments()
})

const fetchDocuments = async () => {
  loading.value = true
  try {
    const response = await api.get('/documents')
    documents.value = (response.data.documents || []).map((doc) => ({
      ...doc,
      visibility: doc.visibility || 'private',
      share_code: doc.share_code || null
    }))
    selectedRows.value = []
  } catch (error) {
    ElMessage.error('获取文档列表失败')
  } finally {
    loading.value = false
  }
}

const selectedIds = computed(() => new Set(selectedRows.value.map(r => r.id)))

const isAllSelected = computed(() => {
  return filteredDocuments.value.length > 0 && filteredDocuments.value.every(r => selectedIds.value.has(r.id))
})

const isIndeterminate = computed(() => {
  const count = filteredDocuments.value.filter(r => selectedIds.value.has(r.id)).length
  return count > 0 && count < filteredDocuments.value.length
})

const toggleSelectAll = (event) => {
  const checked = event.target.checked
  if (checked) {
    selectedRows.value = [...filteredDocuments.value]
  } else {
    selectedRows.value = []
  }
}

const toggleRow = (row) => {
  const idx = selectedRows.value.findIndex(r => r.id === row.id)
  if (idx >= 0) {
    selectedRows.value.splice(idx, 1)
  } else {
    selectedRows.value.push(row)
  }
}

const resetFilters = () => {
  searchKeyword.value = ''
  selectedFileType.value = ''
  startDate.value = ''
  endDate.value = ''
}

const uploadInput = ref(null)

const triggerUpload = () => {
  uploadInput.value?.click()
}

const isUploading = ref(false)

const handleFileChange = async (event) => {
  const files = Array.from(event.target.files || [])
  if (files.length === 0) return

  isUploading.value = true
  let successCount = 0
  let failCount = 0

  try {
    // Upload files concurrently (max 3 at a time)
    const batchSize = 3
    for (let i = 0; i < files.length; i += batchSize) {
      const batch = files.slice(i, i + batchSize)
      const results = await Promise.allSettled(
        batch.map(async (file) => {
          const formData = new FormData()
          formData.append('file', file)
          await api.post('/documents/upload', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          })
        })
      )
      results.forEach(r => {
        if (r.status === 'fulfilled') successCount++
        else failCount++
      })
    }

    if (successCount > 0 && failCount === 0) {
      ElMessage.success(`${successCount} 个文件上传成功`)
    } else if (successCount > 0 && failCount > 0) {
      ElMessage.warning(`${successCount} 个上传成功，${failCount} 个上传失败`)
    } else {
      ElMessage.error('文件上传失败')
    }
    fetchDocuments()
  } catch (error) {
    ElMessage.error('文件上传失败')
  } finally {
    isUploading.value = false
    event.target.value = ''
  }
}

const getPreviewType = (fileType) => {
  if (fileType === 'word' || fileType === 'ppt' || fileType === 'excel') {
    return 'onlyoffice'
  }
  if (fileType === 'pdf') {
    return 'pdf'
  }
  if (fileType === 'text') {
    return 'text'
  }
  if (fileType === 'image') return 'image'
  if (fileType === 'video') return 'video'
  return 'unsupported'
}

const getFileTypeIcon = (fileType) => {
  const type = (fileType || '').toLowerCase()
  if (type === 'pdf') return BookOpen
  if (type === 'word' || type === 'text') return FileText
  if (type === 'ppt') return FolderOpen
  if (type === 'excel') return BarChart3
  if (type === 'image') return Image
  if (type === 'video') return Video
  return FileText
}

const openPreview = async (row) => {
  previewError.value = ''
  previewType.value = getPreviewType(row.file_type)

  try {
    if (previewType.value === 'onlyoffice') {
      const response = await api.get(`/documents/${row.id}/onlyoffice`)
      const info = response.data

      const onlyofficeUrl = (info.onlyoffice_url || 'http://localhost:80').replace('localhost', '127.0.0.1')

      const docConfig = {
        document: info.document,
        documentType: info.documentType,
        editorConfig: info.editor_config,
      }
      if (info.token) {
        docConfig.token = info.token
      }

      showPreviewDialog.value = true
      await nextTick()

      // 动态加载OnlyOffice API脚本（如果尚未加载）
      const loadOnlyOfficeApi = () => {
        return new Promise((resolve, reject) => {
          if (window.DocsAPI) {
            resolve()
            return
          }
          const script = document.createElement('script')
          script.src = `${onlyofficeUrl}/web-apps/apps/api/documents/api.js`
          script.onload = resolve
          script.onerror = () => reject(new Error('无法加载OnlyOffice编辑器'))
          document.head.appendChild(script)
        })
      }

      try {
        await loadOnlyOfficeApi()
      } catch (e) {
        previewError.value = '无法加载OnlyOffice编辑器，请确保OnlyOffice服务正在运行'
        return
      }

      // 等待对话框DOM渲染完成
      setTimeout(() => {
        const container = document.querySelector('.preview-onlyoffice-container')
        if (container) {
          container.innerHTML = ''
          const editorDiv = document.createElement('div')
          editorDiv.id = 'document-library-onlyoffice-editor'
          editorDiv.style.width = '100%'
          editorDiv.style.height = '100%'
          container.appendChild(editorDiv)

          if (window.DocsAPI) {
            new window.DocsAPI.DocEditor('document-library-onlyoffice-editor', docConfig)
          } else {
            previewError.value = 'OnlyOffice编辑器未加载，请刷新页面重试'
          }
        }
      }, 300)
      return
    }

    const token = localStorage.getItem('access_token')
    if (previewType.value === 'pdf') {
      pdfPage.value = 1
      showPreviewDialog.value = true
      await nextTick()
      await loadPdf(row.id)
      return
    }

    if (previewType.value === 'text') {
      markdownHtml.value = ''
      showPreviewDialog.value = true
      const base = import.meta.env.VITE_API_BASE_URL || '/api'
      const res = await api.get(`/documents/${row.id}/preview`, { responseType: 'text' })
      const raw = typeof res.data === 'string' ? res.data : ''
      markdownHtml.value = await marked(raw)
      return
    }

    if (previewType.value === 'image' || previewType.value === 'video') {
      previewUrl.value = `${import.meta.env.VITE_API_BASE_URL}/documents/${row.id}/preview${token ? `?token=${token}` : ''}`
      showPreviewDialog.value = true
      return
    }

    showPreviewDialog.value = true
  } catch (error) {
    previewError.value = error.response?.data?.message || error.message || '预览失败'
    showPreviewDialog.value = true
  }
}

const loadPdf = async (documentId) => {
  try {
    previewError.value = ''
    pdfDoc.value = null
    pdfPageCount.value = 0

    pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
      'pdfjs-dist/build/pdf.worker.min.mjs',
      import.meta.url
    ).toString()

    const base = import.meta.env.VITE_API_BASE_URL || '/api'
    const pdfUrl = `${base}/documents/${documentId}/preview`

    const loadingTask = pdfjsLib.getDocument({
      url: pdfUrl,
      httpHeaders: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      },
      withCredentials: false
    })

    pdfDoc.value = await loadingTask.promise

    if (!pdfDoc.value || !pdfDoc.value.numPages) {
      throw new Error('PDF页数无效')
    }

    pdfPageCount.value = pdfDoc.value.numPages
    pdfPage.value = 1

    await nextTick()
    await renderPdfPages()
  } catch (error) {
    previewError.value = `PDF加载失败：${error?.message || '未知错误'}`
    console.error(error)
  }
}

const renderPdfPages = async () => {
  if (!pdfDoc.value || !pdfContainer.value) return
  pdfContainer.value.innerHTML = ''

  for (let pageNum = 1; pageNum <= pdfDoc.value.numPages; pageNum += 1) {
    const page = await pdfDoc.value.getPage(pageNum)
    const viewport = page.getViewport({ scale: pdfScale.value })

    const canvas = document.createElement('canvas')
    const context = canvas.getContext('2d')
    canvas.height = viewport.height
    canvas.width = viewport.width
    canvas.className = 'pdf-canvas'

    pdfContainer.value.appendChild(canvas)
    await page.render({ canvasContext: context, viewport }).promise
  }
}

const prevPage = () => {
  if (pdfPage.value > 1) {
    pdfPage.value -= 1
    scrollToPdfPage(pdfPage.value)
  }
}

const nextPage = () => {
  if (pdfPage.value < pdfPageCount.value) {
    pdfPage.value += 1
    scrollToPdfPage(pdfPage.value)
  }
}

const scrollToPdfPage = (pageNumber) => {
  if (!pdfContainer.value) return
  const pages = pdfContainer.value.querySelectorAll('.pdf-canvas')
  const target = pages[pageNumber - 1]
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

watch(pdfScale, async () => {
  if (previewType.value === 'pdf') {
    await renderPdfPages()
  }
})

watch(filteredDocuments, (rows) => {
  const visibleIds = new Set(rows.map((item) => item.id))
  selectedRows.value = selectedRows.value.filter((item) => visibleIds.has(item.id))
})

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文档吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.delete(`/documents/${row.id}`)
    ElMessage.success('删除成功')
    fetchDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) return

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 个文档吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await Promise.all(selectedRows.value.map((doc) => api.delete(`/documents/${doc.id}`)))
    ElMessage.success('批量删除成功')
    fetchDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const getStatusVariant = (status) => {
  const variants = {
    processing: 'outline',
    ready: 'default',
    failed: 'outline'
  }
  return variants[status] || 'secondary'
}

const getStatusText = (status) => {
  const texts = {
    processing: '处理中',
    ready: '已上传',
    failed: '失败'
  }
  return texts[status] || status
}

const generateShareCode = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let code = 'KB-'
  for (let i = 0; i < 8; i += 1) {
    code += chars[Math.floor(Math.random() * chars.length)]
  }
  return code
}

const getVisibilityLabel = (visibility) => {
  if (visibility === 'private') return '私密非公开'
  if (visibility === 'shared') return '仅分享可见'
  return '互联网公开'
}

const getVisibilityClass = (visibility) => {
  if (visibility === 'private') return 'is-private'
  if (visibility === 'shared') return 'is-shared'
  return 'is-public'
}

const updateDocumentVisibility = (row, visibility) => {
  row.visibility = visibility

  if (visibility === 'private') {
    row.share_code = null
  } else if (!row.share_code) {
    row.share_code = generateShareCode()
  }

  ElMessage.success(`《${row.original_filename}》权限已更新为：${getVisibilityLabel(visibility)}`)
}

const copyShareCode = async (code) => {
  if (!code) return
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(code)
    } else {
      const textArea = document.createElement('textarea')
      textArea.value = code
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
    }
    ElMessage.success(`已复制分享码：${code}`)
  } catch (e) {
    ElMessage.error('复制失败，请手动复制')
  }
}
</script>

<style scoped>
.document-library {
  min-height: 100vh;
  background: #0a0a0a;
  color: #e5e7eb;
}

/* ===== Header ===== */
.dl-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #111111;
  border-bottom: 1px solid #2a2a2a;
}

.dl-header h1 {
  margin: 0;
  font-size: 22px;
  color: #f3f4f6;
  font-weight: 700;
}

/* ===== Main ===== */
.dl-main {
  padding: 20px 24px;
  max-width: 1280px;
  margin: 0 auto;
}

.library-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* ===== Card ===== */
.dl-card {
  background: #121212;
  border: 1px solid #2a2a2a;
  border-radius: 14px;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #f3f4f6;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.upload-label {
  cursor: pointer;
  display: inline-flex;
}

.upload-input-hidden {
  display: none;
}

/* ===== Filter Toolbar ===== */
.filter-toolbar {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.search-input-wrap {
  position: relative;
  width: 280px;
}

.search-input-wrap .search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  pointer-events: none;
}

.search-input-wrap .shadcn-input {
  padding-left: 34px;
  padding-right: 30px;
}

.search-input-wrap .clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
}

.search-input-wrap .clear-btn:hover {
  color: #e5e7eb;
}

/* Dark input variant */
.dark-input {
  background: #171717 !important;
  border-color: #2f2f2f !important;
  color: #e5e7eb !important;
}

.dark-input::placeholder {
  color: #6b7280 !important;
}

.dark-input:hover {
  border-color: #4b5563 !important;
}

.dark-input:focus {
  border-color: #6b7280 !important;
  box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.15) !important;
}

/* Date Range */
.date-range-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
  position: relative;
}

.date-input {
  width: 140px;
  font-size: 13px;
}

.date-sep {
  color: #6b7280;
  font-size: 13px;
}

.date-range-wrap .clear-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
}

.date-range-wrap .clear-btn:hover {
  color: #e5e7eb;
}

.filter-summary {
  margin-left: auto;
  font-size: 12px;
  color: #9ca3af;
}

/* ===== Folder Grid ===== */
.folder-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

/* ===== Table ===== */
.table-wrap {
  margin-top: 16px;
  position: relative;
  min-height: 200px;
}

.shadcn-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.shadcn-table thead {
  background: #1a1a1a;
}

.shadcn-table th {
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  color: #cbd5e1;
  border-bottom: 1px solid #2a2a2a;
  white-space: nowrap;
}

.shadcn-table td {
  padding: 10px 14px;
  border-bottom: 1px solid #1f1f1f;
  color: #e5e7eb;
}

.shadcn-table tbody tr:hover {
  background: #1a1a1a;
}

.shadcn-table tbody tr.row-selected {
  background: rgba(139, 92, 246, 0.06);
}

.col-check {
  width: 48px;
}

.col-name {
  min-width: 200px;
}

.col-type {
  width: 110px;
}

.col-size {
  width: 100px;
}

.col-visibility {
  min-width: 250px;
}

.visibility-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-start;
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

:deep(.visibility-select .select-dropdown) {
  font-size: 12px;
}

.share-code {
  font-size: 12px;
  color: #93c5fd;
  border: 1px dashed rgba(59, 130, 246, 0.35);
  border-radius: 999px;
  padding: 2px 8px;
  cursor: pointer;
}

.col-status {
  width: 90px;
}

.col-time {
  width: 170px;
}

.col-actions {
  width: 180px;
}

/* Checkbox */
.shadcn-checkbox {
  width: 16px;
  height: 16px;
  accent-color: #0a0a0a;
  cursor: pointer;
}

/* File type tag */
.file-type-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.file-type-icon {
  flex-shrink: 0;
}

.file-type-text {
  line-height: 1;
}

/* Action buttons */
.action-btns {
  display: flex;
  gap: 6px;
}

/* ===== Empty State ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.empty-icon {
  color: #3a3a3f;
  margin-bottom: 12px;
}

.empty-text {
  color: #9ca3af;
  font-size: 14px;
}

/* ===== Dialog ===== */
.dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 5vh;
}

.dialog-panel {
  background: #111111;
  border: 1px solid #2a2a2a;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

.preview-dialog {
  width: 80vw;
  max-width: 1400px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #2a2a2a;
}

.dialog-title {
  font-size: 16px;
  font-weight: 600;
  color: #f3f4f6;
}

.dialog-close {
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

.dialog-close:hover {
  background: #1f1f1f;
  color: #f3f4f6;
}

.dialog-body {
  padding: 0;
  color: #e5e7eb;
}

/* ===== Preview ===== */
.preview-container {
  height: 75vh;
}

.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 12px;
}

.error-icon {
  color: #ef4444;
}

.error-title {
  font-size: 18px;
  font-weight: 600;
  color: #f3f4f6;
  margin: 0;
}

.error-desc {
  color: #9ca3af;
  font-size: 14px;
  margin: 0;
}

.pdf-preview {
  height: 75vh;
  display: flex;
  flex-direction: column;
}

.pdf-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-bottom: 1px solid #2a2a2a;
  background: #151515;
}

.btn-group {
  display: flex;
  border: 1px solid #333;
  border-radius: 8px;
  overflow: hidden;
}

.btn-group-item {
  padding: 5px 12px;
  font-size: 12px;
  background: #1a1a1a;
  color: #e5e7eb;
  border: none;
  border-right: 1px solid #333;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-group-item:last-child {
  border-right: none;
}

.btn-group-item:hover:not(:disabled) {
  background: #242424;
}

.btn-group-item:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pdf-page {
  font-size: 13px;
  color: #cbd5e1;
}

/* Slider */
.shadcn-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 200px;
  height: 4px;
  background: #333;
  border-radius: 999px;
  outline: none;
  cursor: pointer;
}

.shadcn-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #e5e7eb;
  border: 2px solid #555;
  cursor: pointer;
  transition: all 0.15s;
}

.shadcn-slider::-webkit-slider-thumb:hover {
  background: #fff;
  border-color: #888;
}

.pdf-zoom-text {
  font-size: 12px;
  color: #cbd5e1;
  min-width: 36px;
}

.pdf-pages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #0f0f10;
}

.pdf-canvas {
  display: block;
  margin: 0 auto 16px;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
  background: white;
}

.preview-iframe {
  width: 100%;
  height: 75vh;
  border: none;
}

.preview-onlyoffice-container {
  width: 100%;
  height: 75vh;
  background: #ffffff;
}

.preview-image {
  max-width: 100%;
  max-height: 75vh;
  display: block;
  margin: 0 auto;
}

.preview-video {
  width: 100%;
  height: 75vh;
}

.preview-unsupported {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 75vh;
  color: #9ca3af;
}

/* ===== Markdown Preview ===== */
.text-preview {
  padding: 24px 32px;
  overflow-y: auto;
  max-height: 75vh;
  background: #fff;
  border-radius: 8px;
}

.text-preview .markdown-body {
  color: #1f2937;
  font-size: 15px;
  line-height: 1.8;
}

.text-preview .markdown-body h1,
.text-preview .markdown-body h2,
.text-preview .markdown-body h3,
.text-preview .markdown-body h4 {
  margin: 1.2em 0 0.6em;
  font-weight: 700;
  color: #111827;
}

.text-preview .markdown-body h1 { font-size: 1.8em; }
.text-preview .markdown-body h2 { font-size: 1.5em; }
.text-preview .markdown-body h3 { font-size: 1.25em; }

.text-preview .markdown-body p {
  margin: 0.6em 0;
}

.text-preview .markdown-body ul,
.text-preview .markdown-body ol {
  padding-left: 2em;
  margin: 0.6em 0;
}

.text-preview .markdown-body code {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  color: #dc2626;
}

.text-preview .markdown-body pre {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1em 0;
}

.text-preview .markdown-body pre code {
  background: none;
  color: inherit;
  padding: 0;
}

.text-preview .markdown-body blockquote {
  border-left: 4px solid #d1d5db;
  padding: 8px 16px;
  margin: 1em 0;
  color: #6b7280;
  background: #f9fafb;
  border-radius: 0 6px 6px 0;
}

.text-preview .markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.text-preview .markdown-body th,
.text-preview .markdown-body td {
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  text-align: left;
}

.text-preview .markdown-body th {
  background: #f3f4f6;
  font-weight: 600;
}

.text-preview .markdown-body a {
  color: #2563eb;
  text-decoration: underline;
}

.text-preview .markdown-body img {
  max-width: 100%;
  border-radius: 6px;
}

.text-preview .markdown-body hr {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 1.5em 0;
}

/* ===== Responsive ===== */
@media (max-width: 900px) {
  .search-input-wrap {
    width: 100%;
  }

  .date-range-wrap {
    width: 100%;
  }

  .date-input {
    flex: 1;
  }

  .filter-summary {
    margin-left: 0;
    width: 100%;
  }

  .preview-dialog {
    width: 95vw;
  }
}
</style>
