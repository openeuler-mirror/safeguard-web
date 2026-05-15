<template>
  <div class="jobs-container">
    <div class="jobs-header">
      <h2>任务管理</h2>
      <div class="header-actions">
        <select v-model="filterStatus" class="filter-select" @change="handleFilter">
          <option value="">全部状态</option>
          <option value="pending">等待中</option>
          <option value="running">运行中</option>
          <option value="success">成功</option>
          <option value="failed">失败</option>
        </select>
        <select v-model="filterJobType" class="filter-select" @change="handleFilter">
          <option value="">全部类型</option>
          <option value="osdeploy">OS部署</option>
          <option value="hardware">硬件采集</option>
        </select>
        <input
          v-model="searchJobId"
          type="text"
          placeholder="搜索任务ID/目标"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="btn-refresh" @click="loadJobs">刷新</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="jobs-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>任务ID</th>
            <th>任务类型</th>
            <th>目标</th>
            <th>状态</th>
            <th>进度</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.id">
            <td>{{ job.id }}</td>
            <td>{{ job.job_id }}</td>
            <td>{{ formatJobType(job.job_type) }}</td>
            <td>{{ job.target }}</td>
            <td>
              <span :class="getStatusClass(job.status)">
                {{ formatStatus(job.status) }}
              </span>
            </td>
            <td>
              <div class="progress-cell">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: job.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ job.progress }}%</span>
              </div>
            </td>
            <td>{{ formatDate(job.created_at) }}</td>
            <td>
              <button class="btn-detail" @click="openDetailDialog(job)">详情</button>
              <button v-if="job.status === 'pending' || job.status === 'running'" class="btn-cancel" @click="confirmCancel(job)">取消</button>
            </td>
          </tr>
          <tr v-if="jobs.length === 0">
            <td colspan="8" class="empty-text">暂无数据</td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="pagination">
        <button :disabled="page <= 1" @click="handlePageChange(page - 1)">上一页</button>
        <span class="page-info">第 {{ page }} / {{ totalPages }} 页</span>
        <button :disabled="page >= totalPages" @click="handlePageChange(page + 1)">下一页</button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="detailDialogVisible" class="dialog-overlay" @click.self="closeDetailDialog">
      <div class="dialog dialog-wide">
        <div class="dialog-header">
          <h3>任务详情</h3>
          <button class="dialog-close" @click="closeDetailDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="selectedJob" class="job-detail">
            <div class="detail-item">
              <label>任务ID</label>
              <span>{{ selectedJob.job_id }}</span>
            </div>
            <div class="detail-item">
              <label>任务类型</label>
              <span>{{ formatJobType(selectedJob.job_type) }}</span>
            </div>
            <div class="detail-item">
              <label>目标</label>
              <span>{{ selectedJob.target }}</span>
            </div>
            <div class="detail-item">
              <label>状态</label>
              <span :class="getStatusClass(selectedJob.status)">{{ formatStatus(selectedJob.status) }}</span>
            </div>
            <div class="detail-item">
              <label>进度</label>
              <div class="progress-cell">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: selectedJob.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ selectedJob.progress }}%</span>
              </div>
            </div>
            <div class="detail-item" v-if="selectedJob.error_message">
              <label>错误信息</label>
              <span class="error-message">{{ selectedJob.error_message }}</span>
            </div>
            <div class="detail-item" v-if="selectedJob.result && Object.keys(selectedJob.result).length > 0">
              <label>结果详情</label>
              <pre class="result-json">{{ JSON.stringify(selectedJob.result, null, 2) }}</pre>
            </div>
            <div class="detail-item">
              <label>创建时间</label>
              <span>{{ formatDate(selectedJob.created_at) }}</span>
            </div>
            <div class="detail-item">
              <label>更新时间</label>
              <span>{{ formatDate(selectedJob.updated_at) }}</span>
            </div>
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
import { getJobs, getJobDetail, queryJobStatus } from '@/api/osdeploy/job'

export default {
  name: 'Jobs',
  data() {
    return {
      jobs: [],
      loading: false,
      error: '',
      searchJobId: '',
      filterStatus: '',
      filterJobType: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      detailDialogVisible: false,
      selectedJob: null
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize) || 1
    }
  },
  mounted() {
    this.loadJobs()
  },
  methods: {
    async loadJobs() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        if (this.searchJobId) params.search = this.searchJobId
        if (this.filterStatus) params.status = this.filterStatus
        if (this.filterJobType) params.job_type = this.filterJobType
        const res = await getJobs(params)
        this.jobs = res.results || res || []
        this.totalCount = res.count || this.jobs.length
      } catch (e) {
        this.error = e.message || '加载任务列表失败'
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.page = 1
      this.loadJobs()
    },
    handleFilter() {
      this.page = 1
      this.loadJobs()
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadJobs()
    },
    async openDetailDialog(job) {
      try {
        const res = await getJobDetail(job.id)
        this.selectedJob = res
        this.detailDialogVisible = true
      } catch (e) {
        alert(e.message || '加载任务详情失败')
      }
    },
    closeDetailDialog() {
      this.detailDialogVisible = false
      this.selectedJob = null
    },
    async confirmCancel(job) {
      // TODO: 调用取消任务API
      alert('取消功能待实现')
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString()
    },
    formatStatus(status) {
      const statusMap = {
        pending: '等待中',
        running: '运行中',
        success: '成功',
        failed: '失败'
      }
      return statusMap[status] || status
    },
    formatJobType(type) {
      const typeMap = {
        osdeploy: 'OS部署',
        hardware: '硬件采集'
      }
      return typeMap[type] || type
    },
    getStatusClass(status) {
      const classMap = {
        pending: 'status-pending',
        running: 'status-running',
        success: 'status-success',
        failed: 'status-failed'
      }
      return classMap[status] || ''
    }
  }
}
</script>

<style scoped>
.jobs-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.jobs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.jobs-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-select, .search-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 140px;
}

.search-input {
  width: 180px;
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

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #f56c6c;
}

.jobs-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1000px;
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

/* 状态样式 */
.status-pending { color: #909399; }
.status-running { color: #409eff; }
.status-success { color: #67c23a; }
.status-failed { color: #f56c6c; }

/* 进度条 */
.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  width: 80px;
  height: 8px;
  background: #e4e4e4;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #409eff;
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: #666;
  min-width: 35px;
}

/* 按钮样式 */
.btn-detail, .btn-cancel {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 6px;
}

.btn-detail {
  background: #409eff;
  color: white;
}

.btn-detail:hover {
  background: #66b1ff;
}

.btn-cancel {
  background: #f56c6c;
  color: white;
}

.btn-cancel:hover {
  background: #f78989;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #eee;
}

.pagination button {
  padding: 6px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
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
}

.dialog-wide {
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
  max-height: 60vh;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
}

/* 详情样式 */
.job-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  color: #666;
  font-size: 12px;
}

.detail-item span {
  color: #333;
  font-size: 14px;
}

.error-message {
  color: #f56c6c;
}

.result-json {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  margin: 0;
}
</style>