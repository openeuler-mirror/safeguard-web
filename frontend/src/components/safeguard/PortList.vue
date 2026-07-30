<template>
  <div class="port-list">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="port-table">
      <table>
        <thead>
          <tr>
            <th>端口</th>
            <th>协议</th>
            <th>状态</th>
            <th>进程名</th>
            <th>PID</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(port, index) in ports" :key="index">
            <td>{{ port.port }}</td>
            <td>{{ port.protocol }}</td>
            <td>
              <StatusBadge :type="port.state === 'LISTEN' ? 'success' : 'info'" :text="port.state" />
            </td>
            <td>{{ port.process_name || '-' }}</td>
            <td>{{ port.pid || '-' }}</td>
          </tr>
          <tr v-if="ports.length === 0">
            <td colspan="5" class="empty-text">暂无端口信息</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import StatusBadge from './StatusBadge.vue'

export default {
  name: 'PortList',
  components: { StatusBadge },
  props: {
    ports: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    error: { type: String, default: '' }
  }
}
</script>

<style scoped>
.port-list {
  width: 100%;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #f56c6c;
}

.port-table {
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
