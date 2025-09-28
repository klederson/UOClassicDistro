import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: false
  }),

  getters: {
    getToken: (state) => state.token
  },

  actions: {
    async login(credentials) {
      try {
        const response = await api.post('/auth/login', credentials)
        const { access_token } = response.data
        
        this.token = access_token
        this.isAuthenticated = true
        
        localStorage.setItem('token', access_token)
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || 'Login failed' }
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    },

    checkAuth() {
      if (this.token) {
        this.isAuthenticated = true
        api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }
    }
  }
})