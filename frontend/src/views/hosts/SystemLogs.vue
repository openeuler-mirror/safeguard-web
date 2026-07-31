<template>
  <div class="system-logs">
    <div class="page-header">
      <button class="btn-back" @click="goBack">← 返回</button>
      <h2>{{ host?.hostname || '主机' }} - 系统日志</h2>
      <div class="header-actions">
        <select v-model="logLevel" class="filter-select" @change="loadLogs">
          <option value="">全部级别</option>
          <option value="emerg">Emergency</option>
          <option value="alert">Alert</option>
          <option value="crit">Critical</option>
          <option value="err">Error</option>
          <option value="warning">Warning</option>
          <option value="notice">Notice</option>
          <option value="info">Info</option>
          <option value="debug">Debug</option>
        </select>
        <button class="btn-refresh" @click="loadLogs" :disabled="loading">刷新</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="logs-container">
      <pre class="logs-content">{{ logs }}</pre>
    </div>
  </div>
</template>

<script>
import { getHost } from '@/api/host'
import { getSystemLogs } from '@/api/safeguard/host-info'

export default {
  name: 'SystemLogs',
  data() {
    return {
      hostId: null,
      host: null,
      logs: '',
      logLevel: '',
      loading: false,
      error: ''
    }
  },
  mounted() {
    this.hostId = this.$route.params.id
    if (this.hostId) {
      this.loadData()
    }
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = ''
      try {
        const hostRes = await getHost(this.hostId)
        this.host = hostRes
        await this.loadLogs()
      } catch (e) {
        this.error = e.message || '加载数据失败'
      } finally {
        this.loading = false
      }
    },
    async loadLogs() {
      try {
        const params = {}
        if (this.logLevel) params.level = this.logLevel
        const res = await getSystemLogs(this.hostId, params)
        this.logs = res?.logs || '(暂无日志)'
      } catch (e) {
        this.error = e.message || '获取日志失败'
      }
    },
    goBack() {
      this.$router.push(`/hosts/${this.hostId}/dashboard`)
    }
  }
}
</script>

<style scoped>
.system-logs {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 12px;
  margin-left: auto;
}

.btn-back {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.btn-back:hover {
  background: #eee;
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
  padding: 40px;
  color: #666;
}

.error {
  color: #f56c6c;
}

.logs-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.logs-content {
  padding: 20px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: calc(100vh - 220px);
  overflow-y: auto;
  font-size: 13px;
  line-height: 1.6;
  background: #f5f7fa;
  margin: 0;
}
</style>