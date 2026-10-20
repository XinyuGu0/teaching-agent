import { defineStore } from 'pinia'

export const usePPTStore = defineStore('ppt', {
  state: () => ({
    ppts: [],
    currentPPT: null,
    generationProgress: 0
  }),

  actions: {
    // Will be implemented in Phase 4
  }
})
