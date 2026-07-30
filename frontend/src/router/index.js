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
  // ========== 主机详情子路由 ==========
  {
    path: '/hosts/:id/dashboard',
    name: 'HostDashboard',
    component: () => import('@/views/hosts/HostDashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/hosts/:id/ports',
    name: 'HostPorts',
    component: () => import('@/views/hosts/HostPorts.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/hosts/:id/processes',
    name: 'HostProcesses',
    component: () => import('@/views/hosts/HostProcesses.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/hosts/:id/services',
    name: 'HostServices',
    component: () => import('@/views/hosts/HostServices.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/hosts/:id/monitor',
    name: 'HostMonitor',
    component: () => import('@/views/hosts/HostMonitor.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/hosts/:id/monitor-history',
    name: 'HostMonitorHistory',
    component: () => import('@/views/hosts/HostMonitorHistory.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/hosts/:id/file-monitor',
    name: 'HostFileMonitor',
    component: () => import('@/views/hosts/FileMonitorRules.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/hosts/:id/file-events',
    name: 'HostFileEvents',
    component: () => import('@/views/hosts/FileMonitorEvents.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/hosts/:id/accounts',
    name: 'HostAccounts',
    component: () => import('@/views/hosts/HostAccounts.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/hosts/:id/system-logs',
    name: 'HostSystemLogs',
    component: () => import('@/views/hosts/SystemLogs.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/hosts/:id/safeguard/policy',
    name: 'HostSafeguardPolicy',
    component: () => import('@/views/hosts/safeguard/HostSafeguardPolicy.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/vms',
    name: 'VMs',
    component: () => import('@/views/VMs.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/images',
    name: 'Images',
    component: () => import('@/views/Images.vue'),
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
  // Network模块
  {
    path: '/network/lbs',
    name: 'NetworkLoadBalancers',
    component: () => import('@/views/network/LoadBalancers.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/network/listeners',
    name: 'NetworkListeners',
    component: () => import('@/views/network/Listeners.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/network/pools',
    name: 'NetworkPools',
    component: () => import('@/views/network/Pools.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/network/members',
    name: 'NetworkMembers',
    component: () => import('@/views/network/Members.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/network/health-monitors',
    name: 'NetworkHealthMonitors',
    component: () => import('@/views/network/HealthMonitors.vue'),
    meta: { requiresAuth: true }
  },
  // Security模块
  {
    path: '/security/safeguards',
    name: 'SecuritySafeguards',
    component: () => import('@/views/security/Safeguards.vue'),
    meta: { requiresAuth: true }
  },
  // Task模块
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/Tasks.vue'),
    meta: { requiresAuth: true }
  },
  // OSmigrate模块
  {
    path: '/osmigrate/migrations',
    name: 'Migrations',
    component: () => import('@/views/osmigrate/Migrations.vue'),
    meta: { requiresAuth: true }
  },
  // ========== Safeguard管理路由 ==========
  {
    path: '/safeguard/policy-templates',
    name: 'SafeguardPolicyTemplates',
    component: () => import('@/views/safeguard/PolicyTemplates.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/safeguard/policy-templates/:id',
    name: 'SafeguardPolicyTemplateDetail',
    component: () => import('@/views/safeguard/PolicyTemplateDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/safeguard/policy-tasks',
    name: 'SafeguardPolicyTasks',
    component: () => import('@/views/safeguard/PolicyTasks.vue'),
    meta: { requiresAuth: true }
  },
  // ========== 审计日志路由 ==========
  {
    path: '/audit/logs',
    name: 'AuditLogs',
    component: () => import('@/views/audit/AuditLogs.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/audit/dashboard',
    name: 'AuditDashboard',
    component: () => import('@/views/audit/AuditDashboard.vue'),
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
      // 有 token 但没有用户信息，才获取用户
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