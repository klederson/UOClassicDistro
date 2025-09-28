<template>
  <div class="space-y-6">
    <!-- Controls -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <select
            v-model="logLines"
            @change="fetchLogs"
            class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option :value="50">Last 50 lines</option>
            <option :value="100">Last 100 lines</option>
            <option :value="500">Last 500 lines</option>
            <option :value="1000">Last 1000 lines</option>
          </select>
          
          <button
            @click="toggleAutoRefresh"
            class="px-4 py-2 rounded"
            :class="autoRefresh ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'"
          >
            Auto-refresh: {{ autoRefresh ? 'ON' : 'OFF' }}
          </button>
        </div>
        
        <button
          @click="fetchLogs"
          :disabled="loading"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          <RefreshIcon class="w-5 h-5 inline mr-2" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Log Viewer -->
    <div class="bg-gray-900 rounded-lg shadow overflow-hidden">
      <div class="p-4">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-semibold text-white">Server Logs</h3>
          <div class="flex items-center space-x-2">
            <input
              v-model="searchTerm"
              type="text"
              placeholder="Search logs..."
              class="px-3 py-1 bg-gray-800 text-white border border-gray-700 rounded focus:outline-none focus:border-blue-500"
            />
            <button
              @click="downloadLogs"
              class="px-3 py-1 bg-gray-700 text-white rounded hover:bg-gray-600"
            >
              <DownloadIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div
          ref="logContainer"
          class="bg-black rounded p-4 h-96 overflow-y-auto font-mono text-sm"
          @scroll="handleScroll"
        >
          <div v-if="loading" class="text-gray-400">
            Loading logs...
          </div>
          
          <div v-else-if="filteredLogs.length === 0" class="text-gray-400">
            No logs found
          </div>
          
          <div v-else>
            <div
              v-for="(log, index) in filteredLogs"
              :key="index"
              class="whitespace-pre-wrap break-words"
              :class="getLogClass(log)"
            >
              {{ log }}
            </div>
          </div>
        </div>
        
        <div class="mt-2 flex items-center justify-between text-sm text-gray-400">
          <span>{{ filteredLogs.length }} lines</span>
          <label class="flex items-center">
            <input
              v-model="scrollToBottom"
              type="checkbox"
              class="mr-2"
            />
            Auto-scroll to bottom
          </label>
        </div>
      </div>
    </div>

    <!-- Real-time Log Stream -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Real-time Log Stream</h3>
      
      <div class="bg-gray-100 rounded p-4 h-64 overflow-y-auto font-mono text-sm">
        <div v-if="!wsConnected" class="text-gray-500">
          Connecting to log stream...
        </div>
        <div v-else-if="realtimeLogs.length === 0" class="text-gray-500">
          Waiting for new logs...
        </div>
        <div v-else>
          <div
            v-for="(log, index) in realtimeLogs"
            :key="index"
            class="whitespace-pre-wrap break-words"
            :class="getLogClass(log)"
          >
            {{ log }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useServerStore } from '@/stores/server'

// Icons
const RefreshIcon = { template: '<svg fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"></path></svg>' }
const DownloadIcon = { template: '<svg fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>' }

const serverStore = useServerStore()

const loading = ref(false)
const logs = ref([])
const realtimeLogs = ref([])
const logLines = ref(100)
const autoRefresh = ref(false)
const scrollToBottom = ref(true)
const searchTerm = ref('')
const wsConnected = ref(false)
const logContainer = ref(null)

let refreshInterval = null
let ws = null

const filteredLogs = computed(() => {
  if (!searchTerm.value) return logs.value
  
  const term = searchTerm.value.toLowerCase()
  return logs.value.filter(log => log.toLowerCase().includes(term))
})

const getLogClass = (log) => {
  const lowerLog = log.toLowerCase()
  
  if (lowerLog.includes('error') || lowerLog.includes('fail')) {
    return 'text-red-400'
  } else if (lowerLog.includes('warning') || lowerLog.includes('warn')) {
    return 'text-yellow-400'
  } else if (lowerLog.includes('success') || lowerLog.includes('started')) {
    return 'text-green-400'
  } else if (lowerLog.includes('info')) {
    return 'text-blue-400'
  }
  
  return 'text-gray-300'
}

const fetchLogs = async () => {
  loading.value = true
  const result = await serverStore.fetchLogs(logLines.value)
  
  if (result.success) {
    logs.value = result.data
    
    if (scrollToBottom.value) {
      await nextTick()
      scrollToEnd()
    }
  }
  
  loading.value = false
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value) {
    refreshInterval = setInterval(fetchLogs, 2000)
  } else {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }
}

const scrollToEnd = () => {
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

const handleScroll = () => {
  if (!logContainer.value) return
  
  const { scrollTop, scrollHeight, clientHeight } = logContainer.value
  const isAtBottom = scrollHeight - scrollTop === clientHeight
  
  if (!isAtBottom) {
    scrollToBottom.value = false
  }
}

const downloadLogs = () => {
  const content = logs.value.join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `pol-logs-${new Date().toISOString()}.txt`
  a.click()
  window.URL.revokeObjectURL(url)
}

const connectWebSocket = () => {
  ws = new WebSocket('ws://localhost:8001/ws/logs')
  
  ws.onopen = () => {
    wsConnected.value = true
    realtimeLogs.value = []
  }
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.logs) {
      realtimeLogs.value = data.logs.slice(-20) // Keep last 20 lines
    }
  }
  
  ws.onclose = () => {
    wsConnected.value = false
    // Reconnect after 5 seconds
    setTimeout(connectWebSocket, 5000)
  }
  
  ws.onerror = () => {
    wsConnected.value = false
  }
}

onMounted(() => {
  fetchLogs()
  connectWebSocket()
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  
  if (ws) {
    ws.close()
  }
})
</script>