<template>
  <div id="app">
    <header class="app-header" v-show="$store.state.auth.isAuthenticated">
      <h1 class="logo" @click="goHome">Safeguard</h1>
      <div class="header-right">
        <div class="user-info" @click="toggleMenu">
          <span>{{ $store.state.auth.user?.nickname || $store.state.auth.user?.user }}</span>
          <span class="arrow">▾</span>
        </div>
        <div class="dropdown" v-show="menuVisible">
          <div class="dropdown-item" @click="goHome">回到主页</div>
          <div class="dropdown-item" @click="toProfile">个人信息</div>
          <div class="dropdown-item logout" @click="logout">注销</div>
        </div>
      </div>
    </header>
    <div class="app-body" v-show="$store.state.auth.isAuthenticated">
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <button class="sidebar-toggle" @click="toggleSidebar" :title="sidebarCollapsed ? '展开菜单' : '收起菜单'">
          <span>{{ sidebarCollapsed ? '▶' : '◀' }}</span>
        </button>
        <nav class="sidebar-nav">
          <div v-for="menu in menus" :key="menu.path" class="nav-group">
            <router-link
              :to="menu.path"
              class="nav-item"
              :title="sidebarCollapsed ? menu.meta?.title || menu.name : ''"
            >
              <span class="nav-icon">{{ getMenuIcon(menu.path) }}</span>
              <span class="nav-text" v-if="!sidebarCollapsed">{{ menu.meta?.title || menu.name }}</span>
              <span v-if="!sidebarCollapsed && menu.children?.length" class="nav-arrow">▾</span>
            </router-link>
            <!-- 子菜单 -->
            <div v-if="!sidebarCollapsed && menu.children?.length" class="nav-children">
              <router-link
                v-for="child in menu.children"
                :key="child.path"
                :to="child.path"
                class="nav-item child"
                :title="child.meta?.title || child.name"
              >
                <span class="nav-icon">{{ getMenuIcon(child.path) }}</span>
                <span class="nav-text">{{ child.meta?.title || child.name }}</span>
              </router-link>
            </div>
          </div>
        </nav>
      </aside>
      <main class="main-content">
        <transition name="fade" mode="out-in">
          <router-view></router-view>
        </transition>
      </main>
    </div>
    <main class="main-content full-width" v-show="!$store.state.auth.isAuthenticated">
      <router-view></router-view>
    </main>
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
  height: 100vh;
  overflow: hidden;
}

#app {
  height: 100vh;
  overflow: hidden;
}
</style>

<style scoped>
.app-header {
  height: 60px;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 16px;
  position: relative;
  z-index: 1000;
}

.logo {
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
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-toggle {
  background: #f5f7fa;
  border: none;
  border-bottom: 1px solid #e4e7ed;
  color: #606266;
  width: 100%;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding-left: 16px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.sidebar-toggle:hover {
  background: #e4e7ed;
  color: #409eff;
}

.sidebar-nav {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  overflow-y: auto;
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

.nav-arrow {
  margin-left: auto;
  font-size: 10px;
  color: #c0c4cc;
}

.nav-children {
  padding-left: 20px;
}

.nav-item.child {
  padding: 10px 12px;
  font-size: 13px;
}

.nav-item.child .nav-icon {
  font-size: 14px;
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

.main-content.full-width {
  width: 100%;
  height: 100vh;
}

/* 路由过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>