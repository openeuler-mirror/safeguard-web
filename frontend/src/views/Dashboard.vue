<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h2>控制面板</h2>
      <p class="page-desc">一站式服务器运维管理中心，快速进入常用功能</p>
    </div>

    <!-- 概览统计 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ stats.hosts }}</div>
        <div class="stat-label">主机</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.vms }}</div>
        <div class="stat-label">虚拟机</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.clusters }}</div>
        <div class="stat-label">集群</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.runningTasks }}</div>
        <div class="stat-label">运行中任务</div>
      </div>
    </div>

    <!-- 快速入口 -->
    <div class="section">
      <h3 class="section-title">快速入口</h3>
      <div class="quick-actions">
        <div class="action-card" @click="$router.push('/hosts')">
          <div class="action-icon">🖥️</div>
          <div class="action-name">添加主机</div>
          <div class="action-desc">录入服务器资产信息</div>
        </div>
        <div class="action-card" @click="$router.push('/osdeploy/auto-install')">
          <div class="action-icon">🚀</div>
          <div class="action-name">安装系统</div>
          <div class="action-desc">批量自动安装操作系统</div>
        </div>
        <div class="action-card" @click="$router.push('/osmigrate/migrations')">
          <div class="action-icon">🔄</div>
          <div class="action-name">迁移系统</div>
          <div class="action-desc">将系统迁移到新环境</div>
        </div>
        <div class="action-card" @click="$router.push('/network/lbs')">
          <div class="action-icon">⚖️</div>
          <div class="action-name">配置负载均衡</div>
          <div class="action-desc">创建负载均衡与监听器</div>
        </div>
        <div class="action-card" @click="$router.push('/tasks')">
          <div class="action-icon">📋</div>
          <div class="action-name">查看任务</div>
          <div class="action-desc">跟踪异步任务执行状态</div>
        </div>
      </div>
    </div>

    <!-- 最近任务 -->
    <div class="section" v-if="recentTasks.length > 0">
      <h3 class="section-title">最近任务</h3>
      <div class="task-list">
        <div v-for="task in recentTasks" :key="task.id" class="task-item">
          <span class="task-name">{{ task.name || task.task_id || '未命名任务' }}</span>
          <span class="task-status" :class="task.status">{{ formatStatus(task.status) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getHosts } from '@/api/host'
import { getVMs } from '@/api/host'
import { getClusters } from '@/api/host'
import { getTasks } from '@/api/task'

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        hosts: 0,
        vms: 0,
        clusters: 0,
        runningTasks: 0
      },
      recentTasks: []
    }
  },
  mounted() {
    this.loadStats()
    this.loadRecentTasks()
  },
  methods: {
    async loadStats() {
      try {
        const [hosts, vms, clusters, tasks] = await Promise.all([
          getHosts({ page_size: 1 }),
          getVMs({ page_size: 1 }),
          getClusters({ page_size: 1 }),
          getTasks({ page_size: 1 })
        ])
        this.stats.hosts = hosts.total || 0
        this.stats.vms = vms.total || 0
        this.stats.clusters = clusters.total || 0
        this.stats.runningTasks = (tasks.results || []).filter(t => t.status === 'RUNNING' || t.status === 'PENDING').length
      } catch (error) {
        console.error('加载概览数据失败', error)
      }
    },
    async loadRecentTasks() {
      try {
        const data = await getTasks({ page_size: 5 })
        this.recentTasks = (data.results || []).slice(0, 5)
      } catch (error) {
        console.error('加载最近任务失败', error)
      }
    },
    formatStatus(status) {
      const map = {
        'SUCCESS': '成功',
        'FAILURE': '失败',
        'RUNNING': '运行中',
        'PENDING': '等待中',
        'RETRY': '重试中'
      }
      return map[status] || status || '未知'
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.page-header {
  margin-bottom: 24px;
}

h2 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 24px;
}

.page-desc {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  color: #333;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.action-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.action-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.action-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}

.action-desc {
  font-size: 12px;
  color: #999;
}

.task-list {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  padding: 0 16px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid #f0f0f0;
}

.task-item:last-child {
  border-bottom: none;
}

.task-name {
  color: #333;
  font-size: 14px;
}

.task-status {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  background: #f0f0f0;
  color: #666;
}

.task-status.SUCCESS {
  background: #e6f7e6;
  color: #52c41a;
}

.task-status.FAILURE {
  background: #ffe6e6;
  color: #f5222d;
}

.task-status.RUNNING,
.task-status.PENDING {
  background: #e6f4ff;
  color: #1890ff;
}
</style>
