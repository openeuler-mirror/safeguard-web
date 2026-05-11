<template>
  <div class="forgot-container">
    <div class="forgot-box">
      <h2>找回密码</h2>

      <div class="step-form">
        <div class="form-group">
          <label for="email">已注册的邮箱</label>
          <div class="email-input-group">
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="请输入注册邮箱"
              required
            />
            <button
              type="button"
              class="send-code-btn"
              :disabled="codeSending || countdown > 0"
              @click="handleSendCode"
            >
              {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="code">验证码 <span class="label-hint">(6位数字)</span></label>
          <input
            id="code"
            v-model="code"
            type="text"
            placeholder="请输入6位验证码"
            maxlength="6"
            class="code-input"
            required
          />
        </div>

        <div class="form-group">
          <label for="newPassword">新密码</label>
          <input
            id="newPassword"
            v-model="newPassword"
            type="password"
            placeholder="请输入新密码（至少6位）"
            minlength="6"
            required
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

        <button type="button" class="submit-btn" :disabled="loading" @click="handleReset">
          {{ loading ? '重置中...' : '重置密码' }}
        </button>

        <div class="link-group">
          <a href="#" @click.prevent="$router.push('/login')">返回登录</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { sendVerificationCode, resetPasswordWithCode } from '@/api/auth'

export default {
  name: 'ForgotPassword',
  data() {
    return {
      email: '',
      code: '',
      newPassword: '',
      confirmPassword: '',
      loading: false,
      codeSending: false,
      countdown: 0,
      error: '',
      success: ''
    }
  },
  methods: {
    async handleSendCode() {
      if (!this.email) {
        this.error = '请输入邮箱'
        return
      }
      this.codeSending = true
      this.error = ''
      try {
        const res = await sendVerificationCode(this.email, 'forgot')
        if (res.local_verify_url) {
          window.open(res.local_verify_url, '_blank')
        }
        this.countdown = 60
        const timer = setInterval(() => {
          this.countdown--
          if (this.countdown <= 0) clearInterval(timer)
        }, 1000)
      } catch (e) {
        this.error = e.message || '发送验证码失败'
      } finally {
        this.codeSending = false
      }
    },
    async handleReset() {
      if (!this.email) {
        this.error = '请输入邮箱'
        return
      }
      if (!this.code || this.code.length !== 6) {
        this.error = '请输入6位验证码'
        return
      }
      if (this.newPassword.length < 6) {
        this.error = '密码长度至少6位'
        return
      }
      if (this.newPassword !== this.confirmPassword) {
        this.error = '两次输入的密码不一致'
        return
      }
      this.loading = true
      this.error = ''
      this.success = ''
      try {
        await resetPasswordWithCode(this.email, this.code, this.newPassword)
        this.success = '密码重置成功！即将跳转到登录页面...'
        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)
      } catch (e) {
        this.error = e.message || '重置失败'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.forgot-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.forgot-box {
  width: 360px;
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

.code-input {
  letter-spacing: 4px;
  font-size: 16px;
  font-family: monospace;
  background-color: #f8f8f8;
  border-color: #67c23a;
}

.code-input:focus {
  border-color: #67c23a;
  background-color: #f0f9eb;
}

.label-hint {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

.email-input-group {
  display: flex;
  gap: 8px;
}

.email-input-group input {
  flex: 1;
}

.send-code-btn {
  padding: 10px 12px;
  background: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
}

.send-code-btn:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 8px;
}

.submit-btn:hover {
  background-color: #66b1ff;
}

.submit-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
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

.link-group {
  margin-top: 16px;
  text-align: center;
}

.link-group a {
  color: #409eff;
  text-decoration: none;
}

.link-group a:hover {
  text-decoration: underline;
}
</style>