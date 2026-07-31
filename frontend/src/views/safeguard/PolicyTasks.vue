<template>
  <div class="policy-tasks">
    <div class="page-header">
      <h2>策略下发任务</h2>
      <div class="header-actions">
        <select v-model="filterStatus" class="filter-select" @change="loadTasks">
          <option value="">全部状态</option>
          <option value="pending">待执行</option>
          <option value="running">执行中</option>
          <option value="success">成功</option>
          <option value="failed">失败</option>
        </select>
        <button class="btn-refresh" @click="loadTasks" :disabled="loading">刷新</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="tasks-table">
      <table>
        <thead>
          <tr>
            <th>任务 ID</th>
            <th>策略模板</th>
            <th>主机数量</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.id">
            <td>{{ task.id }}</td>
            <td>{{ task.template_name || '-' }}</td>
            <td>{{ task.host_count || 0 }}</td>
            <td>
              <StatusBadge :type="getStatusType(task.status)" :text="getStatusText(task.status)" />
            </td>
            <td>{{ formatDate(task.created_at) }}</td>
            <td>
              <button class="btn-action" @click="viewTask(task)">查看详情</button>
            </td>
          </tr>
          <tr v-if="tasks.length === 0">
            <td colspan="6" class="empty-text">暂无任务</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 任务详情弹窗 -->
    <div v-if="detailDialogVisible" class="dialog-overlay" @click.self="closeDetailDialog">
      <div class="dialog dialog-large">
        <div class="dialog-header">
          <h3>任务详情 - {{ selectedTask?.id }}</h3>
          <button class="dialog-close" @click="closeDetailDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="detail-info">
            <div class="info-row">
              <span class="info-label">策略模板:</span>
              <span class="info-value">{{ selectedTask?.template_name || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">状态:</span>
              <span><StatusBadge :type="getStatusType(selectedTask?.status)" :text="getStatusText(selectedTask?.status)" /></span>
            </div>
            <div class="info-row">
              <span class="info-label">创建时间:</span>
              <span class="info-value">{{ formatDate(selectedTask?.created_at) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">主机:</span>
              <span class="info-value">{{ selectedTask?.host_names?.join(', ') || '-' }}</span>
            </div>
          </div>
          <div v-if="selectedTask?.result" class="result-section">
            <h4>执行结果</h4>
            <pre class="result-json">{{ JSON.stringify(selectedTask.result, null, 2) }}</pre>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDetailDialog">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getPolicyTasks, getPolicyTask } from '@/api/safeguard/policy'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

export default {
  name: 'PolicyTasks',
  components: { StatusBadge },
  data() {
    return {
      tasks: [],
      filterStatus: '',
      loading: false,
      error: '',
      detailDialogVisible: false,
      selectedTask: null
    }
  },
  mounted() {
    this.loadTasks()
  },
  methods: {
    async loadTasks() {
      this.loading = true
      this.error = ''
      try {
        const params = {}
        if (this.filterStatus) params.status = this.filterStatus
        const res = await getPolicyTasks(params)
        this.tasks = res?.results || res || []
      } catch (e) {
        this.error = e.message || '加载任务列表失败'
      } finally {
        this.loading = false
      }
    },
    async viewTask(task) {
      try {
        const res = await getPolicyTask(task.id)
        this.selectedTask = res || task
        this.detailDialogVisible = true
      } catch (e) {
        alert(e.message || '获取任务详情失败')
      }
    },
    closeDetailDialog() {
      this.detailDialogVisible = false
      this.selectedTask = null
    },
    getStatusType(status) {
      const map = {
        pending: 'warning',
        running: 'info',
        success: 'success',
        failed: 'danger'
      }
      return map[status] || 'info'
    },
    getStatusText(status) {
      const map = {
        pending: '待执行',
        running: '执行中',
        success: '成功',
        failed: '失败'
      }
      return map[status] || status
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString()
    }
  }
}
</script>

<style scoped>
.policy-tasks {
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

.btn-cancel {
  padding: 8px 16px;
  background: #fff;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #f5f5f5;
}

.btn-action {
  padding: 6px 12px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.btn-action:hover {
  background: #66b1ff;
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

.tasks-table {
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

/* 弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow: hidden;
}

.dialog-large {
  width: 700px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.dialog-header h3 {
  margin: 0;
  color: #333;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.dialog-close:hover {
  color: #666;
}

.dialog-body {
  padding: 20px;
  overflow-y: auto;
  max-height: 60vh;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
}

.detail-info {
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-label {
  width: 120px;
  color: #909399;
}

.info-value {
  color: #333;
}

.result-section h4 {
  margin: 0 0 12px 0;
  color: #333;
}

.result-json {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 13px;
}
</style>