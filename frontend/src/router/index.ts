import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    // ================= ADMIN ROUTES =================
    {
      path: '/admin',
      meta: { requiresAuth: true, role: 'ADMIN' },
      children: [
        {
          path: '',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/AdminDashboardView.vue')
        },
        {
          path: 'profiles',
          name: 'admin-profiles',
          component: () => import('@/views/admin/AdminProfilesView.vue')
        },
        {
          path: 'templates',
          name: 'admin-templates',
          component: () => import('@/views/admin/AdminTemplatesView.vue')
        }
      ]
    },
    // ================= WORKER ROUTES =================
    {
      path: '/workshop',
      name: 'worker-dashboard',
      component: () => import('@/views/worker/WorkerDashboardView.vue'),
      meta: { requiresAuth: true, role: 'WORKER' }
    },
    // ================= DEFAULT REDIRECT =================
    {
      path: '/',
      redirect: () => {
        const authStore = useAuthStore()
        return authStore.isAdmin ? { name: 'admin-dashboard' } : { name: 'worker-dashboard' }
      }
    }
  ]
})

// Navigation Guards
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login' })
  }
  
  if (to.meta.role && authStore.user?.role !== to.meta.role && authStore.user?.role !== 'ADMIN') {
    return next({ name: 'login' })
  }
  
  next()
})

export default router