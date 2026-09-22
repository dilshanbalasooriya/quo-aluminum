import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'
import router from '@/router'

// Create an Axios instance with base configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request Interceptor: Attach JWT Bearer Token to outgoing requests
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()

    // OAuth2 login endpoint expects 'application/x-www-form-urlencoded' or FormData
    if (config.url?.includes('/auth/login')) {
      return config
    }

    // Attach token if available
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response Interceptor: Catch 401 Unauthorized errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const authStore = useAuthStore()

    if (error.response && error.response.status === 401) {
      // Token expired or invalid -> log out and redirect to login
      authStore.logout()
      router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
    }

    return Promise.reject(error)
  }
)

export default apiClient