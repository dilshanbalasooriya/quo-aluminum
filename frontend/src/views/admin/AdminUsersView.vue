<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/axios'
import { useToastStore } from '@/stores/toastStore'
import { useConfirmStore } from '@/stores/confirmStore'

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

interface UserUpdate {
  username: string
  password?: string
}

const toast = useToastStore()
const confirmStore = useConfirmStore()
const users = ref<UserOut[]>([])
const loading = ref(false)
const showModal = ref(false)
const editingUserId = ref<number | null>(null)

const form = ref<UserCreate>({
  username: '',
  email: '',
  password: '',
  role: 'WORKER',
})
const editForm = ref<UserUpdate>({ username: '' })

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

function openEditUser(user: UserOut) {
  editingUserId.value = user.id
  editForm.value = { username: user.username, password: '' }
}

async function handleEditUser() {
  if (editingUserId.value === null) return
  try {
    const payload = {
      username: editForm.value.username,
      ...(editForm.value.password ? { password: editForm.value.password } : {}),
    }
    await apiClient.patch(`/admin/users/${editingUserId.value}`, payload)
    toast.success('User updated successfully.')
    editingUserId.value = null
    fetchUsers()
  } catch (err) {
    toast.error('Failed to update user.')
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
  const confirmed = await confirmStore.ask(
    'This user will be unable to sign in and cannot be restored.',
    'Permanently delete user?',
  )
  if (!confirmed) return
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
                @click="handleDeleteUser(u.id)"
                class="rounded-lg bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700 transition hover:bg-rose-100 dark:bg-rose-950/40 dark:text-rose-300 dark:hover:bg-rose-950/70"
              >
                Delete
              </button>
              <button 
                @click="handleToggleStatus(u)"
                :class="u.is_active
                  ? 'text-amber-700 hover:bg-amber-50 dark:text-amber-300 dark:hover:bg-amber-950/40'
                  : 'text-emerald-700 hover:bg-emerald-50 dark:text-emerald-300 dark:hover:bg-emerald-950/40'"
                class="rounded-lg px-3 py-2 text-xs font-semibold transition"
              >
                {{ u.is_active ? 'Deactivate' : 'Activate' }}
              </button>
              <button
                @click="openEditUser(u)"
                class="rounded-lg px-3 py-2 text-xs font-semibold text-sky-700 transition hover:bg-sky-50 dark:text-sky-300 dark:hover:bg-sky-950/40"
              >
                Edit
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit User Modal -->
    <div v-if="editingUserId !== null" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 backdrop-blur-sm p-4">
      <div class="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full p-6 border border-slate-200 dark:border-slate-800 shadow-xl space-y-4">
        <h3 class="text-lg font-bold text-slate-950 dark:text-slate-100">Edit User</h3>
        <form @submit.prevent="handleEditUser" class="space-y-4">
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">Username</label>
            <input v-model="editForm.username" type="text" required class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-950 dark:text-slate-100" />
          </div>
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">New Password</label>
            <input v-model="editForm.password" type="password" placeholder="Leave blank to keep current password" class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-950 dark:text-slate-100" />
          </div>
          <div class="flex justify-end space-x-2 pt-4">
            <button type="button" @click="editingUserId = null" class="px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 text-sm font-medium text-slate-700 dark:text-slate-300">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-slate-950 dark:bg-slate-100 dark:text-slate-950 text-white text-sm font-bold rounded-xl">Save Changes</button>
          </div>
        </form>
      </div>
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