<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-semibold text-gray-800">Account Management</h2>
      <button
        @click="showCreateModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Create Account
      </button>
    </div>

    <!-- Accounts Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Username
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Email
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Cmd Level
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Characters
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Last Login
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="account in accounts" :key="account.username">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {{ account.username }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ account.email || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ account.cmdlevel }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                :class="{
                  'bg-green-100 text-green-800': account.status === 'active',
                  'bg-red-100 text-red-800': account.status === 'banned',
                  'bg-yellow-100 text-yellow-800': account.status === 'suspended'
                }"
              >
                {{ account.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ account.character_count || 0 }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(account.last_login) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button
                @click="editAccount(account)"
                class="text-indigo-600 hover:text-indigo-900 mr-3"
              >
                Edit
              </button>
              <button
                @click="deleteAccount(account.username)"
                class="text-red-600 hover:text-red-900"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="loading" class="text-center py-4">
        Loading accounts...
      </div>
      
      <div v-if="!loading && accounts.length === 0" class="text-center py-4 text-gray-500">
        No accounts found
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <AccountModal
      v-if="showCreateModal || selectedAccount"
      :account="selectedAccount"
      @close="closeModal"
      @save="saveAccount"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useAccountsStore } from '@/stores/accounts'
import AccountModal from '@/components/AccountModal.vue'

const toast = useToast()
const accountsStore = useAccountsStore()

const accounts = ref([])
const loading = ref(false)
const showCreateModal = ref(false)
const selectedAccount = ref(null)

const fetchAccounts = async () => {
  loading.value = true
  const result = await accountsStore.fetchAccounts()
  if (result.success) {
    accounts.value = result.data
  } else {
    toast.error('Failed to load accounts')
  }
  loading.value = false
}

const editAccount = (account) => {
  selectedAccount.value = account
}

const deleteAccount = async (username) => {
  if (!confirm(`Are you sure you want to delete account "${username}"?`)) {
    return
  }
  
  const result = await accountsStore.deleteAccount(username)
  if (result.success) {
    toast.success('Account deleted successfully')
    fetchAccounts()
  } else {
    toast.error(result.error)
  }
}

const saveAccount = async (accountData) => {
  let result
  
  if (selectedAccount.value) {
    result = await accountsStore.updateAccount(selectedAccount.value.username, accountData)
  } else {
    result = await accountsStore.createAccount(accountData)
  }
  
  if (result.success) {
    toast.success(selectedAccount.value ? 'Account updated successfully' : 'Account created successfully')
    closeModal()
    fetchAccounts()
  } else {
    toast.error(result.error)
  }
}

const closeModal = () => {
  showCreateModal.value = false
  selectedAccount.value = null
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleString()
  } catch {
    return dateString
  }
}

onMounted(() => {
  fetchAccounts()
})
</script>