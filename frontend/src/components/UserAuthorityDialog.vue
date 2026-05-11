<template>
  <div v-if="visible" class="dialog-overlay" @click.self="handleClose">
    <div class="dialog-content">
      <div class="dialog-header">
        <h3>为「{{ userInfo.user }}」分配角色</h3>
        <button class="close-btn" @click="handleClose">&times;</button>
      </div>

      <div class="dialog-body">
        <div class="user-info">
          <div class="info-item">
            <span class="label">用户名：</span>
            <span>{{ userInfo.user }}</span>
          </div>
          <div class="info-item">
            <span class="label">昵称：</span>
            <span>{{ userInfo.nickname || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">邮箱：</span>
            <span>{{ userInfo.email || '-' }}</span>
          </div>
        </div>

        <div class="roles-section">
          <h4>角色列表</h4>
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="error" class="error">{{ error }}</div>
          <div v-else class="roles-list">
            <label v-for="role in allRoles" :key="role.id" class="role-item">
              <input type="checkbox" :value="role.authority_id" v-model="selectedRoles" />
              <span class="role-name">{{ role.authority_name }}</span>
              <span class="role-id">ID: {{ role.authority_id }}</span>
            </label>
          </div>
        </div>
      </div>

      <div class="dialog-footer">
        <div v-if="message" :class="['message', messageType]">{{ message }}</div>
        <button class="cancel-btn" @click="handleClose">取消</button>
        <button class="save-btn" @click="handleSave" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { getUserAuthorities, setUserAuthorities } from '@/api/user'

export default {
  name: 'UserAuthorityDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    userInfo: {
      type: Object,
      required: true
    },
    allRoles: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'success'],
  data() {
    return {
      selectedRoles: [],
      loading: false,
      saving: false,
      message: '',
      messageType: ''
    }
  },
  watch: {
    visible: {
      handler(newVal) {
        if (newVal) {
          this.loadUserAuthorities()
        } else {
          this.reset()
        }
      }
    }
  },
  methods: {
    async loadUserAuthorities() {
      this.loading = true
      this.error = ''
      try {
        const res = await getUserAuthorities(this.userInfo.id)
        // 从响应中提取 authority_id 列表
        this.selectedRoles = res.map(item => item.authority.authority_id)
      } catch (e) {
        this.error = e.message || '加载用户角色失败'
      } finally {
        this.loading = false
      }
    },
    async handleSave() {
      this.saving = true
      this.message = ''
      try {
        await setUserAuthorities(this.userInfo.id, this.selectedRoles)
        this.message = '保存成功'
        this.messageType = 'success'
        setTimeout(() => {
          this.$emit('success')
          this.$emit('close')
        }, 1000)
      } catch (e) {
        this.message = e.message || '保存失败'
        this.messageType = 'error'
      } finally {
        this.saving = false
      }
    },
    handleClose() {
      this.$emit('close')
    },
    reset() {
      this.selectedRoles = []
      this.loading = false
      this.saving = false
      this.message = ''
      this.messageType = ''
      this.error = ''
    }
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.dialog-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #666;
}

.dialog-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.user-info {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item .label {
  color: #666;
  width: 60px;
}

.roles-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #333;
}

.loading, .error {
  padding: 20px;
  text-align: center;
  color: #666;
}

.error {
  color: #f56c6c;
}

.roles-list {
  max-height: 300px;
  overflow-y: auto;
}

.role-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.role-item:last-child {
  border-bottom: none;
}

.role-item:hover {
  background: #f5f5f5;
}

.role-item input {
  margin-right: 10px;
}

.role-name {
  flex: 1;
  color: #333;
}

.role-id {
  color: #999;
  font-size: 12px;
}

.dialog-footer {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

.message {
  margin-right: auto;
  font-size: 14px;
}

.message.success {
  color: #67c23a;
}

.message.error {
  color: #f56c6c;
}

.cancel-btn, .save-btn {
  padding: 8px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn {
  background: #f0f0f0;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.save-btn {
  background: #409eff;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.save-btn:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}
</style>
