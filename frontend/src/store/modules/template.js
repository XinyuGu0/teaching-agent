import { defineStore } from 'pinia'

export const useTemplateStore = defineStore('template', {
  state: () => ({
    templates: [],
    selectedTemplate: null
  }),

  actions: {
    // Will be implemented in Phase 4
  }
})
