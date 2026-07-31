<template>
  <div class="file-monitor-events">
    <div class="page-header">
      <button class="btn-back" @click="goBack">← 返回</button>
      <h2>{{ host?.hostname || '主机' }} - 文件监控事件</h2>
      <div class="header-actions">
        <select v-model="filterType" class="filter-select" @change="loadEvents">
          <option value="">全部类型</option>
          <option value="read">read</option>
          <option value="write">write</option>
          <option value="create">create</option>
          <option value="delete">delete</option>
          <option value="modify">modify</option>
        </select>
        <button class="btn-primary" @click="collectEvents">采集事件</button>
        <button class="btn-refresh" @click="loadEvents" :disabled="loading">刷新</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="events-table">
      <table>
        <thead>
          <tr>
            <th>时间</th>
            <th>路径</th>
            <th>事件类型</th>
            <th>进程</th>
            <th>用户</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="event in events" :key="event.id">
            <td>{{ formatDate(event.timestamp) }}</td>
            <td>{{ event.path }}</td>
            <td>
              <StatusBadge :type="getEventTypeColor(event.event_type)" :text="event.event_type" />
            </td>
            <td>{{ event.process_name || '-' }}</td>
            <td>{{ event.user || '-' }}</td>
          </tr>
          <tr v-if="events.length === 0">
            <td colspan="5" class="empty-text">暂无事件</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { getHost } from '@/api/host'
import { getFileMonitorEvents, collectFileMonitorEvents } from '@/api/safeguard/file-monitor'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

export default {
  name: 'FileMonitorEvents',
  components: { StatusBadge },
  data() {
    return {
      hostId: null,
      host: null,
      events: [],
      filterType: '',
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
        await this.loadEvents()
      } catch (e) {
        this.error = e.message || '加载数据失败'
      } finally {
        this.loading = false
      }
    },
    async loadEvents() {
      try {
        this.error = ''
        const params = { host_id: this.hostId }
        if (this.filterType) params.event_type = this.filterType
        const res = await getFileMonitorEvents(params)
        this.events = res?.results || res || []
      } catch (e) {
        this.error = e.message || '获取事件失败'
      }
    },
    async collectEvents() {
      try {
        await collectFileMonitorEvents(this.hostId)
        alert('事件采集任务已触发')
        await this.loadEvents()
      } catch (e) {
        alert(e.message || '触发采集失败')
      }
    },
    getEventTypeColor(type) {
      const map = {
        read: 'info',
        write: 'warning',
        create: 'success',
        delete: 'danger',
        modify: 'info'
      }
      return map[type] || 'info'
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString()
    },
    goBack() {
      this.$router.push(`/hosts/${this.hostId}/dashboard`)
    }
  }
}
</script>

<style scoped>
.file-monitor-events {
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
  flex-wrap: wrap;
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

.btn-primary {
  padding: 8px 16px;
  background: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover:not(:disabled) {
  background: #85ce61;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
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

.events-table {
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