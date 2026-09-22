<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/axios'
import { useToastStore } from '@/stores/toastStore'

interface UserOut {
  id: number
  username: string
  email?: string
  role: 'ADMIN' | 'WORKER'
  is_active: boolean
}

interface UserCreate {
  username: string
  email: string
  password: string
  role: 'ADMIN' | 'WORKER'
}

const toast = useToastStore()
const users = ref<UserOut[]>([])
const loading = ref(false)
const showModal = ref(false)

const form = ref<UserCreate>({
  username: '',
  email: '',
  password: '',
  role: 'WORKER',
})

async function fetchUsers() {
  loading.value = true
  try {
    const res = await apiClient.get<UserOut[]>('/auth/users')
    users.value = res.data
  } catch (err) {
    toast.error('Failed to load users.')
  } finally {
    loading.value = false
  }
}

async function handleCreateUser() {
  try {
    await apiClient.post('/auth/users', form.value)
    toast.success('User registered successfully!')
    showModal.value = false
    form.value = { username: '', email: '', password: '', role: 'WORKER' }
    fetchUsers()
  } catch (err) {
    toast.error('Failed to register user.')
  }
}

async function handleToggleStatus(user: UserOut) {
  try {
    const newStatus = !user.is_active
    await apiClient.patch(`/admin/users/${user.id}`, { is_active: newStatus })
    toast.success(`User ${newStatus ? 'activated' : 'deactivated'} successfully.`)
    fetchUsers()
  } catch (err) {
    toast.error('Failed to update user status.')
  }
}

async function handleDeleteUser(id: number) {
  if (!confirm('Are you sure you want to permanently delete this user?')) return
  try {
    await apiClient.delete(`/admin/users/${id}`)
    toast.success('User permanently deleted.')
    fetchUsers()
  } catch (err) {
    toast.error('Failed to delete user.')
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-950 dark:text-slate-100">Worker & User Management</h1>
        <p class="text-sm text-slate-600 dark:text-slate-400">Manage staff accounts, access permissions, and account statuses.</p>
      </div>
      <button 
        @click="showModal = true"
        class="px-4 py-2 bg-slate-900 hover:bg-slate-800 dark:bg-sky-600 dark:hover:bg-sky-500 text-white text-sm font-medium rounded-xl transition-colors shadow-sm"
      >
        + Register New User
      </button>
    </div>

    <!-- Users Table -->
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-x-auto shadow-sm">
      <table class="w-full text-left border-collapse min-w-[600px]">
        <thead>
          <tr class="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
            <th class="p-4">Username</th>
            <th class="p-4">Email</th>
            <th class="p-4">Role</th>
            <th class="p-4">Status</th>
            <th class="p-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200 dark:divide-slate-800 text-sm">
          <tr v-for="u in users" :key="u.id" class="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 text-slate-950 dark:text-slate-100">
            <td class="p-4 font-semibold">{{ u.username }}</td>
            <td class="p-4 text-slate-600 dark:text-slate-400">{{ u.email || '-' }}</td>
            <td class="p-4">
              <span :class="u.role === 'ADMIN' ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300' : 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300'" class="px-2.5 py-1 rounded-full text-xs font-bold">
                {{ u.role }}
              </span>
            </td>
            <td class="p-4">
              <span :class="u.is_active ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300' : 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'" class="px-2.5 py-1 rounded-full text-xs font-bold">
                {{ u.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="p-4 text-right space-x-3">
              <button 
                @click="handleToggleStatus(u)"
                class="font-semibold text-xs text-amber-600 dark:text-amber-400 hover:underline"
              >
                {{ u.is_active ? 'Deactivate' : 'Activate' }}
              </button>
              <button 
                @click="handleDeleteUser(u.id)"
                class="font-semibold text-xs text-rose-600 dark:text-rose-400 hover:underline"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Register User Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 backdrop-blur-sm p-4">
      <div class="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full p-6 border border-slate-200 dark:border-slate-800 shadow-xl space-y-4">
        <h3 class="text-lg font-bold text-slate-950 dark:text-slate-100">Register New Staff User</h3>
        <form @submit.prevent="handleCreateUser" class="space-y-4">
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">Username</label>
            <input v-model="form.username" type="text" required class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-950 dark:text-slate-100" />
          </div>
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">Email</label>
            <input v-model="form.email" type="email" required class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-950 dark:text-slate-100" />
          </div>
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">Password</label>
            <input v-model="form.password" type="password" required class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-950 dark:text-slate-100" />
          </div>
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">Role</label>
            <select v-model="form.role" class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-950 dark:text-slate-100">
              <option value="WORKER">WORKER</option>
              <option value="ADMIN">ADMIN</option>
            </select>
          </div>
          <div class="flex justify-end space-x-2 pt-4">
            <button type="button" @click="showModal = false" class="px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 text-sm font-medium text-slate-700 dark:text-slate-300">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-slate-950 dark:bg-slate-100 dark:text-slate-950 text-white text-sm font-bold rounded-xl">Register Account</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>