<template>
  <div class="register-container">
    <div class="register-box">
      <h2>用户注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="form.user"
            type="text"
            placeholder="请输入用户名"
            required
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            required
            minlength="6"
          />
        </div>
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
          />
        </div>
        <div class="form-group">
          <label for="nickname">昵称</label>
          <input
            id="nickname"
            v-model="form.nickname"
            type="text"
            placeholder="请输入昵称"
          />
        </div>
        <div class="form-group">
          <label for="phone">手机号</label>
          <input
            id="phone"
            v-model="form.phone"
            type="text"
            placeholder="请输入手机号（可选）"
          />
        </div>
        <div class="form-group">
          <label for="email">邮箱</label>
          <div class="email-input-group">
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="请输入邮箱"
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
        <div class="form-group" v-if="localVerifyUrl">
          <label for="code">验证码</label>
          <div class="code-input-group">
            <input
              id="code"
              v-model="verificationCode"
              type="text"
              placeholder="请输入验证码"
              required
            />
            <span class="local-hint">
              <span class="check-icon">✓</span> 本地验证模式
            </span>
          </div>
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">注册成功！正在跳转...</div>
        <button type="submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <div class="link-group">
        <router-link to="/login">已有账号？去登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { createUser, sendVerificationCode, verifyCode } from '@/api/auth'

export default {
  name: 'Register',
  data() {
    return {
      form: {
        user: '',
        password: '',
        nickname: '',
        phone: '',
        email: ''
      },
      confirmPassword: '',
      loading: false,
      error: '',
      success: false,
      codeSending: false,
      countdown: 0,
      localVerifyUrl: '',
      verificationCode: ''
    }
  },
  methods: {
    async handleSendCode() {
      if (!this.form.email) {
        this.error = '请先输入邮箱'
        return
      }
      this.codeSending = true
      this.error = ''
      try {
        const res = await sendVerificationCode(this.form.email, 'register')
        if (res.data.local_verify_url) {
          // 本地模式：打开验证页面
          this.localVerifyUrl = res.data.local_verify_url
          window.open(res.data.local_verify_url, '_blank')
        }
        // 启动60秒本地倒计时（刷新页面后重置）
        this.countdown = 60
        const timer = setInterval(() => {
          this.countdown--
          if (this.countdown <= 0) clearInterval(timer)
        }, 1000)
      } catch (e) {
        this.error = e.response?.data?.error || '发送验证码失败'
      } finally {
        this.codeSending = false
      }
    },
    async handleRegister() {
      if (this.form.password !== this.confirmPassword) {
        this.error = '两次输入的密码不一致'
        return
      }
      if (this.localVerifyUrl && this.verificationCode) {
        // 本地模式：先验证邮箱
        try {
          await verifyCode(this.form.email, this.verificationCode)
        } catch (e) {
          this.error = '邮箱验证失败，请先完成验证'
          return
        }
      }
      this.loading = true
      this.error = ''
      this.success = false
      try {
        await createUser(this.form)
        this.success = true
        setTimeout(() => {
          this.$router.push('/login')
        }, 1500)
      } catch (e) {
        this.error = e.response?.data?.error || e.response?.data?.user?.[0] || e.response?.data?.password?.[0] || '注册失败'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.register-box {
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

.code-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.code-input-group input {
  flex: 1;
}

.local-hint {
  display: flex;
  align-items: center;
  color: #67c23a;
  font-size: 12px;
}

.check-icon {
  margin-right: 2px;
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

button[type="submit"] {
  width: 100%;
  padding: 12px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

button[type="submit"]:hover {
  background-color: #66b1ff;
}

button[type="submit"]:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
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