import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: () => import('@/views/admin/AdminView.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/worker',
    name: 'worker-dashboard',
    component: () => import('@/views/worker/WorkerView.vue'),
    meta: { requiresAuth: true, role: 'WORKER' } // Accessible by both WORKER and ADMIN
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth
  const requiredRole = to.meta.role

  // 1. Unauthenticated users trying to access protected pages
  if (requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login' })
  }

  // 2. Already logged in users trying to visit /login
  if (to.name === 'login' && authStore.isAuthenticated) {
    if (authStore.isAdmin) return next({ name: 'admin-dashboard' })
    return next({ name: 'worker-dashboard' })
  }

  // 3. Admin user visiting Worker route -> ALLOWED
  if (authStore.isAdmin && requiredRole === 'WORKER') {
    return next()
  }

  // 4. Worker user trying to visit Admin route -> BLOCKED
  if (requiredRole === 'ADMIN' && !authStore.isAdmin) {
    return next({ name: 'worker-dashboard' })
  }

  // 5. Allow normal navigation
  next()
})

export default router