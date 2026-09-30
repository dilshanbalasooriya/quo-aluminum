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
    {
      path: '/',
      name: 'public-estimator',
      component: () => import('@/views/PublicEstimationView.vue'),
      meta: { requiresAuth: false },
      beforeEnter: () => {
        const authStore = useAuthStore()
        if (!authStore.isAuthenticated) return true
        return authStore.isAdmin ? { name: 'admin-dashboard' } : { name: 'worker-dashboard' }
      }
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
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('@/views/admin/AdminUsersView.vue')
        },
      ]
    },
    // ================= WORKER ROUTES =================
    {
      path: '/workshop',
      meta: { requiresAuth: true, role: 'WORKER' },
      children: [
        {
          path: '',
          name: 'worker-dashboard',
          component: () => import('@/views/worker/WorkerDashboardView.vue'),
        },
        {
          path: 'quotations',
          name: 'worker-quotations',            
          component: () => import('@/views/worker/QuotationHistoryView.vue'),
        },
      ],
    },
  ]
})

// Navigation Guards
router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.meta.role && authStore.user?.role !== to.meta.role && authStore.user?.role !== 'ADMIN') {
    return { name: 'login' }
  }

  return true
})

export default router