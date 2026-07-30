<template>
  <div class="metric-card">
    <div class="metric-icon" :style="{ background: iconBg }">
      <span>{{ icon }}</span>
    </div>
    <div class="metric-content">
      <div class="metric-label">{{ label }}</div>
      <div class="metric-value">
        {{ value }}
        <span v-if="unit" class="metric-unit">{{ unit }}</span>
      </div>
      <div v-if="trend !== null" class="metric-trend" :class="trendClass">
        {{ trend > 0 ? '↑' : '↓' }} {{ Math.abs(trend) }}%
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MetricCard',
  props: {
    label: String,
    value: [String, Number],
    unit: String,
    icon: { type: String, default: '📊' },
    iconBg: { type: String, default: '#ecf5ff' },
    trend: { type: Number, default: null }
  },
  computed: {
    trendClass() {
      return this.trend > 0 ? 'trend-up' : 'trend-down'
    }
  }
}
</script>

<style scoped>
.metric-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
.metric-icon {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.metric-content {
  flex: 1;
}
.metric-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 4px;
}
.metric-value {
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}
.metric-unit {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
  margin-left: 4px;
}
.metric-trend {
  font-size: 12px;
  margin-top: 4px;
}
.trend-up { color: #67c23a; }
.trend-down { color: #f56c6c; }
</style>
