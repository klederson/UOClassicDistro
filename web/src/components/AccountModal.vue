<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <h3 class="text-lg font-bold text-gray-900 mb-4">
        {{ account ? 'Edit Account' : 'Create Account' }}
      </h3>
      
      <form @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Username</label>
            <input
              v-model="form.username"
              type="text"
              :disabled="!!account"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div v-if="!account">
            <label class="block text-sm font-medium text-gray-700">Password</label>
            <input
              v-model="form.password"
              type="password"
              required
              minlength="6"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Email</label>
            <input
              v-model="form.email"
              type="email"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Command Level</label>
            <select
              v-model="form.cmdlevel"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option :value="0">0 - Player</option>
              <option :value="1">1 - Counselor</option>
              <option :value="2">2 - Seer</option>
              <option :value="3">3 - Game Master</option>
              <option :value="4">4 - Developer</option>
              <option :value="5">5 - Administrator</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Expansion</label>
            <select
              v-model="form.expansion"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="T2A">T2A</option>
              <option value="LBR">LBR</option>
              <option value="AOS">AOS</option>
              <option value="SE">SE</option>
              <option value="ML">ML</option>
              <option value="SA">SA</option>
              <option value="HS">HS</option>
              <option value="TOL">TOL</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Status</label>
            <select
              v-model="form.status"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
              <option value="banned">Banned</option>
            </select>
          </div>
        </div>
        
        <div class="mt-6 flex justify-end space-x-3">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {{ account ? 'Update' : 'Create' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  account: Object
})

const emit = defineEmits(['close', 'save'])

const form = ref({
  username: '',
  password: '',
  email: '',
  cmdlevel: 0,
  expansion: 'ML',
  status: 'active'
})

watch(() => props.account, (newAccount) => {
  if (newAccount) {
    form.value = {
      username: newAccount.username,
      password: '', // Don't show existing password
      email: newAccount.email || '',
      cmdlevel: newAccount.cmdlevel || 0,
      expansion: newAccount.expansion || 'ML',
      status: newAccount.status || 'active'
    }
  }
}, { immediate: true })

const handleSubmit = () => {
  const data = { ...form.value }
  if (props.account && !data.password) {
    delete data.password // Don't send empty password on update
  }
  emit('save', data)
}
</script>