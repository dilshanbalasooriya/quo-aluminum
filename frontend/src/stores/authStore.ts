/* 
authStore: globle authentication haddleing class.
check the request user role. 
set jwt token for outgoing responces.
haddle loging and logout function in ui prespective
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { jwtDecode} from 'jwt-decode'
import apiClient from '@/api/axios'

// TypeScript Interfaces
export type Role = 'ADMIN' | 'WORKER'

export interface JwtPayload {
  sub: string
  role: Role
  user_id: number
  exp: number
}

export interface User {
  id: number
  username: string
  role: Role
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)

  // Initialize state from token if page is refreshed
  if (token.value) {
    try {
      const decoded = jwtDecode<JwtPayload>(token.value)
      // Check if token is expired
      if (decoded.exp * 1000 < Date.now()) {
        logout()
      } else {
        user.value = {
          id: decoded.user_id,
          username: decoded.sub,
          role: decoded.role
        }
      }
    } catch {
      logout()
    }
  }

  // Getters (Computed properties)
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'ADMIN')
  const isWorker = computed(() => user.value?.role === 'WORKER')

  // Actions
  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
    
    // Decode token payload to extract user metadata
    const decoded = jwtDecode<JwtPayload>(newToken)
    user.value = {
      id: decoded.user_id,
      username: decoded.sub,
      role: decoded.role
    }
  }

  async function login(username: string, password: string): Promise<Role> {
    // OAuth2 password flow expects form-data
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await apiClient.post('auth/login',formData,{
      headers:{
        'Content-Type':'application/x-www-form-urlencoded'
      }
    })
    const accessToken = response.data.access_token

    setToken(accessToken)

    // Return role so the calling component/router knows where to redirect
    return user.value!.role
  }
      
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    isWorker,
    login,
    logout,
    setToken
  }
})