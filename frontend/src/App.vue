<template>
  <div id="app">
    <header class="app-header" v-if="$store.state.auth.isAuthenticated">
      <div class="header-left">
        <button class="toggle-btn" @click="toggleSidebar" :title="sidebarCollapsed ? '展开菜单' : '收起菜单'">
          <span class="toggle-icon">{{ sidebarCollapsed ? '▶' : '◀' }}</span>
        </button>
        <h1 class="logo" @click="goHome">Safeguard</h1>
      </div>
      <div class="header-right">
        <div class="user-info" @click="toggleMenu">
          <span>{{ $store.state.auth.user?.nickname || $store.state.auth.user?.user }}</span>
          <span class="arrow">▾</span>
        </div>
        <div class="dropdown" v-if="menuVisible">
          <div class="dropdown-item" @click="goHome">回到主页</div>
          <div class="dropdown-item" @click="toProfile">个人信息</div>
          <div class="dropdown-item logout" @click="logout">注销</div>
        </div>
      </div>
    </header>
    <div class="app-body" v-if="$store.state.auth.isAuthenticated">
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <nav class="sidebar-nav">
          <router-link
            v-for="menu in menus"
            :key="menu.path"
            :to="menu.path"
            class="nav-item"
            :title="sidebarCollapsed ? menu.meta?.title || menu.name : ''"
          >
            <span class="nav-icon">{{ getMenuIcon(menu.path) }}</span>
            <span class="nav-text" v-if="!sidebarCollapsed">{{ menu.meta?.title || menu.name }}</span>
          </router-link>
        </nav>
      </aside>
      <main class="main-content">
        <router-view></router-view>
      </main>
    </div>
    <router-view v-else></router-view>
  </div>
</template>

<script>
export default {
  data() {
    return {
      menuVisible: false,
      sidebarCollapsed: false
    }
  },
  computed: {
    menus() {
      return this.$store.state.auth.menus
    }
  },
  mounted() {
    this.$store.dispatch('auth/fetchUser').then(() => {
      this.$store.dispatch('auth/fetchMenus')
    })
    document.addEventListener('click', this.closeMenu)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeMenu)
  },
  methods: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    toggleMenu(e) {
      e.stopPropagation()
      this.menuVisible = !this.menuVisible
    },
    closeMenu() {
      this.menuVisible = false
    },
    goHome() {
      this.menuVisible = false
      this.$router.push('/dashboard')
    },
    toProfile() {
      this.menuVisible = false
      this.$router.push('/profile')
    },
    logout() {
      this.menuVisible = false
      this.$store.dispatch('auth/logout')
      this.$router.push('/login')
    },
    getMenuIcon(path) {
      const icons = {
        '/dashboard': '🏠',
        '/users': '👤',
        '/authorities': '🔐',
        '/menus': '📋',
        '/clusters': '🗄️',
        '/hosts': '🖥️',
        '/profile': '👤',
        '/change-password': '🔑'
      }
      return icons[path] || '📄'
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  min-height: 100vh;
}
</style>

<style scoped>
.app-header {
  height: 60px;
  background: #409eff;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px 0 8px;
  position: relative;
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-btn {
  background: rgba(255,255,255,0.2);
  border: none;
  color: #fff;
  width: 36px;
  height: 36px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.toggle-btn:hover {
  background: rgba(255,255,255,0.3);
}

.toggle-icon {
  font-size: 12px;
}

.header-left .logo {
  font-size: 20px;
  cursor: pointer;
  margin: 0;
}

.header-right {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
}

.user-info:hover {
  background: rgba(255,255,255,0.2);
}

.arrow {
  font-size: 10px;
}

.dropdown {
  position: absolute;
  right: 0;
  top: 48px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  min-width: 120px;
  overflow: hidden;
}

.dropdown-item {
  padding: 12px 16px;
  color: #333;
  cursor: pointer;
}

.dropdown-item:hover {
  background: #f5f5f5;
}

.dropdown-item:last-child {
  color: #f56c6c;
  border-top: 1px solid #eee;
}

/* 侧边栏样式 */
.app-body {
  display: flex;
  height: calc(100vh - 60px);
}

.sidebar {
  width: 200px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-nav {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  color: #606266;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s;
  white-space: nowrap;
}

.nav-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

.nav-item.router-link-active {
  background: #ecf5ff;
  color: #409eff;
}

.nav-icon {
  font-size: 18px;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
}

.nav-text {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 12px 8px;
}

.sidebar.collapsed .nav-text {
  display: none;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: #f5f7fa;
}
</style>