import { defineStore } from 'pinia'

const THEME_KEY = 'theme_mode'

const resolveSystemTheme = () => {
  if (typeof window === 'undefined' || !window.matchMedia) return 'dark'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const applyThemeToDOM = (mode) => {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  root.setAttribute('data-theme', mode)
  root.classList.toggle('theme-dark', mode === 'dark')
  root.classList.toggle('theme-light', mode === 'light')
  root.style.colorScheme = mode
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    mode: 'dark'
  }),

  getters: {
    isDark: (state) => state.mode === 'dark'
  },

  actions: {
    initTheme() {
      const saved = localStorage.getItem(THEME_KEY)
      const mode = saved === 'light' || saved === 'dark' ? saved : resolveSystemTheme()
      this.mode = mode
      applyThemeToDOM(mode)
    },

    setTheme(mode) {
      const nextMode = mode === 'light' ? 'light' : 'dark'
      this.mode = nextMode
      localStorage.setItem(THEME_KEY, nextMode)
      applyThemeToDOM(nextMode)
    },

    toggleTheme() {
      this.setTheme(this.mode === 'dark' ? 'light' : 'dark')
    }
  }
})
