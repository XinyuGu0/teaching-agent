import { defineStore } from 'pinia'
import authService from '@/services/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    currentUser: (state) => state.user
  },

  actions: {
    async register(username, email, password) {
      try {
        const response = await authService.register(username, email, password)
        const { access_token, refresh_token, user } = response.data

        this.accessToken = access_token
        this.refreshToken = refresh_token
        this.user = user

        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)

        return response.data
      } catch (error) {
        throw error.response?.data || error
      }
    },

    async login(username, password) {
      try {
        const response = await authService.login(username, password)
        const { access_token, refresh_token, user } = response.data

        this.accessToken = access_token
        this.refreshToken = refresh_token
        this.user = user

        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)

        return user
      } catch (error) {
        throw error.response?.data || error
      }
    },

    async fetchCurrentUser() {
      try {
        const response = await authService.getCurrentUser()
        this.user = response.data.user
        return this.user
      } catch (error) {
        this.logout()
        throw error
      }
    },

    logout() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }
})
