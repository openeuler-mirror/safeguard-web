<template>
  <div class="audit-dashboard">
    <div class="page-header">
      <h2>审计统计</h2>
      <button class="btn-refresh" @click="loadStats" :disabled="loading">刷新</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="dashboard-content">
      <div class="metrics-row">
        <MetricCard label="今日操作数" :value="stats.today_count || 0" icon="📊" icon-bg="#ecf5ff" />
        <MetricCard label="本周操作数" :value="stats.week_count || 0" icon="📈" icon-bg="#fdf6ec" />
        <MetricCard label="活跃用户数" :value="stats.active_users || 0" icon="👥" icon-bg="#f0f9ff" />
        <MetricCard label="异常操作数" :value="stats.anomaly_count || 0" icon="⚠️" icon-bg="#fef0f0" />
      </div>

      <div class="charts-row">
        <div class="chart-card">
          <h3>操作类型分布</h3>
          <div class="type-distribution">
            <div v-for="(count, type) in stats.action_distribution || {}" :key="type" class="type-item">
              <span class="type-label">{{ type }}</span>
              <div class="type-bar">
                <div class="type-bar-fill" :style="{ width: getBarWidth(count) + '%', background: getBarColor(type) }"></div>
              </div>
              <span class="type-count">{{ count }}</span>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h3>用户操作排行</h3>
          <div class="user-list">
            <div v-for="(item, index) in stats.user_ranking || []" :key="index" class="user-item">
              <span class="user-rank">#{{ index + 1 }}</span>
              <span class="user-name">{{ item.username }}</span>
              <span class="user-count">{{ item.count }} 次</span>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <h3>操作趋势</h3>
        <div class="trend-placeholder">
          <p>趋势图表将在此显示</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getAuditStats } from '@/api/safeguard/audit'
import MetricCard from '@/components/safeguard/MetricCard.vue'

export default {
  name: 'AuditDashboard',
  components: { MetricCard },
  data() {
    return {
      stats: {},
      loading: false,
      error: ''
    }
  },
  mounted() {
    this.loadStats()
  },
  methods: {
    async loadStats() {
      this.loading = true
      this.error = ''
      try {
        const res = await getAuditStats()
        this.stats = res || {}
      } catch (e) {
        this.error = e.message || '获取统计失败'
      } finally {
        this.loading = false
      }
    },
    getBarWidth(count) {
      const maxCount = Math.max(...Object.values(this.stats.action_distribution || {}), 1)
      return (count / maxCount) * 100
    },
    getBarColor(type) {
      const map = {
        create: '#67c23a',
        update: '#e6a23c',
        delete: '#f56c6c',
        login: '#409eff',
        logout: '#909399'
      }
      return map[type] || '#909399'
    }
  }
}
</script>

<style scoped>
.audit-dashboard {
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
}

.page-header h2 {
  margin: 0;
  color: #333;
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

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.chart-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.type-distribution {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.type-label {
  width: 100px;
  color: #333;
}

.type-bar {
  flex: 1;
  height: 24px;
  background: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}

.type-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.type-count {
  width: 50px;
  text-align: right;
  color: #666;
  font-weight: 500;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  background: #f5f7fa;
  border-radius: 6px;
}

.user-rank {
  width: 40px;
  color: #909399;
  font-weight: 600;
}

.user-name {
  flex: 1;
  color: #333;
}

.user-count {
  color: #409eff;
  font-weight: 500;
}

.trend-placeholder {
  padding: 60px 20px;
  text-align: center;
  background: #f5f7fa;
  border-radius: 6px;
}

.trend-placeholder p {
  margin: 0;
  color: #909399;
}
</style>