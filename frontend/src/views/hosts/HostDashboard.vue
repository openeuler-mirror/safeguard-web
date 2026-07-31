<template>
  <div class="host-dashboard">
    <div class="page-header">
      <button class="btn-back" @click="goBack">← 返回</button>
      <h2>{{ host?.hostname || '主机详情' }} - 仪表盘</h2>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="dashboard-content">
      <!-- 指标卡片 -->
      <div class="metrics-row">
        <MetricCard
          label="CPU 使用率"
          :value="monitorData.cpu_percent || 0"
          unit="%"
          icon="💻"
          iconBg="#ecf5ff"
        />
        <MetricCard
          label="内存使用率"
          :value="monitorData.mem_percent || 0"
          unit="%"
          icon="🧠"
          iconBg="#fdf6ec"
        />
        <MetricCard
          label="磁盘使用率"
          :value="monitorData.disk_percent || 0"
          unit="%"
          icon="💾"
          iconBg="#f0f9ff"
        />
        <MetricCard
          label="系统负载"
          :value="monitorData.load_1 || 0"
          icon="📊"
          iconBg="#fef0f0"
        />
      </div>

      <!-- 快速导航 -->
      <div class="quick-nav">
        <h3>快速导航</h3>
        <div class="nav-buttons">
          <button class="nav-btn" @click="navigateTo('ports')">
            <span class="nav-icon">🔌</span>
            <span class="nav-label">端口信息</span>
          </button>
          <button class="nav-btn" @click="navigateTo('processes')">
            <span class="nav-icon">⚙️</span>
            <span class="nav-label">进程管理</span>
          </button>
          <button class="nav-btn" @click="navigateTo('services')">
            <span class="nav-icon">🛠️</span>
            <span class="nav-label">服务控制</span>
          </button>
          <button class="nav-btn" @click="navigateTo('monitor')">
            <span class="nav-icon">📈</span>
            <span class="nav-label">实时监控</span>
          </button>
          <button class="nav-btn" @click="navigateTo('monitor-history')">
            <span class="nav-icon">📉</span>
            <span class="nav-label">历史监控</span>
          </button>
          <button class="nav-btn" @click="navigateTo('accounts')">
            <span class="nav-icon">👥</span>
            <span class="nav-label">系统账户</span>
          </button>
          <button class="nav-btn" @click="navigateTo('system-logs')">
            <span class="nav-icon">📜</span>
            <span class="nav-label">系统日志</span>
          </button>
          <button class="nav-btn" @click="navigateTo('file-monitor')">
            <span class="nav-icon">📁</span>
            <span class="nav-label">文件监控</span>
          </button>
          <button class="nav-btn" @click="navigateTo('safeguard-policy')">
            <span class="nav-icon">🛡️</span>
            <span class="nav-label">安全策略</span>
          </button>
        </div>
      </div>

      <!-- 系统信息 -->
      <div class="system-info">
        <h3>系统信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">主机名</span>
            <span class="info-value">{{ systemInfo.hostname || host?.hostname || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">操作系统</span>
            <span class="info-value">{{ systemInfo.os || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">内核版本</span>
            <span class="info-value">{{ systemInfo.kernel || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">CPU 核心数</span>
            <span class="info-value">{{ systemInfo.cpu_cores || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">总内存</span>
            <span class="info-value">{{ systemInfo.mem_total ? formatBytes(systemInfo.mem_total) : '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">运行时间</span>
            <span class="info-value">{{ systemInfo.uptime || '-' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getHost } from '@/api/host'
import { getSystemInfo } from '@/api/safeguard/host-info'
import { getRealTimeMonitor } from '@/api/safeguard/monitor'
import MetricCard from '@/components/safeguard/MetricCard.vue'

export default {
  name: 'HostDashboard',
  components: { MetricCard },
  data() {
    return {
      hostId: null,
      host: null,
      systemInfo: {},
      monitorData: {},
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
        const [hostRes, systemRes, monitorRes] = await Promise.allSettled([
          getHost(this.hostId),
          getSystemInfo(this.hostId),
          getRealTimeMonitor(this.hostId)
        ])
        if (hostRes.status === 'fulfilled') {
          this.host = hostRes.value
        }
        if (systemRes.status === 'fulfilled') {
          this.systemInfo = systemRes.value || {}
        }
        if (monitorRes.status === 'fulfilled') {
          this.monitorData = monitorRes.value || {}
        }
      } catch (e) {
        this.error = e.message || '加载数据失败'
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$router.push('/hosts')
    },
    navigateTo(page) {
      const routeMap = {
        'ports': `/hosts/${this.hostId}/ports`,
        'processes': `/hosts/${this.hostId}/processes`,
        'services': `/hosts/${this.hostId}/services`,
        'monitor': `/hosts/${this.hostId}/monitor`,
        'monitor-history': `/hosts/${this.hostId}/monitor-history`,
        'accounts': `/hosts/${this.hostId}/accounts`,
        'system-logs': `/hosts/${this.hostId}/system-logs`,
        'file-monitor': `/hosts/${this.hostId}/file-monitor`,
        'safeguard-policy': `/hosts/${this.hostId}/safeguard/policy`
      }
      if (routeMap[page]) {
        this.$router.push(routeMap[page])
      }
    },
    formatBytes(bytes) {
      if (!bytes) return '-'
      const units = ['B', 'KB', 'MB', 'GB', 'TB']
      let size = bytes
      let unitIndex = 0
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024
        unitIndex++
      }
      return `${size.toFixed(2)} ${units[unitIndex]}`
    }
  }
}
</script>

<style scoped>
.host-dashboard {
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
}

.page-header h2 {
  margin: 0;
  color: #333;
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

.loading, .error {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 16px;
}

.error {
  color: #f56c6c;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.quick-nav, .system-info {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.quick-nav h3, .system-info h3 {
  margin: 0 0 16px 0;
  color: #333;
}

.nav-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.nav-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 12px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: #ecf5ff;
  border-color: #409eff;
  transform: translateY(-2px);
}

.nav-icon {
  font-size: 28px;
}

.nav-label {
  font-size: 14px;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 6px;
}

.info-label {
  color: #909399;
}

.info-value {
  color: #333;
  font-weight: 500;
}
</style>