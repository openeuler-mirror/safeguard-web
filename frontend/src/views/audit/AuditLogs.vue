<template>
  <div class="audit-logs">
    <div class="page-header">
      <h2>审计日志</h2>
      <div class="header-actions">
        <select v-model="filterAction" class="filter-select" @change="loadLogs">
          <option value="">全部操作</option>
          <option value="create">create</option>
          <option value="update">update</option>
          <option value="delete">delete</option>
          <option value="login">login</option>
          <option value="logout">logout</option>
        </select>
        <select v-model="filterResource" class="filter-select" @change="loadLogs">
          <option value="">全部资源</option>
          <option value="host">host</option>
          <option value="policy">policy</option>
          <option value="user">user</option>
        </select>
        <button class="btn-refresh" @click="loadLogs" :disabled="loading">刷新</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="logs-table">
      <table>
        <thead>
          <tr>
            <th>时间</th>
            <th>用户</th>
            <th>操作</th>
            <th>资源类型</th>
            <th>资源 ID</th>
            <th>IP 地址</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td>{{ formatDate(log.timestamp) }}</td>
            <td>{{ log.username || '-' }}</td>
            <td>
              <StatusBadge :type="getActionColor(log.action)" :text="log.action" />
            </td>
            <td>{{ log.resource_type || '-' }}</td>
            <td>{{ log.resource_id || '-' }}</td>
            <td>{{ log.ip_address || '-' }}</td>
          </tr>
          <tr v-if="logs.length === 0">
            <td colspan="6" class="empty-text">暂无日志</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { getAuditLogs } from '@/api/safeguard/audit'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

export default {
  name: 'AuditLogs',
  components: { StatusBadge },
  data() {
    return {
      logs: [],
      filterAction: '',
      filterResource: '',
      loading: false,
      error: ''
    }
  },
  mounted() {
    this.loadLogs()
  },
  methods: {
    async loadLogs() {
      this.loading = true
      this.error = ''
      try {
        const params = {}
        if (this.filterAction) params.action = this.filterAction
        if (this.filterResource) params.resource_type = this.filterResource
        const res = await getAuditLogs(params)
        this.logs = res?.results || res || []
      } catch (e) {
        this.error = e.message || '获取日志失败'
      } finally {
        this.loading = false
      }
    },
    getActionColor(action) {
      const map = {
        create: 'success',
        update: 'warning',
        delete: 'danger',
        login: 'info',
        logout: 'info'
      }
      return map[action] || 'info'
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString()
    }
  }
}
</script>

<style scoped>
.audit-logs {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn-refresh {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-refresh:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading, .error {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 16px;
}

.error {
  color: #f56c6c;
}

.logs-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
  white-space: nowrap;
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

.empty-text {
  text-align: center;
  color: #999;
}
</style>