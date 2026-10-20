import api from './api'

const memoryService = {
  getConversationMemory(conversationId) {
    return api.get(`/conversations/${conversationId}/memory`)
  },

  updateMemoryItem(conversationId, key, value) {
    return api.patch(`/conversations/${conversationId}/memory/${key}`, { value })
  },

  updateMemoryItem(conversationId, key, value) {
    return api.patch(`/conversations/${conversationId}/memory/${key}`, { value })
  },

  deleteMemoryItem(conversationId, key) {
    return api.delete(`/conversations/${conversationId}/memory/${key}`)
  }
}

export default memoryService
