<template>
  <div class="host-monitor-history">
    <div class="page-header">
      <button class="btn-back" @click="goBack">← 返回</button>
      <h2>{{ host?.hostname || '主机' }} - 历史监控</h2>
      <div class="header-actions">
        <select v-model="timeRange" class="filter-select" @change="loadHistoryData">
          <option value="1h">最近 1 小时</option>
          <option value="6h">最近 6 小时</option>
          <option value="24h">最近 24 小时</option>
          <option value="7d">最近 7 天</option>
        </select>
        <select v-model="metricType" class="filter-select" @change="updateChartData">
          <option value="all">全部指标</option>
          <option value="cpu">仅 CPU</option>
          <option value="memory">仅内存</option>
          <option value="network">仅网络</option>
        </select>
        <button class="btn-refresh" @click="loadHistoryData" :disabled="loading">刷新</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="history-content">
      <!-- 图表区域 -->
      <div v-if="showCpuChart" class="chart-card">
        <h3>CPU 使用率</h3>
        <SimpleLineChart :data="cpuChartData" :max-value="100" color="#409eff" unit="%" />
      </div>
      <div v-if="showMemChart" class="chart-card">
        <h3>内存使用率</h3>
        <SimpleLineChart :data="memChartData" :max-value="100" color="#67c23a" unit="%" />
      </div>
      <div v-if="showNetChart" class="chart-card">
        <h3>网络流量</h3>
        <SimpleLineChart
          :data="[
            { label: '入流量', data: netInChartData, color: '#409eff' },
            { label: '出流量', data: netOutChartData, color: '#f56c6c' }
          ]"
          :max-value="maxNetValue"
          unit="KB/s"
        />
      </div>

      <!-- 数据表格 -->
      <div class="table-card">
        <h3>详细数据</h3>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>时间</th>
                <th>CPU 使用率</th>
                <th>内存使用率</th>
                <th>网络入流量</th>
                <th>网络出流量</th>
                <th>系统负载</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, i) in historyData" :key="i">
                <td>{{ formatTime(item.timestamp) }}</td>
                <td>{{ item.cpu_percent }}%</td>
                <td>{{ item.mem_percent }}%</td>
                <td>{{ item.net_in }} KB/s</td>
                <td>{{ item.net_out }} KB/s</td>
                <td>{{ item.load_1 }}</td>
              </tr>
              <tr v-if="historyData.length === 0">
                <td colspan="6" class="empty-text">暂无数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getHost } from '@/api/host'
import { getMonitorHistory } from '@/api/safeguard/monitor'
import SimpleLineChart from '@/components/safeguard/SimpleLineChart.vue'

export default {
  name: 'HostMonitorHistory',
  components: { SimpleLineChart },
  data() {
    return {
      hostId: null,
      host: null,
      historyData: [],
      timeRange: '1h',
      metricType: 'all',
      loading: false,
      error: ''
    }
  },
  computed: {
    showCpuChart() {
      return this.metricType === 'all' || this.metricType === 'cpu'
    },
    showMemChart() {
      return this.metricType === 'all' || this.metricType === 'memory'
    },
    showNetChart() {
      return this.metricType === 'all' || this.metricType === 'network'
    },
    cpuChartData() {
      return this.historyData.map((d, i) => ({ x: i, y: d.cpu_percent || 0 }))
    },
    memChartData() {
      return this.historyData.map((d, i) => ({ x: i, y: d.mem_percent || 0 }))
    },
    netInChartData() {
      return this.historyData.map((d, i) => ({ x: i, y: d.net_in || 0 }))
    },
    netOutChartData() {
      return this.historyData.map((d, i) => ({ x: i, y: d.net_out || 0 }))
    },
    maxNetValue() {
      const allValues = [...this.netInChartData, ...this.netOutChartData].map(d => d.y)
      const max = Math.max(...allValues, 100)
      return Math.ceil(max / 100) * 100
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
        await this.loadHistoryData()
      } catch (e) {
        this.error = e.message || '加载数据失败'
      } finally {
        this.loading = false
      }
    },
    async loadHistoryData() {
      try {
        const res = await getMonitorHistory(this.hostId, { range: this.timeRange })
        this.historyData = res?.history || []
      } catch (e) {
        this.error = e.message || '获取历史监控数据失败'
      }
    },
    updateChartData() {
      // 计算属性会自动更新
    },
    formatTime(timestamp) {
      if (!timestamp) return '-'
      const d = new Date(timestamp)
      return d.toLocaleString()
    },
    goBack() {
      this.$router.push(`/hosts/${this.hostId}/dashboard`)
    }
  }
}
</script>

<style scoped>
.host-monitor-history {
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

.history-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-card, .table-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chart-card h3, .table-card h3 {
  margin: 0 0 16px 0;
  color: #333;
}

.table-container {
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