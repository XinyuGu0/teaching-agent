/**
 * 社区功能 API 服务层（前端演示占位）
 * 后端接口上线后可直接启用
 */
import api from './api'

export function createKbShare(data) {
  return api.post('/community/kb/share', data)
}

export function getMyKbShares() {
  return api.get('/community/kb/my-shares')
}

export function updateKbShare(id, data) {
  return api.put(`/community/kb/share/${id}`, data)
}

export function deleteKbShare(id) {
  return api.delete(`/community/kb/share/${id}`)
}

export function getKbShareByCode(code) {
  return api.get(`/community/kb/share/${code}`)
}

export function importKb(data) {
  return api.post('/community/kb/import', data)
}

export function exploreKb(params = {}) {
  return api.get('/community/kb/explore', { params })
}

export function getKbExploreDetail(id) {
  return api.get(`/community/kb/explore/${id}`)
}

export function getCommunityTemplates(params = {}) {
  return api.get('/community/templates', { params })
}

export function getCommunityTemplateDetail(id) {
  return api.get(`/community/templates/${id}`)
}

export function toggleTemplateLike(id) {
  return api.post(`/community/templates/${id}/like`)
}

export function downloadCommunityTemplate(id) {
  return api.post(`/community/templates/${id}/download`)
}

export function shareTemplate(data) {
  return api.post('/community/templates/share', data)
}

export function getTemplateByCode(code) {
  return api.get(`/community/templates/code/${code}`)
}

export function getHotTags() {
  return api.get('/community/tags')
}

export function getCommunityStats() {
  return api.get('/community/stats')
}
