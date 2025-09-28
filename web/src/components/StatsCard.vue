<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600">{{ title }}</p>
        <p class="mt-2 text-2xl font-semibold text-gray-900">{{ value }}</p>
      </div>
      <div
        class="p-3 rounded-full"
        :class="colorClasses"
      >
        <component :is="icon" class="w-6 h-6 text-white" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  value: String,
  icon: Object,
  color: {
    type: String,
    default: 'blue'
  }
})

const colorClasses = computed(() => {
  const colors = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
    purple: 'bg-purple-500'
  }
  return colors[props.color] || colors.blue
})
</script>