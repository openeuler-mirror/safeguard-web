<template>
  <div class="profile-container">
    <div class="profile-box">
      <h2>个人中心</h2>

      <div class="user-info">
        <div class="info-item">
          <span class="label">用户名：</span>
          <span>{{ user.user }}</span>
        </div>
        <div class="info-item">
          <span class="label">昵称：</span>
          <span>{{ user.nickname }}</span>
        </div>
        <div class="info-item">
          <span class="label">手机号：</span>
          <span>{{ user.phone || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="label">邮箱：</span>
          <span>{{ user.email || '-' }}</span>
        </div>
        <div class="info-item">
          <span class="label">状态：</span>
          <span :class="user.enable === 1 ? 'status-active' : 'status-disabled'">
            {{ user.enable === 1 ? '正常' : '已禁用' }}
          </span>
        </div>
      </div>

      <div class="actions">
        <button @click="goToChangePassword">修改密码</button>
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'Profile',
  computed: {
    ...mapState('auth', ['user'])
  },
  methods: {
    ...mapActions('auth', ['logout']),
    goToChangePassword() {
      this.$router.push('/change-password')
    },
    handleLogout() {
      this.logout()
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.profile-box {
  width: 480px;
  padding: 30px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin-bottom: 24px;
  color: #333;
}

.user-info {
  background: #f9f9f9;
  padding: 16px;
  border-radius: 4px;
}

.info-item {
  display: flex;
  margin-bottom: 12px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  color: #666;
  width: 80px;
}

.status-active {
  color: #67c23a;
}

.status-disabled {
  color: #f56c6c;
}

.actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

.actions button {
  flex: 1;
  padding: 12px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.actions button:hover {
  background-color: #66b1ff;
}

.logout-btn {
  background-color: #f56c6c !important;
}

.logout-btn:hover {
  background-color: #f78989 !important;
}
</style>