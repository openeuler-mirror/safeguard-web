<template>
  <div id="app">
    <header class="app-header" v-if="$store.state.auth.isAuthenticated">
      <div class="header-left">
        <h1 class="logo" @click="goHome">Safeguard</h1>
        <nav class="main-nav">
          <router-link v-for="menu in menus" :key="menu.path" :to="menu.path">
            {{ menu.meta?.title || menu.name }}
          </router-link>
        </nav>
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
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  data() {
    return {
      menuVisible: false
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
  padding: 0 24px;
  position: relative;
  z-index: 999;
}

.header-left .logo {
  font-size: 20px;
  cursor: pointer;
}

.main-nav {
  display: flex;
  gap: 24px;
  margin-left: 32px;
}

.main-nav a {
  color: rgba(255,255,255,0.8);
  text-decoration: none;
  font-size: 14px;
  padding: 8px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.main-nav a:hover,
.main-nav a.router-link-active {
  color: #fff;
  border-bottom-color: #fff;
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
</style>