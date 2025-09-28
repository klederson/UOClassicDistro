<template>
  <div class="space-y-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatsCard
        title="Server Status"
        :value="serverStatus.running ? 'Online' : 'Offline'"
        :icon="ServerIcon"
        :color="serverStatus.running ? 'green' : 'red'"
      />
      
      <StatsCard
        title="Players Online"
        :value="`${serverStatus.player_count} / ${serverStatus.max_players}`"
        :icon="UsersIcon"
        color="blue"
      />
      
      <StatsCard
        title="CPU Usage"
        :value="`${serverStatus.cpu_usage.toFixed(1)}%`"
        :icon="CpuIcon"
        color="yellow"
      />
      
      <StatsCard
        title="Memory Usage"
        :value="`${serverStatus.memory_usage.toFixed(1)}%`"
        :icon="MemoryIcon"
        color="purple"
      />
    </div>

    <!-- Server Control -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Server Control</h3>
      
      <div class="flex space-x-4">
        <button
          @click="startServer"
          :disabled="serverStatus.running || loading"
          class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Start Server
        </button>
        
        <button
          @click="stopServer"
          :disabled="!serverStatus.running || loading"
          class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Stop Server
        </button>
        
        <button
          @click="restartServer"
          :disabled="!serverStatus.running || loading"
          class="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Restart Server
        </button>
      </div>
      
      <div v-if="serverStatus.running && serverStatus.uptime" class="mt-4 text-sm text-gray-600">
        Uptime: {{ formatUptime(serverStatus.uptime) }}
      </div>
    </div>

    <!-- System Resources -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">System Resources</h3>
        
        <div v-if="systemStats" class="space-y-4">
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span>CPU</span>
              <span>{{ systemStats.cpu_percent }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full"
                :style="`width: ${systemStats.cpu_percent}%`"
              ></div>
            </div>
          </div>
          
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span>Memory</span>
              <span>{{ formatBytes(systemStats.memory.used) }} / {{ formatBytes(systemStats.memory.total) }}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-green-600 h-2 rounded-full"
                :style="`width: ${systemStats.memory.percent}%`"
              ></div>
            </div>
          </div>
          
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span>Disk</span>
              <span>{{ formatBytes(systemStats.disk.used) }} / {{ formatBytes(systemStats.disk.total) }}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-purple-600 h-2 rounded-full"
                :style="`width: ${systemStats.disk.percent}%`"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Logs -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Recent Logs</h3>
        
        <div class="space-y-2 max-h-64 overflow-y-auto">
          <div
            v-for="(log, index) in recentLogs"
            :key="index"
            class="text-sm text-gray-600 font-mono"
          >
            {{ log }}
          </div>
          <div v-if="recentLogs.length === 0" class="text-gray-400">
            No logs available
          </div>
        </div>
        
        <router-link
          to="/logs"
          class="mt-4 inline-block text-sm text-blue-600 hover:text-blue-800"
        >
          View all logs →
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useServerStore } from '@/stores/server'
import StatsCard from '@/components/StatsCard.vue'

// Icons
const ServerIcon = { template: '<svg fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M2 5a2 2 0 012-2h12a2 2 0 012 2v2a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm14 1a1 1 0 11-2 0 1 1 0 012 0zM2 13a2 2 0 012-2h12a2 2 0 012 2v2a2 2 0 01-2 2H4a2 2 0 01-2-2v-2zm14 1a1 1 0 11-2 0 1 1 0 012 0z" clip-rule="evenodd"></path></svg>' }
const UsersIcon = { template: '<svg fill="currentColor" viewBox="0 0 20 20"><path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"></path></svg>' }
const CpuIcon = { template: '<svg fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M13 7H7v6h6V7z" clip-rule="evenodd"></path><path fill-rule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2z" clip-rule="evenodd"></path></svg>' }
const MemoryIcon = { template: '<svg fill="currentColor" viewBox="0 0 20 20"><path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"></path></svg>' }

const toast = useToast()
const serverStore = useServerStore()

const loading = ref(false)
const serverStatus = serverStore.status
const systemStats = ref(null)
const recentLogs = ref([])

let statusInterval
let statsInterval

const startServer = async () => {
  loading.value = true
  const result = await serverStore.startServer()
  if (result.success) {
    toast.success('Server started successfully')
  } else {
    toast.error(result.error)
  }
  loading.value = false
}

const stopServer = async () => {
  loading.value = true
  const result = await serverStore.stopServer()
  if (result.success) {
    toast.success('Server stopped successfully')
  } else {
    toast.error(result.error)
  }
  loading.value = false
}

const restartServer = async () => {
  loading.value = true
  const result = await serverStore.restartServer()
  if (result.success) {
    toast.success('Server restarted successfully')
  } else {
    toast.error(result.error)
  }
  loading.value = false
}

const formatUptime = (seconds) => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  const parts = []
  if (days > 0) parts.push(`${days}d`)
  if (hours > 0) parts.push(`${hours}h`)
  if (minutes > 0) parts.push(`${minutes}m`)
  
  return parts.join(' ') || '< 1m'
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const fetchData = async () => {
  await serverStore.fetchStatus()
  
  const statsResult = await serverStore.fetchSystemStats()
  if (statsResult.success) {
    systemStats.value = statsResult.data
  }
  
  const logsResult = await serverStore.fetchLogs(10)
  if (logsResult.success) {
    recentLogs.value = logsResult.data
  }
}

onMounted(() => {
  fetchData()
  
  statusInterval = setInterval(() => {
    serverStore.fetchStatus()
  }, 5000)
  
  statsInterval = setInterval(() => {
    fetchData()
  }, 10000)
})

onUnmounted(() => {
  if (statusInterval) clearInterval(statusInterval)
  if (statsInterval) clearInterval(statsInterval)
})
</script>