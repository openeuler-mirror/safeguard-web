<template>
  <div class="app-container">
    <header class="app-header" v-if="isAuthenticated">
      <div class="header-left">
        <h1>Safeguard</h1>
      </div>
      <div class="header-right">
        <div class="user-info" @click="toggleDropdown">
          <span class="username">{{ user?.nickname || user?.user }}</span>
          <span class="arrow" :class="{ open: showDropdown }">▼</span>
        </div>
        <div class="dropdown-menu" v-if="showDropdown" @click.stop>
          <div class="dropdown-item" @click="goToProfile">个人信息</div>
          <div class="dropdown-item logout" @click="handleLogout">注销</div>
        </div>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'App',
  data() {
    return {
      showDropdown: false
    }
  },
  computed: {
    ...mapState('auth', ['user', 'isAuthenticated'])
  },
  mounted() {
    this.fetchUser()
    document.addEventListener('click', this.closeDropdown)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeDropdown)
  },
  methods: {
    ...mapActions('auth', ['fetchUser', 'logout']),
    toggleDropdown(e) {
      e.stopPropagation()
      this.showDropdown = !this.showDropdown
    },
    closeDropdown() {
      this.showDropdown = false
    },
    goToProfile() {
      this.showDropdown = false
      this.$router.push('/profile')
    },
    handleLogout() {
      this.showDropdown = false
      this.logout()
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
</style>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  height: 60px;
  background-color: #409eff;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  font-size: 20px;
  font-weight: 600;
}

.header-right {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.username {
  margin-right: 8px;
}

.arrow {
  font-size: 10px;
  transition: transform 0.2s;
}

.arrow.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 120px;
  z-index: 1000;
}

.dropdown-item {
  padding: 12px 16px;
  color: #333;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item:first-child {
  border-radius: 4px 4px 0 0;
}

.dropdown-item:last-child {
  border-radius: 0 0 4px 4px;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.dropdown-item.logout {
  color: #f56c6c;
  border-top: 1px solid #eee;
}

.app-main {
  flex: 1;
}
</style>