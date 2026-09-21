<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

// Form state
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

// Template ref for UX auto-focus
const usernameInput = ref<HTMLInputElement | null>(null)

onMounted(() => {
  usernameInput.value?.focus()
})

async function handleLogin() {
  errorMessage.value = ''

  if (!username.value || !password.value) {
    errorMessage.value = 'Please enter both username and password.'
    return
  }

  try {
    isLoading.value = true
    const userRole = await authStore.login(username.value, password.value)
    
    // Smooth redirect based on role
    if (userRole === 'ADMIN') {
      await router.push({ name: 'admin-dashboard' })
    } else {
      await router.push({ name: 'worker-dashboard' })
    }
  } catch (err: any) {
    if (err.response?.status === 401) {
      errorMessage.value = 'Invalid username or password.'
    } else {
      errorMessage.value = 'Unable to connect to the server. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 px-4 py-12">
    <div class="w-full max-full max-w-md space-y-8 bg-white p-8 rounded-2xl shadow-sm border border-slate-100">
      
      <!-- Brand & Header -->
      <div class="text-center">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-slate-900 text-white font-bold text-xl mb-4 shadow-md">
          Al
        </div>
        <h2 class="text-2xl font-bold tracking-tight text-slate-900">
          QUO-Alumininum
        </h2>
        <p class="mt-2 text-sm text-slate-500">
          Sign in to access your estimation workshop
        </p>
      </div>

      <!-- Error Alert -->
      <div 
        v-if="errorMessage" 
        class="p-4 rounded-xl bg-rose-50 border border-rose-100 text-sm text-rose-6-00 flex items-start space-x-2 animate-fade-in"
      >
        <svg class="w-5 h-5 text-rose-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Form -->
      <form class="space-y-5" @submit.prevent="handleLogin">
        <!-- Username Field -->
        <div>
          <label for="username" class="block text-sm font-medium text-slate-700 mb-1.5">
            Username
          </label>
          <input
            id="username"
            ref="usernameInput"
            v-model.trim="username"
            type="text"
            required
            autocomplete="username"
            placeholder="e.g. admin or worker"
            class="w-full px-4 py-3 rounded-xl border border-slate-200 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition"
          />
        </div>

        <!-- Password Field -->
        <div>
          <label for="password" class="block text-sm font-medium text-slate-700 mb-1.5">
            Password
          </label>
          <div class="relative">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              required
              autocomplete="current-password"
              placeholder="••••••••"
              class="w-full px-4 py-3 pr-12 rounded-xl border border-slate-200 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition"
            />
            <!-- Show/Hide Password Toggle -->
            <button
              type="button"
              class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600 focus:outline-none"
              @click="showPassword = !showPassword"
            >
              <svg v-if="!showPassword" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858-5.908a8.962 8.962 0 012.122-.38c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m-1.74-3.1a3 3 0 10-4.243-4.243 text-slate-400" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3l18 18" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full py-3.5 px-4 rounded-xl bg-slate-900 text-white font-medium hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center space-x-2 shadow-sm"
        >
          <span v-if="!isLoading">Sign In</span>
          <span v-else class="flex items-center space-x-2">
            <svg class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Authenticating...</span>
          </span>
        </button>
      </form>

      <!-- Footer Info -->
      <div class="text-center text-xs text-slate-400 pt-4 border-t border-slate-100">
        System Protected • Standard Role Access
      </div>

    </div>
  </div>
</template>