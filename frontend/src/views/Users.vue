<template>
  <div class="users-container">
    <div class="users-header">
      <h2>用户管理</h2>
      <button class="refresh-btn" @click="loadUsers">刷新</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="users-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>昵称</th>
            <th>邮箱</th>
            <th>手机号</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.user }}</td>
            <td>{{ user.nickname || '-' }}</td>
            <td>{{ user.email || '-' }}</td>
            <td>{{ user.phone || '-' }}</td>
            <td>
              <span :class="user.enable === 1 ? 'status-active' : 'status-disabled'">
                {{ user.enable === 1 ? '正常' : '已禁用' }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <button class="auth-btn" @click="openAuthorityDialog(user)">授权</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <UserAuthorityDialog
      :visible="dialogVisible"
      :user-info="selectedUser"
      :all-roles="allRoles"
      @close="dialogVisible = false"
      @success="handleAuthSuccess"
    />
  </div>
</template>

<script>
import { getUsers, getAuthorities } from '@/api/user'
import UserAuthorityDialog from '@/components/UserAuthorityDialog.vue'

export default {
  name: 'Users',
  components: {
    UserAuthorityDialog
  },
  data() {
    return {
      users: [],
      allRoles: [],
      loading: false,
      error: '',
      dialogVisible: false,
      selectedUser: {}
    }
  },
  mounted() {
    this.loadUsers()
    this.loadAuthorities()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      this.error = ''
      try {
        const res = await getUsers()
        this.users = res.data
      } catch (e) {
        this.error = e.response?.data?.error || '加载用户列表失败'
      } finally {
        this.loading = false
      }
    },
    async loadAuthorities() {
      try {
        const res = await getAuthorities()
        this.allRoles = res.data.results || res.data
      } catch (e) {
        console.error('加载角色列表失败', e)
      }
    },
    openAuthorityDialog(user) {
      this.selectedUser = user
      this.dialogVisible = true
    },
    handleAuthSuccess() {
      // 权限设置成功后可以刷新用户列表或其他操作
      this.loadUsers()
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.users-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.users-header h2 {
  margin: 0;
  color: #333;
}

.refresh-btn {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn:hover {
  background: #66b1ff;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #f56c6c;
}

.users-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f5f5f5;
  font-weight: 600;
  color: #333;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background: #fafafa;
}

.status-active {
  color: #67c23a;
}

.status-disabled {
  color: #f56c6c;
}

.auth-btn {
  padding: 6px 12px;
  background: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.auth-btn:hover {
  background: #85ce61;
}
</style>
