<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/axios'
import { useToastStore } from '@/stores/toastStore'

interface AdminStats {
  daily_sales: number
  monthly_revenue: number
  total_users: number
  active_profiles: number
}

const stats = ref<AdminStats>({
  daily_sales: 0,
  monthly_revenue: 0,
  total_users: 0,
  active_profiles: 0,
})
const loading = ref(true)
const toast = useToastStore()

async function fetchStats() {
  try {
    // Adjust endpoint name to match your specific backend route (e.g., /admin/stats)
    const response = await apiClient.get<AdminStats>('/admin/stats')
    stats.value = response.data
  } catch (error) {
    toast.error('Failed to load dashboard statistics.')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Admin Dashboard</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400">Overview of system performance, sales, and catalog metrics.</p>
      </div>
      <button 
        @click="fetchStats"
        class="px-4 py-2 bg-slate-900 hover:bg-slate-800 dark:bg-sky-600 dark:hover:bg-sky-500 text-white text-sm font-medium rounded-xl transition-colors shadow-sm"
      >
        Refresh Stats
      </button>
    </div>

    <!-- KPI Metric Cards Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Daily Sales -->
      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Daily Sales</span>
          <svg class="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="text-3xl font-bold text-slate-900 dark:text-white">
          {{ loading ? '...' : `$${stats.daily_sales.toLocaleString()}` }}
        </div>
        <span class="text-xs text-emerald-500 font-medium mt-1 inline-block">Updated just now</span>
      </div>

      <!-- Monthly Revenue -->
      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Monthly Revenue</span>
          <svg class="w-5 h-5 text-sky-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
        <div class="text-3xl font-bold text-slate-900 dark:text-white">
          {{ loading ? '...' : `$${stats.monthly_revenue.toLocaleString()}` }}
        </div>
        <span class="text-xs text-sky-500 font-medium mt-1 inline-block">Current cycle</span>
      </div>

      <!-- Total Users -->
      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Registered Users</span>
          <svg class="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <div class="text-3xl font-bold text-slate-900 dark:text-white">
          {{ loading ? '...' : stats.total_users }}
        </div>
        <span class="text-xs text-slate-400 mt-1 inline-block">Workers & Admins</span>
      </div>

      <!-- Active Profiles -->
      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Active Profiles</span>
          <svg class="w-5 h-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div class="text-3xl font-bold text-slate-900 dark:text-white">
          {{ loading ? '...' : stats.active_profiles }}
        </div>
        <span class="text-xs text-amber-500 font-medium mt-1 inline-block">Catalog items</span>
      </div>
    </div>
  </div>
</template>