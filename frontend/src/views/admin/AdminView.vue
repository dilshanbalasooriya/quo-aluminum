<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useToastStore } from '@/stores/toastStore'

const authStore = useAuthStore()
const toastStore = useToastStore()

// Mock data to test state rendering
const systemStats = ref([
  { label: 'Active Profiles', value: '24 Extrusions', change: '+2 this week' },
  { label: 'Hardware Items', value: '142 Items', change: 'Up to date' },
  { label: 'Saved Templates', value: '8 Formats', change: '2 sliding / 6 casement' },
  { label: 'Quotes Today', value: '12 Generated', change: '$4,280 Total Value' }
])

const recentProfiles = ref([
  { code: 'SD-01', name: 'Sliding Door Outer Frame', rate: '$12.50 / m', status: 'Active' },
  { code: 'CW-04', name: 'Casement Window Sash', rate: '$8.20 / m', status: 'Active' },
  { code: 'FD-02', name: 'Fixed Glass Bead 12mm', rate: '$3.10 / m', status: 'Draft' }
])

// Interactive Toast Test Trigger Functions
function testToast(type: 'success' | 'error' | 'warning' | 'info') {
  if (type === 'success') {
    toastStore.success('Profile rate saved successfully!')
  } else if (type === 'error') {
    toastStore.error('Failed to connect to FastAPI backend (500 Error).')
  } else if (type === 'warning') {
    toastStore.warning('Stock level low for Rubber Seal EPDM-01.')
  } else {
    toastStore.info('System maintenance scheduled for 10:00 PM.')
  }
}
</script>

<template>
  <div class="space-y-6">

    <!-- Header Banner -->
    <div class="p-6 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
          Admin Control Center
        </h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Logged in as <strong class="text-slate-800 dark:text-slate-200">{{ authStore.user?.username }}</strong> 
          (<span class="text-sky-600 dark:text-sky-400 font-bold uppercase">{{ authStore.user?.role }}</span>)
        </p>
      </div>

      <div class="flex items-center space-x-2">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
          <span class="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
          Role Guards Working
        </span>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div 
        v-for="(stat, idx) in systemStats" 
        :key="idx"
        class="p-5 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm"
      >
        <div class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1">
          {{ stat.label }}
        </div>
        <div class="text-2xl font-bold text-slate-900 dark:text-white">
          {{ stat.value }}
        </div>
        <div class="text-xs text-sky-600 dark:text-sky-400 mt-2 font-medium">
          {{ stat.change }}
        </div>
      </div>
    </div>

    <!-- Interactive Shell Testing Section -->
    <div class="p-6 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
      <h3 class="text-lg font-bold text-slate-900 dark:text-white">
        Global Component & Toast Testing
      </h3>
      <p class="text-sm text-slate-500 dark:text-slate-400">
        Click the buttons below to fire reactive alerts into `AppToast.vue` via `toastStore`:
      </p>

      <div class="flex flex-wrap gap-3 pt-2">
        <button 
          @click="testToast('success')"
          class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm rounded-xl transition shadow-sm focus:outline-none"
        >
          Test Success Toast
        </button>

        <button 
          @click="testToast('error')"
          class="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white font-medium text-sm rounded-xl transition shadow-sm focus:outline-none"
        >
          Test Error Toast
        </button>

        <button 
          @click="testToast('warning')"
          class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm rounded-xl transition shadow-sm focus:outline-none"
        >
          Test Warning Toast
        </button>

        <button 
          @click="testToast('info')"
          class="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white font-medium text-sm rounded-xl transition shadow-sm focus:outline-none"
        >
          Test Info Toast
        </button>
      </div>
    </div>

    <!-- Data Table Prototype -->
    <div class="p-6 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-bold text-slate-900 dark:text-white">
          Profile Rates Overview
        </h3>
        <button class="text-xs font-semibold text-sky-600 dark:text-sky-400 hover:underline">
          View All Profiles &rarr;
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="border-b border-slate-200 dark:border-slate-700 text-slate-400 dark:text-slate-500 text-xs uppercase">
            <tr>
              <th class="py-3 px-4">Code</th>
              <th class="py-3 px-4">Name</th>
              <th class="py-3 px-4">Rate</th>
              <th class="py-3 px-4">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700/50">
            <tr v-for="item in recentProfiles" :key="item.code" class="hover:bg-slate-50 dark:hover:bg-slate-700/30">
              <td class="py-3.5 px-4 font-mono font-bold text-slate-900 dark:text-white">{{ item.code }}</td>
              <td class="py-3.5 px-4 text-slate-700 dark:text-slate-300">{{ item.name }}</td>
              <td class="py-3.5 px-4 font-medium text-slate-900 dark:text-white">{{ item.rate }}</td>
              <td class="py-3.5 px-4">
                <span 
                  class="px-2.5 py-1 text-xs rounded-full font-semibold"
                  :class="item.status === 'Active' ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'"
                >
                  {{ item.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>