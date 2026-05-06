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
          <span v-if="!editing">{{ user.nickname }}</span>
          <input v-else v-model="form.nickname" type="text" class="edit-input" />
        </div>
        <div class="info-item">
          <span class="label">手机号：</span>
          <span v-if="!editing">{{ user.phone || '-' }}</span>
          <input v-else v-model="form.phone" type="text" class="edit-input" />
        </div>
        <div class="info-item">
          <span class="label">邮箱：</span>
          <span v-if="!editing">{{ user.email || '-' }}</span>
          <input v-else v-model="form.email" type="email" class="edit-input" />
        </div>
        <div class="info-item">
          <span class="label">状态：</span>
          <span :class="user.enable === 1 ? 'status-active' : 'status-disabled'">
            {{ user.enable === 1 ? '正常' : '已禁用' }}
          </span>
        </div>
      </div>

      <div v-if="message" :class="['message', messageType]">{{ message }}</div>

      <div class="actions">
        <button v-if="!editing" @click="startEdit">编辑信息</button>
        <template v-else>
          <button @click="cancelEdit">取消</button>
          <button class="save-btn" @click="saveProfile">保存</button>
        </template>
        <button @click="goToChangePassword">修改密码</button>
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { updateMe } from '@/api/auth'

export default {
  name: 'Profile',
  data() {
    return {
      editing: false,
      form: {
        nickname: '',
        phone: '',
        email: ''
      },
      message: '',
      messageType: ''
    }
  },
  computed: {
    ...mapState('auth', ['user'])
  },
  methods: {
    ...mapActions('auth', ['logout', 'fetchUser']),
    startEdit() {
      this.form.nickname = this.user.nickname || ''
      this.form.phone = this.user.phone || ''
      this.form.email = this.user.email || ''
      this.editing = true
      this.message = ''
    },
    cancelEdit() {
      this.editing = false
      this.message = ''
    },
    async saveProfile() {
      try {
        await updateMe(this.form)
        await this.fetchUser()
        this.editing = false
        this.message = '保存成功'
        this.messageType = 'success'
      } catch (e) {
        this.message = e.response?.data?.error || '保存失败'
        this.messageType = 'error'
      }
    },
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
  align-items: center;
  margin-bottom: 12px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  color: #666;
  width: 80px;
}

.edit-input {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.edit-input:focus {
  outline: none;
  border-color: #409eff;
}

.status-active {
  color: #67c23a;
}

.status-disabled {
  color: #f56c6c;
}

.message {
  margin-top: 16px;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
  font-size: 14px;
}

.message.success {
  background-color: #f0f9eb;
  color: #67c23a;
}

.message.error {
  background-color: #fef0f0;
  color: #f56c6c;
}

.actions {
  margin-top: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.actions button {
  flex: 1;
  min-width: 120px;
  padding: 12px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.actions button:hover {
  background-color: #66b1ff;
}

.save-btn {
  background-color: #67c23a !important;
}

.save-btn:hover {
  background-color: #85ce61 !important;
}

.logout-btn {
  background-color: #f56c6c !important;
}

.logout-btn:hover {
  background-color: #f78989 !important;
}
</style>