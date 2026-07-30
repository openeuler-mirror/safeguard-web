<template>
  <div class="host-monitor">
    <div class="page-header">
      <button class="btn-back" @click="goBack">← 返回</button>
      <h2>{{ host?.hostname || '主机' }} - 实时监控</h2>
      <div class="header-actions">
        <button v-if="!autoRefresh" class="btn-refresh" @click="loadMonitorData">手动刷新</button>
        <button :class="['btn-toggle', { active: autoRefresh }]" @click="toggleAutoRefresh">
          {{ autoRefresh ? '暂停自动刷新' : '开启自动刷新' }}
        </button>
      </div>
    </div>

    <div v-if="loading && !monitorHistory.length" class="loading">加载中...</div>
    <div v-else-if="error && !monitorHistory.length" class="error">{{ error }}</div>
    <div v-else class="monitor-content">
      <!-- 当前指标 -->
      <div class="current-metrics">
        <MetricCard
          label="CPU 使用率"
          :value="currentMetrics.cpu_percent || 0"
          unit="%"
          icon="💻"
          iconBg="#ecf5ff"
        />
        <MetricCard
          label="内存使用率"
          :value="currentMetrics.mem_percent || 0"
          unit="%"
          icon="🧠"
          iconBg="#fdf6ec"
        />
        <MetricCard
          label="网络入流量"
          :value="currentMetrics.net_in || 0"
          unit="KB/s"
          icon="📥"
          iconBg="#f0f9ff"
        />
        <MetricCard
          label="网络出流量"
          :value="currentMetrics.net_out || 0"
          unit="KB/s"
          icon="📤"
          iconBg="#fef0f0"
        />
      </div>

      <!-- 图表区域 -->
      <div class="charts-grid">
        <div class="chart-card">
          <h3>CPU 使用率</h3>
          <SimpleLineChart :data="cpuData" :max-value="100" color="#409eff" unit="%" />
        </div>
        <div class="chart-card">
          <h3>内存使用率</h3>
          <SimpleLineChart :data="memData" :max-value="100" color="#67c23a" unit="%" />
        </div>
        <div class="chart-card">
          <h3>网络流量</h3>
          <SimpleLineChart
            :data="[
              { label: '入流量', data: netInData, color: '#409eff' },
              { label: '出流量', data: netOutData, color: '#f56c6c' }
            ]"
            :max-value="maxNetValue"
            unit="KB/s"
          />
        </div>
        <div class="chart-card">
          <h3>系统负载</h3>
          <SimpleLineChart :data="loadData" :max-value="maxLoadValue" color="#e6a23c" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getHost } from '@/api/host'
import { getRealTimeMonitor } from '@/api/safeguard/monitor'
import MetricCard from '@/components/safeguard/MetricCard.vue'
import SimpleLineChart from '@/components/safeguard/SimpleLineChart.vue'

export default {
  name: 'HostMonitor',
  components: { MetricCard, SimpleLineChart },
  data() {
    return {
      hostId: null,
      host: null,
      currentMetrics: {},
      monitorHistory: [],
      maxDataPoints: 20,
      loading: false,
      error: '',
      autoRefresh: true,
      refreshInterval: null
    }
  },
  computed: {
    cpuData() {
      return this.monitorHistory.map((m, i) => ({ x: i, y: m.cpu_percent || 0 }))
    },
    memData() {
      return this.monitorHistory.map((m, i) => ({ x: i, y: m.mem_percent || 0 }))
    },
    netInData() {
      return this.monitorHistory.map((m, i) => ({ x: i, y: m.net_in || 0 }))
    },
    netOutData() {
      return this.monitorHistory.map((m, i) => ({ x: i, y: m.net_out || 0 }))
    },
    loadData() {
      return this.monitorHistory.map((m, i) => ({ x: i, y: m.load_1 || 0 }))
    },
    maxNetValue() {
      const allValues = [...this.netInData, ...this.netOutData].map(d => d.y)
      const max = Math.max(...allValues, 100)
      return Math.ceil(max / 100) * 100
    },
    maxLoadValue() {
      const values = this.loadData.map(d => d.y)
      const max = Math.max(...values, 2)
      return Math.ceil(max / 2) * 2
    }
  },
  mounted() {
    this.hostId = this.$route.params.id
    if (this.hostId) {
      this.loadData()
    }
  },
  beforeDestroy() {
    this.stopAutoRefresh()
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = ''
      try {
        const hostRes = await getHost(this.hostId)
        this.host = hostRes
        await this.loadMonitorData()
        if (this.autoRefresh) {
          this.startAutoRefresh()
        }
      } catch (e) {
        this.error = e.message || '加载数据失败'
      } finally {
        this.loading = false
      }
    },
    async loadMonitorData() {
      try {
        const res = await getRealTimeMonitor(this.hostId)
        const data = res || {}
        this.currentMetrics = data
        this.monitorHistory.push(data)
        if (this.monitorHistory.length > this.maxDataPoints) {
          this.monitorHistory.shift()
        }
      } catch (e) {
        console.error('获取监控数据失败', e)
      }
    },
    startAutoRefresh() {
      this.stopAutoRefresh()
      this.refreshInterval = setInterval(() => {
        this.loadMonitorData()
      }, 10000)
    },
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    },
    toggleAutoRefresh() {
      this.autoRefresh = !this.autoRefresh
      if (this.autoRefresh) {
        this.startAutoRefresh()
      } else {
        this.stopAutoRefresh()
      }
    },
    goBack() {
      this.$router.push(`/hosts/${this.hostId}/dashboard`)
    }
  }
}
</script>

<style scoped>
.host-monitor {
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

.btn-refresh {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-refresh:hover {
  background: #66b1ff;
}

.btn-toggle {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.btn-toggle:hover {
  background: #eee;
}

.btn-toggle.active {
  background: #67c23a;
  color: white;
  border-color: #67c23a;
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

.monitor-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.current-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 20px;
}

.chart-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin: 0 0 16px 0;
  color: #333;
}
</style>