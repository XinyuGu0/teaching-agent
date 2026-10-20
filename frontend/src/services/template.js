import api from './api';

/**
 * 模板服务
 */
const templateService = {
  /**
   * 获取内置模板列表（硬编码数据，不查数据库）
   */
  async getBuiltinTemplates() {
    return api.get('/templates/builtin/');
  },

  /**
   * 上传内置模板封面图
   * @param {String} templateId - 内置模板ID（如 builtin_xxx）
   * @param {FormData} formData - 包含cover文件
   * @returns {Promise}
   */
  async uploadBuiltinTemplateCover(templateId, formData) {
    return api.post(`/templates/builtin/${templateId}/cover/`, formData);
  },

  /**
   * 获取内置模板封面图URL
   * @param {String} templateId - 内置模板ID（如 builtin_xxx）
   * @returns {String}
   */
  getBuiltinTemplateCoverUrl(templateId) {
    return `${api.defaults.baseURL}/templates/builtin/${templateId}/cover/`;
  },

  /**
   * 获取模板列表（用户上传的模板）
   * @param {Object} params - 查询参数 {category, type}
   * @returns {Promise}
   */
  async getTemplates(params = {}) {
    const queryParams = new URLSearchParams(params).toString();
    return api.get(`/templates/${queryParams ? '?' + queryParams : ''}`);
  },

  /**
   * 获取单个模板
   * @param {String} templateId - 模板ID
   * @returns {Promise}
   */
  async getTemplate(templateId) {
    return api.get(`/templates/${templateId}/`);
  },

  /**
   * 获取模板预览
   * @param {String} templateId - 模板ID
   * @returns {Promise}
   */
  async getTemplatePreview(templateId) {
    return api.get(`/templates/${templateId}/preview/`);
  },

  /**
   * 获取内置模板预览
   * @param {String} templateId - 内置模板ID
   * @returns {Promise}
   */
  async getBuiltinTemplatePreview(templateId) {
    return api.get(`/templates/builtin/${templateId}/preview/`);
  },

  /**
   * 上传模板缩略图
   * @param {String} templateId - 模板ID
   * @param {FormData} formData - 包含thumbnail文件
   * @returns {Promise}
   */
  async uploadTemplateThumbnail(templateId, formData) {
    return api.post(`/templates/${templateId}/thumbnail/`, formData);
  },

  /**
   * 获取模板缩略图URL
   * @param {String} templateId - 模板ID
   * @returns {String}
   */
  getTemplateThumbnailUrl(templateId) {
    return `${api.defaults.baseURL}/templates/${templateId}/thumbnail/`;
  },

  /**
   * 获取模板某一页预览图URL
   * @param {String} templateId - 模板ID
   * @param {Number} pageNumber - 页码（从1开始）
   * @returns {String}
   */
  getTemplateSlideImageUrl(templateId, pageNumber) {
    return `${api.defaults.baseURL}/templates/${templateId}/slides/${pageNumber}/image/`;
  },

  /**
   * 上传模板
   * @param {FormData} formData - 表单数据
   * @returns {Promise}
   */
  async uploadTemplate(formData) {
    // 不手动设置Content-Type，让axios自动设置正确的boundary
    return api.post('/templates/', formData);
  },

  /**
   * 更新模板
   * @param {String} templateId - 模板ID
   * @param {Object} data - 更新数据
   * @returns {Promise}
   */
  async updateTemplate(templateId, data) {
    return api.put(`/templates/${templateId}/`, data);
  },

  /**
   * 删除模板
   * @param {String} templateId - 模板ID
   * @returns {Promise}
   */
  async deleteTemplate(templateId) {
    return api.delete(`/templates/${templateId}/`);
  },

  /**
   * 获取所有分类
   * @returns {Promise}
   */
  async getCategories() {
    return api.get('/templates/categories/');
  },

  /**
   * 上传模板封面图片
   * @param {String} templateId - 模板ID
   * @param {FormData} formData - 包含cover文件
   * @returns {Promise}
   */
  async uploadTemplateCover(templateId, formData) {
    return api.post(`/templates/${templateId}/cover/`, formData);
  },

  /**
   * 保存自定义分析模板（关联到内置PPT文件）
   * @param {FormData} formData - 表单数据（name, description, category, preview_file, page_count, placeholder_count, cover）
   * @returns {Promise}
   */
  async saveAnalyzedTemplate(formData) {
    return api.post('/templates/analyze-save/', formData);
  },

  /**
   * 从PPT第一页自动提取封面
   * @param {String} templateId - 模板ID
   * @returns {Promise}
   */
  async extractTemplateCover(templateId) {
    return api.post(`/templates/${templateId}/extract-cover/`);
  },
};

export default templateService;
