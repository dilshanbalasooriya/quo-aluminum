/*catalogStore
This is use to chache the details that didn't change oftern.
for exaple aluminium profile,WindoworDoor type those kind a thigs.
*/

import { ref } from 'vue'
import { defineStore } from 'pinia'
import apiClient from '@/api/axios'
import type { ProfileOut, TypeOut } from '@/types'

export const useCatalogStore = defineStore('catalog', () => {
  const profiles = ref<ProfileOut[]>([])
  const aluTypes = ref<TypeOut[]>([])
  const isLoaded = ref(false)
  const loading = ref(false)

  // Fetch all reference data once, or re-fetch when forced (e.g., after admin updates)
  async function fetchCatalog(force = false) {
    if (isLoaded.value && !force) return // Return cached data if already loaded

    loading.value = true
    try {
      const [profilesRes, typesRes] = await Promise.all([
        apiClient.get<ProfileOut[]>('/catalog/aluminium-profiles'),
        apiClient.get<TypeOut[]>('/catalog/window-door-types')
      ])

      profiles.value = profilesRes.data
      aluTypes.value = typesRes.data
      isLoaded.value = true
    } catch (error) {
      console.error('Failed to load catalog data:', error)
    } finally {
      loading.value = false
    }
  }

  // Clear cache if admin modifies profiles/types so fresh data is pulled next time
  function invalidateCache() {
    isLoaded.value = false
  }

  return {
    profiles,
    aluTypes,
    isLoaded,
    loading,
    fetchCatalog,
    invalidateCache
  }
})