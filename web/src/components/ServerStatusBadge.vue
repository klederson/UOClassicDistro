<template>
  <div class="flex items-center space-x-2">
    <div class="flex items-center">
      <div
        class="w-3 h-3 rounded-full mr-2"
        :class="status.running ? 'bg-green-500' : 'bg-red-500'"
      ></div>
      <span class="text-sm font-medium text-gray-700">
        Server: {{ status.running ? 'Online' : 'Offline' }}
      </span>
    </div>
    
    <div v-if="status.running" class="text-sm text-gray-500">
      <span>Players: {{ status.player_count }}/{{ status.max_players }}</span>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useServerStore } from '@/stores/server'

const serverStore = useServerStore()
const status = serverStore.status

let interval

onMounted(() => {
  serverStore.fetchStatus()
  interval = setInterval(() => {
    serverStore.fetchStatus()
  }, 5000) // Update every 5 seconds
})

onUnmounted(() => {
  if (interval) {
    clearInterval(interval)
  }
})
</script>