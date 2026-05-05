<template>
  <div class="change-password-container">
    <div class="change-password-box">
      <h2>修改密码</h2>
      <form @submit.prevent="handleChangePassword">
        <div class="form-group">
          <label for="oldPassword">旧密码</label>
          <input
            id="oldPassword"
            v-model="form.old_password"
            type="password"
            placeholder="请输入旧密码"
            required
          />
        </div>
        <div class="form-group">
          <label for="newPassword">新密码</label>
          <input
            id="newPassword"
            v-model="form.new_password"
            type="password"
            placeholder="请输入新密码（至少6位）"
            required
            minlength="6"
          />
        </div>
        <div class="form-group">
          <label for="confirmPassword">确认新密码</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            required
          />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>
        <button type="submit" :disabled="loading">
          {{ loading ? '修改中...' : '确认修改' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { changePassword } from '@/api/auth'

export default {
  name: 'ChangePassword',
  data() {
    return {
      form: {
        old_password: '',
        new_password: ''
      },
      confirmPassword: '',
      loading: false,
      error: '',
      success: ''
    }
  },
  methods: {
    async handleChangePassword() {
      if (this.form.new_password !== this.confirmPassword) {
        this.error = '两次输入的新密码不一致'
        return
      }
      this.loading = true
      this.error = ''
      this.success = ''
      try {
        await changePassword(this.form.old_password, this.form.new_password)
        this.success = '密码修改成功'
        this.form.old_password = ''
        this.form.new_password = ''
        this.confirmPassword = ''
      } catch (e) {
        this.error = e.response?.data?.error || '修改失败'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.change-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.change-password-box {
  width: 400px;
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
</style>