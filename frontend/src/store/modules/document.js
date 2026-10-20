import { defineStore } from 'pinia'

export const useDocumentStore = defineStore('document', {
  state: () => ({
    documents: [],
    uploadProgress: 0
  }),

  actions: {
    // Will be implemented in Phase 2
  }
})
