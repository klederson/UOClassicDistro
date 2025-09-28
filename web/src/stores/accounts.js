import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useAccountsStore = defineStore('accounts', {
  state: () => ({
    accounts: [],
    currentAccount: null,
    loading: false
  }),

  actions: {
    async fetchAccounts() {
      this.loading = true
      try {
        const response = await api.get('/accounts')
        this.accounts = response.data.accounts
        return { success: true, data: response.data.accounts }
      } catch (error) {
        return { success: false, error: error.message }
      } finally {
        this.loading = false
      }
    },

    async fetchAccount(username) {
      try {
        const response = await api.get(`/accounts/${username}`)
        this.currentAccount = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async createAccount(accountData) {
      try {
        await api.post('/accounts', accountData)
        await this.fetchAccounts()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || 'Failed to create account' }
      }
    },

    async updateAccount(username, accountData) {
      try {
        await api.put(`/accounts/${username}`, accountData)
        await this.fetchAccounts()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || 'Failed to update account' }
      }
    },

    async deleteAccount(username) {
      try {
        await api.delete(`/accounts/${username}`)
        await this.fetchAccounts()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || 'Failed to delete account' }
      }
    }
  }
})