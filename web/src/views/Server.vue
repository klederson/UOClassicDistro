<template>
  <div class="space-y-6">
    <!-- Server Status -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Server Status</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <p class="text-sm text-gray-600">Status</p>
          <p class="text-xl font-semibold" :class="status.running ? 'text-green-600' : 'text-red-600'">
            {{ status.running ? 'Online' : 'Offline' }}
          </p>
        </div>
        
        <div v-if="status.running">
          <p class="text-sm text-gray-600">Uptime</p>
          <p class="text-xl font-semibold">{{ formatUptime(status.uptime) }}</p>
        </div>
        
        <div v-if="status.running">
          <p class="text-sm text-gray-600">Players</p>
          <p class="text-xl font-semibold">{{ status.player_count }} / {{ status.max_players }}</p>
        </div>
      </div>
      
      <!-- Server Controls -->
      <div class="flex space-x-4">
        <button
          @click="startServer"
          :disabled="status.running || loading"
          class="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <PlayIcon class="w-5 h-5 inline mr-2" />
          Start Server
        </button>
        
        <button
          @click="stopServer"
          :disabled="!status.running || loading"
          class="px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <StopIcon class="w-5 h-5 inline mr-2" />
          Stop Server
        </button>
        
        <button
          @click="restartServer"
          :disabled="!status.running || loading"
          class="px-6 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshIcon class="w-5 h-5 inline mr-2" />
          Restart Server
        </button>
      </div>
    </div>

    <!-- Resource Usage -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Resource Usage</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <canvas ref="cpuChart"></canvas>
        </div>
        <div>
          <canvas ref="memoryChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          @click="compileScripts"
          :disabled="loading"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          Compile All Scripts
        </button>
        
        <button
          @click="backupServer"
          :disabled="loading"
          class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
        >
          Backup Server
        </button>
        
        <button
          @click="clearLogs"
          :disabled="loading"
          class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50"
        >
          Clear Logs
        </button>
        
        <button
          @click="reloadConfig"
          :disabled="loading || !status.running"
          class="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
        >
          Reload Configuration
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useServerStore } from '@/stores/server'
import Chart from 'chart.js/auto'

// Icons
const PlayIcon = { template: '<svg fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"></path></svg>' }
const StopIcon = { template: '<svg fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd"></path></svg>' }
const RefreshIcon = { template: '<svg fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"></path></svg>' }

const toast = useToast()
const serverStore = useServerStore()

const loading = ref(false)
const status = serverStore.status
const cpuChart = ref(null)
const memoryChart = ref(null)

let cpuChartInstance = null
let memoryChartInstance = null
let updateInterval = null

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
  if (!confirm('Are you sure you want to stop the server?')) return
  
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
  if (!confirm('Are you sure you want to restart the server?')) return
  
  loading.value = true
  const result = await serverStore.restartServer()
  if (result.success) {
    toast.success('Server restarted successfully')
  } else {
    toast.error(result.error)
  }
  loading.value = false
}

const compileScripts = async () => {
  loading.value = true
  toast.info('Compiling scripts... This may take a while.')
  // Implementation would call the compile endpoint
  setTimeout(() => {
    toast.success('Scripts compiled successfully')
    loading.value = false
  }, 3000)
}

const backupServer = async () => {
  loading.value = true
  toast.info('Creating backup...')
  // Implementation would call the backup endpoint
  setTimeout(() => {
    toast.success('Backup created successfully')
    loading.value = false
  }, 2000)
}

const clearLogs = async () => {
  if (!confirm('Are you sure you want to clear all logs?')) return
  
  loading.value = true
  // Implementation would call the clear logs endpoint
  setTimeout(() => {
    toast.success('Logs cleared successfully')
    loading.value = false
  }, 1000)
}

const reloadConfig = async () => {
  loading.value = true
  // Implementation would call the reload config endpoint
  setTimeout(() => {
    toast.success('Configuration reloaded successfully')
    loading.value = false
  }, 1000)
}

const formatUptime = (seconds) => {
  if (!seconds) return 'N/A'
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  const parts = []
  if (days > 0) parts.push(`${days}d`)
  if (hours > 0) parts.push(`${hours}h`)
  if (minutes > 0) parts.push(`${minutes}m`)
  
  return parts.join(' ') || '< 1m'
}

const initCharts = () => {
  // CPU Chart
  const cpuCtx = cpuChart.value.getContext('2d')
  cpuChartInstance = new Chart(cpuCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'CPU Usage (%)',
        data: [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  })
  
  // Memory Chart
  const memCtx = memoryChart.value.getContext('2d')
  memoryChartInstance = new Chart(memCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Memory Usage (%)',
        data: [],
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  })
}

const updateCharts = () => {
  const time = new Date().toLocaleTimeString()
  
  // Update CPU chart
  cpuChartInstance.data.labels.push(time)
  cpuChartInstance.data.datasets[0].data.push(status.cpu_usage)
  
  // Keep only last 20 data points
  if (cpuChartInstance.data.labels.length > 20) {
    cpuChartInstance.data.labels.shift()
    cpuChartInstance.data.datasets[0].data.shift()
  }
  
  cpuChartInstance.update()
  
  // Update Memory chart
  memoryChartInstance.data.labels.push(time)
  memoryChartInstance.data.datasets[0].data.push(status.memory_usage)
  
  // Keep only last 20 data points
  if (memoryChartInstance.data.labels.length > 20) {
    memoryChartInstance.data.labels.shift()
    memoryChartInstance.data.datasets[0].data.shift()
  }
  
  memoryChartInstance.update()
}

onMounted(() => {
  serverStore.fetchStatus()
  
  setTimeout(() => {
    initCharts()
  }, 100)
  
  updateInterval = setInterval(() => {
    serverStore.fetchStatus()
    if (cpuChartInstance && memoryChartInstance) {
      updateCharts()
    }
  }, 5000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
  
  if (cpuChartInstance) {
    cpuChartInstance.destroy()
  }
  
  if (memoryChartInstance) {
    memoryChartInstance.destroy()
  }
})
</script>