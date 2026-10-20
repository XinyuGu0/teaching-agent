/**
 * 认证状态管理模块
 * 基于 Pinia 管理用户登录态、JWT 令牌存储与自动刷新
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  // ---- 状态 ----
  const token = ref(localStorage.getItem('access_token') || '')
  const user = ref(null)

  // ---- 计算属性 ----
  const isAuthenticated = computed(() => !!token.value)

  /**
   * 用户登录
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @returns {Object} 用户信息
   */
  async function login(username, password) {
    const res = await api.post('/api/auth/login', { username, password })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('access_token', token.value)
    return res.data
  }

  /**
   * 用户注册
   * @param {Object} params - 注册参数 { username, email, password }
   * @returns {Object} 用户信息
   */
  async function register(params) {
    const res = await api.post('/api/auth/register', params)
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('access_token', token.value)
    return res.data
  }

  /** 退出登录，清除本地令牌 */
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('access_token')
  }

  /**
   * 获取当前用户信息（用于页面刷新后恢复会话）
   */
  async function fetchUser() {
    if (!token.value) return null
    try {
      const res = await api.get('/api/auth/me')
      user.value = res.data.user
      return res.data.user
    } catch {
      logout()
      return null
    }
  }

  /**
   * 更新用户画像
   * @param {Object} profile - 画像数据
   */
  async function updateProfile(profile) {
    const res = await api.put('/api/auth/profile', profile)
    user.value = res.data.user
    return res.data
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser,
    updateProfile,
  }
})