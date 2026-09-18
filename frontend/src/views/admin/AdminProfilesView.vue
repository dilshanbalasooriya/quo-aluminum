<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/axios'
import { useToastStore } from '@/stores/toastStore'
import { useCatalogStore } from '@/stores/catalogStore'
import type { ProfileOut, ProfileCreate } from '@/types'

const catalog = useCatalogStore()
const toast = useToastStore()

const profiles = ref<ProfileOut[]>([])
const loading = ref(false)
const showModal = ref(false)
const editingId = ref<number | null>(null)

const form = ref<ProfileCreate>({
  profile_name: '',
  brand: '',
  gauge: 1.2,
  weight_per_meter: 0.75,
  rate_per_kg: 10.0,
})

async function fetchProfiles() {
  loading.value = true
  try {
    const res = await apiClient.get<ProfileOut[]>('/catalog/aluminium-profiles?include_inactive=true')
    profiles.value = res.data
  } catch (err) {
    toast.error('Failed to load aluminium profiles.')
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  editingId.value = null
  form.value = {
    profile_name: '',
    brand: '',
    gauge: 1.2,
    weight_per_meter: 0.75,
    rate_per_kg: 10.0,
  }
  showModal.value = true
}

function openEditModal(p: ProfileOut) {
  editingId.value = p.id
  form.value = {
    profile_name: p.profile_name,
    brand: p.brand || '',
    gauge: p.gauge,
    weight_per_meter: p.weight_per_meter,
    rate_per_kg: p.rate_per_kg,
  }
  showModal.value = true
}

async function handleSubmit() {
  try {
    if (editingId.value !== null) {
      // Edit / Update any column
      await apiClient.patch(`/admin/aluminium-profiles/${editingId.value}`, form.value)
      toast.success('Profile updated successfully!')
    } else {
      // Create new profile
      await apiClient.post('/admin/aluminium-profiles', form.value)
      toast.success('Profile created successfully!')
    }
    catalog.invalidateCache()
    showModal.value = false
    fetchProfiles()
  } catch (err) {
    toast.error('Failed to save profile.')
  }
}

// Toggle between Active and Inactive
async function handleToggleStatus(p: ProfileOut) {
  try {
    const newStatus = !p.is_active
    await apiClient.patch(`/admin/aluminium-profiles/${p.id}`, { is_active: newStatus })
    toast.success(`Profile ${newStatus ? 'activated' : 'deactivated'} successfully.`)
    catalog.invalidateCache()
    fetchProfiles()
  } catch (err) {
    toast.error('Failed to update profile status.')
  }
}

// Permanently delete item so it disappears completely
async function handleDelete(id: number) {
  if (!confirm('Are you sure you want to permanently delete this profile?')) return
  try {
    await apiClient.delete(`/admin/aluminium-profiles/${id}`)
    toast.success('Profile permanently removed.')
    catalog.invalidateCache()
    fetchProfiles()
  } catch (err) {
    toast.error('Failed to delete profile.')
  }
}

onMounted(() => {
  fetchProfiles()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Aluminium Profiles & Rates</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400">Manage gauges, weight per meter, and cost rates with full edit control.</p>
      </div>
      <button 
        @click="openCreateModal"
        class="px-4 py-2 bg-slate-900 hover:bg-slate-800 dark:bg-sky-600 dark:hover:bg-sky-500 text-white text-sm font-medium rounded-xl transition-colors shadow-sm"
      >
        + Add New Profile
      </button>
    </div>

    <!-- Profiles Table with High Contrast & Clear Actions -->
    <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl overflow-hidden shadow-sm">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
            <th class="p-4">Profile Name</th>
            <th class="p-4">Brand</th>
            <th class="p-4">Gauge</th>
            <th class="p-4">Weight (kg/m)</th>
            <th class="p-4">Rate ($/kg)</th>
            <th class="p-4">Status</th>
            <th class="p-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200 dark:divide-slate-700 text-sm">
          <tr v-for="p in profiles" :key="p.id" class="hover:bg-slate-50/50 dark:hover:bg-slate-700/20 text-slate-900 dark:text-slate-100">
            <td class="p-4 font-semibold">{{ p.profile_name }}</td>
            <td class="p-4 text-slate-600 dark:text-slate-400">{{ p.brand || '-' }}</td>
            <td class="p-4 font-medium">{{ p.gauge }}</td>
            <td class="p-4 font-medium">{{ p.weight_per_meter }}</td>
            <td class="p-4 font-bold text-emerald-600 dark:text-emerald-400">${{ p.rate_per_kg }}</td>
            <td class="p-4">
              <span :class="p.is_active ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300' : 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'" class="px-2.5 py-1 rounded-full text-xs font-bold">
                {{ p.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="p-4 text-right space-x-3">
              <button 
                @click="openEditModal(p)"
                class="font-semibold text-xs text-sky-600 dark:text-sky-400 hover:underline"
              >
                Edit
              </button>
              <button 
                @click="handleToggleStatus(p)"
                class="font-semibold text-xs text-amber-600 dark:text-amber-400 hover:underline"
              >
                {{ p.is_active ? 'Deactivate' : 'Activate' }}
              </button>
              <button 
                @click="handleDelete(p.id)"
                class="font-semibold text-xs text-rose-600 dark:text-rose-400 hover:underline"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create / Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
      <div class="bg-white dark:bg-slate-800 rounded-2xl max-w-md w-full p-6 border border-slate-200 dark:border-slate-700 shadow-xl space-y-4">
        <h3 class="text-lg font-bold text-slate-900 dark:text-white">
          {{ editingId !== null ? 'Edit Aluminium Profile' : 'Create Aluminium Profile' }}
        </h3>
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">Profile Name</label>
            <input v-model="form.profile_name" type="text" required class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white" />
          </div>
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">Brand</label>
            <input v-model="form.brand" type="text" class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white" />
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">Gauge</label>
              <input v-model.number="form.gauge" type="number" step="0.1" required class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">Weight/m</label>
              <input v-model.number="form.weight_per_meter" type="number" step="0.01" required class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-600 mb-1">Rate/kg ($)</label>
              <input v-model.number="form.rate_per_kg" type="number" step="0.01" required class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white" />
            </div>
          </div>
          <div class="flex justify-end space-x-2 pt-4">
            <button type="button" @click="showModal = false" class="px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-600 text-sm font-medium text-slate-700 dark:text-slate-300">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-slate-900 dark:bg-sky-600 text-white text-sm font-medium rounded-xl">Save Changes</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>