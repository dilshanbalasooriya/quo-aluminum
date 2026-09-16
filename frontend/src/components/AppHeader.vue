<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import ThemeToggle from '@/components/ThemeToggle.vue'

const props = defineProps<{
  isSidebarCollapsed: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle-sidebar'): void
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Dynamic header title based on current router meta or path
const pageTitle = computed(() => {
  if (route.name === 'admin-dashboard') return 'Admin Dashboard'
  if (route.name === 'worker-dashboard') return 'Estimation Workshop'
  return 'Aluminium Estimator'
})

async function handleLogout() {
  authStore.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <header class="h-16 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-4 sm:px-6 flex items-center justify-between shrink-0 transition-colors duration-200 z-10">
    
    <!-- Left: Sidebar Toggle & Page Title -->
    <div class="flex items-center space-x-3">
      <button
        type="button"
        class="p-2 rounded-xl text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700/50 focus:outline-none transition"
        title="Toggle Sidebar"
        @click="emit('toggle-sidebar')"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <h1 class="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight">
        {{ pageTitle }}
      </h1>
    </div>

    <!-- Right: Theme Toggle & User Info -->
    <div class="flex items-center space-x-3 sm:space-x-4">
      
      <!-- Theme Switcher -->
      <ThemeToggle />

      <!-- User Profile Badge & Logout -->
      <div v-if="authStore.user" class="flex items-center space-x-3 border-l border-slate-200 dark:border-slate-700 pl-3 sm:pl-4">
        <div class="hidden sm:block text-right">
          <div class="text-sm font-semibold text-slate-800 dark:text-slate-200 leading-tight">
            {{ authStore.user.username }}
          </div>
          <div class="text-[10px] font-bold tracking-wider text-sky-600 dark:text-sky-400 uppercase">
            {{ authStore.user.role }}
          </div>
        </div>

        <!-- Logout Button -->
        <button
          type="button"
          class="px-3 py-1.5 text-xs font-medium text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-950/40 rounded-xl transition focus:outline-none"
          title="Sign out of system"
          @click="handleLogout"
        >
          Logout
        </button>
      </div>

    </div>
  </header>
</template>