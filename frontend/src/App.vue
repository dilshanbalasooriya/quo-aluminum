<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

import AppHeader from '@/components/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppFooter from '@/components/AppFooter.vue'
import AppToast from '@/components/AppToast.vue'

const route = useRoute()
const authStore = useAuthStore()

// State for sidebar collapsing
const isSidebarCollapsed = ref(window.innerWidth < 768)

function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

// Show shell components only when logged in and not on the login page
const showLayoutShell = computed(() => {
  return authStore.isAuthenticated && route.name !== 'login'
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 flex flex-col font-sans antialiased transition-colors duration-200">
    
    <!-- 1. FULL APP SHELL (Renders when logged in) -->
    <div v-if="showLayoutShell" class="flex h-screen overflow-hidden relative">
      
      <!-- Mobile Backdrop Overlay -->
      <div v-if="!isSidebarCollapsed" 
           @click="toggleSidebar"
           class="fixed inset-0 bg-slate-950/50 backdrop-blur-sm z-20 md:hidden" 
           aria-hidden="true">
      </div>

      <!-- Collapsible Role-Based Sidebar -->
      <AppSidebar :is-collapsed="isSidebarCollapsed" />

      <!-- Content Area (Header + Workspace Canvas + Footer) -->
      <div class="flex-1 flex flex-col h-screen overflow-hidden">
        
        <!-- App Header -->
        <AppHeader 
          :is-sidebar-collapsed="isSidebarCollapsed" 
          @toggle-sidebar="toggleSidebar" 
        />

        <!-- Dynamic Main Workspace Canvas -->
        <main class="flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-50 dark:bg-slate-900">
          <RouterView />
        </main>

        <!-- App Footer -->
        <AppFooter />
      </div>
    </div>

    <!-- 2. CLEAN CANVAS (Renders for LoginView without header/sidebar) -->
    <div v-else class="min-h-screen flex items-center justify-center">
      <RouterView />
    </div>

    <!-- Global Toast Alert Overlay (Always Active) -->
    <AppToast />

  </div>
</template>