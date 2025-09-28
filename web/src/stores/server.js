import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useServerStore = defineStore('server', {
  state: () => ({
    status: {
      running: false,
      uptime: null,
      player_count: 0,
      max_players: 300,
      cpu_usage: 0,
      memory_usage: 0,
      last_save: null
    },
    logs: [],
    config: null,
    systemStats: null
  }),

  actions: {
    async fetchStatus() {
      try {
        const response = await api.get('/server/status')
        this.status = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async startServer() {
      try {
        await api.post('/server/start')
        await this.fetchStatus()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || 'Failed to start server' }
      }
    },

    async stopServer() {
      try {
        await api.post('/server/stop')
        await this.fetchStatus()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || 'Failed to stop server' }
      }
    },

    async restartServer() {
      try {
        await api.post('/server/restart')
        await this.fetchStatus()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || 'Failed to restart server' }
      }
    },

    async fetchLogs(lines = 100) {
      try {
        const response = await api.get(`/server/logs?lines=${lines}`)
        this.logs = response.data.logs
        return { success: true, data: response.data.logs }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async fetchConfig() {
      try {
        const response = await api.get('/config')
        this.config = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async updateConfig(config) {
      try {
        await api.put('/config', config)
        await this.fetchConfig()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || 'Failed to update config' }
      }
    },

    async fetchSystemStats() {
      try {
        const response = await api.get('/system/stats')
        this.systemStats = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { success: false, error: error.message }
      }
    }
  }
})