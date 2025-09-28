<template>
  <div class="space-y-6">
    <!-- Configuration Form -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-semibold text-gray-800">Server Configuration</h3>
        <div class="flex space-x-2">
          <button
            @click="resetConfig"
            :disabled="!hasChanges || loading"
            class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50"
          >
            Reset
          </button>
          <button
            @click="saveConfig"
            :disabled="!hasChanges || loading"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Save Changes
          </button>
        </div>
      </div>
      
      <form @submit.prevent="saveConfig">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Basic Settings -->
          <div>
            <h4 class="text-md font-medium text-gray-700 mb-4">Basic Settings</h4>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Server Name</label>
                <input
                  v-model="config.server_name"
                  type="text"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Listen Port</label>
                <input
                  v-model.number="config.listen_port"
                  type="number"
                  min="1024"
                  max="65535"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Maximum Clients</label>
                <input
                  v-model.number="config.max_clients"
                  type="number"
                  min="1"
                  max="1000"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Character Slots</label>
                <select
                  v-model.number="config.character_slots"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option :value="1">1</option>
                  <option :value="2">2</option>
                  <option :value="3">3</option>
                  <option :value="4">4</option>
                  <option :value="5">5</option>
                  <option :value="6">6</option>
                  <option :value="7">7</option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- Access Control -->
          <div>
            <h4 class="text-md font-medium text-gray-700 mb-4">Access Control</h4>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Minimum Cmd Level to Login</label>
                <select
                  v-model.number="config.min_cmdlevel_to_login"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option :value="0">0 - Everyone</option>
                  <option :value="1">1 - Counselor+</option>
                  <option :value="2">2 - Seer+</option>
                  <option :value="3">3 - Game Master+</option>
                  <option :value="4">4 - Developer+</option>
                  <option :value="5">5 - Administrator only</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Inactivity Warning (minutes)</label>
                <input
                  v-model.number="config.inactivity_warning_timeout"
                  type="number"
                  min="1"
                  max="60"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Inactivity Disconnect (minutes)</label>
                <input
                  v-model.number="config.inactivity_disconnect_timeout"
                  type="number"
                  min="1"
                  max="120"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
          
          <!-- Game Features -->
          <div>
            <h4 class="text-md font-medium text-gray-700 mb-4">Game Features</h4>
            
            <div class="space-y-4">
              <label class="flex items-center">
                <input
                  v-model="config.require_spellbooks"
                  type="checkbox"
                  class="mr-2 rounded"
                />
                <span class="text-sm text-gray-700">Require Spellbooks</span>
              </label>
              
              <label class="flex items-center">
                <input
                  v-model="config.enable_secure_trading"
                  type="checkbox"
                  class="mr-2 rounded"
                />
                <span class="text-sm text-gray-700">Enable Secure Trading</span>
              </label>
            </div>
          </div>
          
          <!-- Web Server -->
          <div>
            <h4 class="text-md font-medium text-gray-700 mb-4">Web Server</h4>
            
            <div class="space-y-4">
              <label class="flex items-center">
                <input
                  v-model="config.web_server"
                  type="checkbox"
                  class="mr-2 rounded"
                />
                <span class="text-sm text-gray-700">Enable Web Server</span>
              </label>
              
              <div v-if="config.web_server">
                <label class="block text-sm font-medium text-gray-700">Web Server Port</label>
                <input
                  v-model.number="config.web_server_port"
                  type="number"
                  min="1024"
                  max="65535"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- Advanced Configuration -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Advanced Configuration</h3>
      
      <div class="space-y-4">
        <p class="text-sm text-gray-600">
          For advanced configuration options, you'll need to edit the pol.cfg file directly.
          Always backup your configuration before making changes.
        </p>
        
        <div class="flex space-x-4">
          <button
            @click="downloadConfig"
            class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Download pol.cfg
          </button>
          
          <button
            @click="openConfigEditor"
            class="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Open Config Editor
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { useServerStore } from '@/stores/server'

const toast = useToast()
const serverStore = useServerStore()

const loading = ref(false)
const config = ref({
  server_name: 'POL Server',
  listen_port: 5003,
  max_clients: 300,
  min_cmdlevel_to_login: 0,
  inactivity_warning_timeout: 9,
  inactivity_disconnect_timeout: 10,
  character_slots: 5,
  require_spellbooks: true,
  enable_secure_trading: true,
  web_server: false,
  web_server_port: 8080
})

const originalConfig = ref(null)

const hasChanges = computed(() => {
  if (!originalConfig.value) return false
  return JSON.stringify(config.value) !== JSON.stringify(originalConfig.value)
})

const fetchConfig = async () => {
  loading.value = true
  const result = await serverStore.fetchConfig()
  
  if (result.success) {
    config.value = { ...result.data }
    originalConfig.value = { ...result.data }
  } else {
    toast.error('Failed to load configuration')
  }
  
  loading.value = false
}

const saveConfig = async () => {
  loading.value = true
  const result = await serverStore.updateConfig(config.value)
  
  if (result.success) {
    toast.success('Configuration saved successfully')
    originalConfig.value = { ...config.value }
    
    // Prompt to restart server if it's running
    if (serverStore.status.running) {
      if (confirm('Configuration changes require a server restart. Restart now?')) {
        await serverStore.restartServer()
      }
    }
  } else {
    toast.error(result.error)
  }
  
  loading.value = false
}

const resetConfig = () => {
  if (originalConfig.value) {
    config.value = { ...originalConfig.value }
  }
}

const downloadConfig = () => {
  // Implementation would download the actual pol.cfg file
  toast.info('Downloading pol.cfg...')
}

const openConfigEditor = () => {
  // Implementation would open a text editor modal for pol.cfg
  toast.info('Config editor not implemented yet')
}

onMounted(() => {
  fetchConfig()
})
</script>