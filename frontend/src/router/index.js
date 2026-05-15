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
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true, hideSidebar: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/Users.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/authorities',
    name: 'Authorities',
    component: () => import('@/views/Authorities.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/menus',
    name: 'Menus',
    component: () => import('@/views/Menus.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/clusters',
    name: 'Clusters',
    component: () => import('@/views/Clusters.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/hosts',
    name: 'Hosts',
    component: () => import('@/views/Hosts.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/vms',
    name: 'VMs',
    component: () => import('@/views/VMs.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('@/views/ChangePassword.vue'),
    meta: { requiresAuth: true, hideSidebar: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { requiresAuth: false }
  },
  // OS部署模块
  {
    path: '/osdeploy/jobs',
    name: 'OsdeployJobs',
    component: () => import('@/views/osdeploy/Jobs.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/osdeploy/repos',
    name: 'OsdeployRepos',
    component: () => import('@/views/osdeploy/Repos.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/osdeploy/kickstarts',
    name: 'OsdeployKickstarts',
    component: () => import('@/views/osdeploy/Kickstarts.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/osdeploy/pxe',
    name: 'OsdeployPXE',
    component: () => import('@/views/osdeploy/PXEConfig.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/osdeploy/auto-install',
    name: 'OsdeployAutoInstall',
    component: () => import('@/views/osdeploy/AutoInstall.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/osdeploy/whitelist',
    name: 'OsdeployWhiteList',
    component: () => import('@/views/osdeploy/WhiteList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/osdeploy/isos',
    name: 'OsdeployISOFiles',
    component: () => import('@/views/osdeploy/ISOFiles.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/osdeploy/outipsn',
    name: 'OsdeployOutIpSN',
    component: () => import('@/views/osdeploy/OutIpSN.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    redirect: '/dashboard'
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
  const hasToken = !!localStorage.getItem('access_token')
  const hasUser = !!store.state.auth.user

  if (requiresAuth && !isAuthenticated) {
    if (hasToken) {
      // 有 token 但没有用户信息，才获取
      if (!hasUser) {
        try {
          await store.dispatch('auth/fetchUser')
        } catch (e) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          next('/login')
          return
        }
      }
      next()
    } else {
      next('/login')
    }
  } else if (!requiresAuth && isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router