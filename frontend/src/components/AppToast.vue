<script setup lang="ts">
import { useToastStore } from '@/stores/toastStore'

const toastStore = useToastStore()

// Style lookup based on toast type
const toastStyles = {
  success: {
    bg: 'bg-emerald-950/90 border-emerald-800 text-emerald-100',
    iconColor: 'text-emerald-400'
  },
  error: {
    bg: 'bg-rose-950/90 border-rose-800 text-rose-100',
    iconColor: 'text-rose-400'
  },
  warning: {
    bg: 'bg-amber-950/90 border-amber-800 text-amber-100',
    iconColor: 'text-amber-400'
  },
  info: {
    bg: 'bg-slate-900/90 border-slate-700 text-slate-100',
    iconColor: 'text-sky-400'
  }
}
</script>

<template>
  <div 
    aria-live="assertive" 
    class="fixed bottom-6 right-6 z-50 flex flex-col space-y-2.5 max-w-sm w-full pointer-events-none px-4 sm:px-0"
  >
    <TransitionGroup
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-4"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        class="pointer-events-auto flex items-center justify-between p-4 rounded-2xl border shadow-xl backdrop-blur-md transition-all duration-200"
        :class="toastStyles[toast.type].bg"
      >
        <div class="flex items-center space-x-3 pr-2">
          <!-- Success Icon -->
          <svg v-if="toast.type === 'success'" class="w-5 h-5 shrink-0" :class="toastStyles.success.iconColor" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>

          <!-- Error Icon -->
          <svg v-else-if="toast.type === 'error'" class="w-5 h-5 shrink-0" :class="toastStyles.error.iconColor" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>

          <!-- Warning Icon -->
          <svg v-else-if="toast.type === 'warning'" class="w-5 h-5 shrink-0" :class="toastStyles.warning.iconColor" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>

          <!-- Info Icon -->
          <svg v-else class="w-5 h-5 shrink-0" :class="toastStyles.info.iconColor" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>

          <span class="text-sm font-medium leading-snug">{{ toast.message }}</span>
        </div>

        <!-- Manual Dismiss Button -->
        <button
          type="button"
          class="shrink-0 p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition focus:outline-none"
          @click="toastStore.remove(toast.id)"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>