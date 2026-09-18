<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

defineProps<{
  isCollapsed: boolean
}>()

const route = useRoute()
const authStore = useAuthStore()

// Helper to highlight the active menu item
function isActive(routeName: string) {
  return route.name === routeName
}
</script>

<template>
  <aside
    class="bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col transition-all duration-300 z-20 shrink-0 select-none"
    :class="isCollapsed ? 'w-16' : 'w-64'">
    <!-- Brand Header -->
    <div class="h-16 flex items-center px-4 border-b border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="flex items-center space-x-3">
        <div
          class="w-9 h-9 rounded-xl bg-slate-900 dark:bg-sky-500 text-white flex items-center justify-center font-bold text-lg shrink-0 shadow-sm">
          Al
        </div>
        <span v-if="!isCollapsed" class="font-bold text-slate-900 dark:text-white truncate tracking-tight">
          Estimator Pro
        </span>
      </div>
    </div>

    <!-- Navigation Menu (Role Aware) -->
    <div class="flex-1 overflow-y-auto px-3 py-4 space-y-6">

      <!-- ================= ADMIN SECTION ================= -->
      <div v-if="authStore.isAdmin" class="space-y-1">
        <div v-if="!isCollapsed"
          class="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2">
          Admin Controls
        </div>

        <!-- Admin Dashboard -->
        <RouterLink :to="{ name: 'admin-dashboard' }"
          class="flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium transition-colors" :class="isActive('admin-dashboard')
            ? 'bg-slate-900 dark:bg-slate-700 text-white'
            : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50'"
          :title="isCollapsed ? 'Admin Dashboard' : ''">
          <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
          <span v-if="!isCollapsed" class="truncate text-sm">Dashboard</span>
        </RouterLink>

        <!-- Profile Rates -->
        <RouterLink :to="{ name: 'admin-profiles' }"
          class="flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium transition-colors"
          :class="isActive('admin-profiles') ? 'bg-slate-900 dark:bg-slate-700 text-white' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50'"
          :title="isCollapsed ? 'Profile Rates' : ''">
          <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span v-if="!isCollapsed" class="truncate text-sm">Profile Rates</span>
        </RouterLink>

        <!-- Window Templates -->
        <RouterLink :to="{ name: 'admin-templates' }"
          class="flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium transition-colors"
          :class="isActive('admin-templates') ? 'bg-slate-900 dark:bg-slate-700 text-white' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50'"
          :title="isCollapsed ? 'Window Templates' : ''">
          <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <span v-if="!isCollapsed" class="truncate text-sm">Window Templates</span>
        </RouterLink>
      </div>

      <!-- ================= WORKER SECTION ================= -->
      <div class="space-y-1">
        <div v-if="!isCollapsed"
          class="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2">
          Estimation Workshop
        </div>

        <!-- Worker Dashboard / New Estimation -->
        <RouterLink :to="{ name: 'worker-dashboard' }"
          class="flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium transition-colors" :class="isActive('worker-dashboard')
            ? 'bg-slate-900 dark:bg-slate-700 text-white'
            : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50'"
          :title="isCollapsed ? 'New Estimation' : ''">
          <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span v-if="!isCollapsed" class="truncate text-sm">New Estimation</span>
        </RouterLink>

        <!-- Saved Quotations -->
        <a href="#"
          class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50 font-medium transition-colors"
          :title="isCollapsed ? 'Saved Quotations' : ''">
          <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span v-if="!isCollapsed" class="truncate text-sm">Saved Quotations</span>
        </a>
      </div>

    </div>
  </aside>
</template>