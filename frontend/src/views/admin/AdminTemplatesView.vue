<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/axios'
import { useToastStore } from '@/stores/toastStore'
import { useCatalogStore } from '@/stores/catalogStore'
import type { TypeOut, TypeCreate } from '@/types'
import WindowSvgPreview from '@/components/WindowSvgPreview.vue'

const catalog = useCatalogStore()
const toast = useToastStore()

const types = ref<TypeOut[]>([])
const showModal = ref(false)
const editingId = ref<number | null>(null)

const form = ref<TypeCreate>({
  type_name: '',
  category: 'WINDOW',
  vertical_bars_count: 1,
  horizontal_bars_count: 1,
})

async function fetchTypes() {
  try {
    const res = await apiClient.get<TypeOut[]>('/catalog/window-door-types?include_inactive=true')
    types.value = res.data
  } catch (err) {
    toast.error('Failed to load window/door types.')
  }
}

function openCreateModal() {
  editingId.value = null
  form.value = {
    type_name: '',
    category: 'WINDOW',
    vertical_bars_count: 1,
    horizontal_bars_count: 1,
  }
  showModal.value = true
}

function openEditModal(t: TypeOut) {
  editingId.value = t.id
  form.value = {
    type_name: t.type_name,
    category: t.category,
    vertical_bars_count: t.vertical_bars_count,
    horizontal_bars_count: t.horizontal_bars_count,
  }
  showModal.value = true
}

async function handleSubmit() {
  try {
    if (editingId.value !== null) {
      // Update existing template
      await apiClient.patch(`/admin/window-door-types/${editingId.value}`, form.value)
      toast.success('Template updated successfully!')
    } else {
      // Create new template
      await apiClient.post('/admin/window-door-types', form.value)
      toast.success('Template created successfully!')
    }
    catalog.invalidateCache()
    showModal.value = false
    fetchTypes()
  } catch (err) {
    toast.error('Failed to save template.')
  }
}

// Toggle between Active and Inactive
async function handleToggleStatus(t: TypeOut) {
  try {
    const newStatus = !t.is_active
    await apiClient.patch(`/admin/window-door-types/${t.id}`, { is_active: newStatus })
    toast.success(`Template ${newStatus ? 'activated' : 'deactivated'} successfully.`)
    catalog.invalidateCache()
    fetchTypes()
  } catch (err) {
    toast.error('Failed to update template status.')
  }
}

onMounted(() => {
  fetchTypes()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Window & Door Templates</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400">Configure structural frame styles and mullion grids.</p>
      </div>
      <button 
        @click="openCreateModal"
        class="px-4 py-2 bg-slate-900 hover:bg-slate-800 dark:bg-sky-600 dark:hover:bg-sky-500 text-white text-sm font-medium rounded-xl transition-colors shadow-sm"
      >
        + Add New Template
      </button>
    </div>

    <!-- Templates Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="t in types" :key="t.id" class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm space-y-4 flex flex-col justify-between">
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider px-2.5 py-1 bg-slate-100 dark:bg-slate-700 rounded-full text-slate-700 dark:text-slate-300">
              {{ t.category }}
            </span>
            <span :class="t.is_active ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300' : 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'" class="px-2.5 py-1 rounded-full text-xs font-bold">
              {{ t.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>

          <div>
            <h3 class="font-bold text-lg text-slate-900 dark:text-white">{{ t.type_name }}</h3>
            <p class="text-xs text-slate-500 mt-1">Grid: {{ t.vertical_bars_count }} Vertical / {{ t.horizontal_bars_count }} Horizontal bars</p>
          </div>

          <!-- Embedded Live Preview -->
          <WindowSvgPreview 
            :category="t.category"
            :vertical-bars="t.vertical_bars_count"
            :horizontal-bars="t.horizontal_bars_count"
            :width-mm="1200"
            :height-mm="1500"
          />
        </div>

        <!-- Card Actions -->
        <div class="flex items-center justify-end space-x-3 pt-3 border-t border-slate-100 dark:border-slate-700/50">
          <button @click="openEditModal(t)" class="text-xs font-semibold text-sky-600 dark:text-sky-400 hover:underline">
            Edit
          </button>
          <button 
            @click="handleToggleStatus(t)" 
            :class="t.is_active ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'"
            class="text-xs font-semibold hover:underline"
          >
            {{ t.is_active ? 'Deactivate' : 'Activate' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal with Live Preview Integration -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 overflow-y-auto">
      <div class="bg-white dark:bg-slate-800 rounded-2xl max-w-2xl w-full p-6 border border-slate-200 dark:border-slate-700 shadow-xl grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-4">
          <h3 class="text-lg font-bold text-slate-900 dark:text-white">
            {{ editingId !== null ? 'Edit Template' : 'Create Template' }}
          </h3>
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Type Name</label>
              <input v-model="form.type_name" type="text" required class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent text-slate-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Category</label>
              <select v-model="form.category" class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent text-slate-900 dark:text-white">
                <option value="WINDOW">WINDOW</option>
                <option value="DOOR">DOOR</option>
              </select>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Vertical Bars</label>
                <input v-model.number="form.vertical_bars_count" type="number" min="0" required class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent text-slate-900 dark:text-white" />
              </div>
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Horizontal Bars</label>
                <input v-model.number="form.horizontal_bars_count" type="number" min="0" required class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent text-slate-900 dark:text-white" />
              </div>
            </div>
            <div class="flex justify-end space-x-2 pt-4">
              <button type="button" @click="showModal = false" class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-sm font-medium">Cancel</button>
              <button type="submit" class="px-4 py-2 bg-slate-900 dark:bg-sky-600 text-white text-sm font-medium rounded-xl">Save Changes</button>
            </div>
          </form>
        </div>

        <!-- Live Preview inside Modal -->
        <div class="flex flex-col justify-center">
          <WindowSvgPreview 
            :category="form.category"
            :vertical-bars="form.vertical_bars_count"
            :horizontal-bars="form.horizontal_bars_count"
          />
        </div>
      </div>
    </div>
  </div>
</template>