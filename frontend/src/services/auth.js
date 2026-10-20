import api from './api'

export default {
  register(username, email, password) {
    return api.post('/auth/register', { username, email, password })
  },

  login(username, password) {
    return api.post('/auth/login', { username, password })
  },

  refresh() {
    return api.post('/auth/refresh')
  },

  getCurrentUser() {
    return api.get('/auth/me')
  },

  getProfile() {
    return api.get('/auth/profile')
  },

  updateProfile(payload) {
    return api.put('/auth/profile', payload)
  },

  uploadAvatar(file) {
    const formData = new FormData()
    formData.append('avatar', file)
    return api.post('/auth/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  suggestSchools(keyword) {
    return api.get('/auth/schools/suggest', { params: { q: keyword } })
  },

  logout() {
    return api.post('/auth/logout')
  }
}
