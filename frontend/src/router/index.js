import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    redirect: '/profile'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = store.state.auth.isAuthenticated

  if (requiresAuth && !isAuthenticated) {
    // 检查是否有token
    const token = localStorage.getItem('access_token')
    if (token) {
      // 尝试获取用户信息
      try {
        await store.dispatch('auth/fetchUser')
        next()
      } catch (e) {
        next('/login')
      }
    } else {
      next('/login')
    }
  } else if (!requiresAuth && isAuthenticated && to.path === '/login') {
    // 已登录且访问公开页面，跳转
    next('/profile')
  } else {
    next()
  }
})

export default router