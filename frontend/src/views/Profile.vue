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

      <div class="divider"></div>

      <h3>修改密码</h3>
      <form @submit.prevent="handleChangePassword">
        <div class="form-group">
          <label for="oldPassword">旧密码</label>
          <input
            id="oldPassword"
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入旧密码"
            required
          />
        </div>
        <div class="form-group">
          <label for="newPassword">新密码</label>
          <input
            id="newPassword"
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码（至少6位）"
            required
            minlength="6"
          />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>
        <button type="submit" :disabled="loading">
          {{ loading ? '修改中...' : '修改密码' }}
        </button>
      </form>

      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { changePassword } from '@/api/auth'

export default {
  name: 'Profile',
  data() {
    return {
      passwordForm: {
        old_password: '',
        new_password: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  computed: {
    ...mapState('auth', ['user'])
  },
  methods: {
    ...mapActions('auth', ['logout']),
    async handleChangePassword() {
      this.loading = true
      this.error = ''
      this.success = ''
      try {
        await changePassword(this.passwordForm.old_password, this.passwordForm.new_password)
        this.success = '密码修改成功'
        this.passwordForm.old_password = ''
        this.passwordForm.new_password = ''
      } catch (e) {
        this.error = e.response?.data?.error || '修改失败'
      } finally {
        this.loading = false
      }
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

h3 {
  margin: 16px 0;
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

.divider {
  height: 1px;
  background: #eee;
  margin: 20px 0;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #666;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #409eff;
}

.error-message {
  color: #f56c6c;
  margin-bottom: 16px;
  font-size: 14px;
}

.success-message {
  color: #67c23a;
  margin-bottom: 16px;
  font-size: 14px;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

button:hover {
  background-color: #66b1ff;
}

button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.logout-btn {
  margin-top: 16px;
  background-color: #f56c6c;
}

.logout-btn:hover {
  background-color: #f78989;
}
</style>