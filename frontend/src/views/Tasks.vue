<template>
  <div class="tasks-container">
    <div class="tasks-header">
      <div class="header-actions">
        <select v-model="filterType" class="filter-select" @change="handleFilter">
          <option value="">全部类型</option>
          <option value="os_install">系统安装</option>
          <option value="os_migrate">系统迁移</option>
          <option value="safeguard_deploy">安全部署</option>
          <option value="safeguard_rollback">安全回滚</option>
          <option value="hardware_collect">硬件采集</option>
          <option value="repo_sync">仓库同步</option>
        </select>
        <select v-model="filterStatus" class="filter-select" @change="handleFilter">
          <option value="">全部状态</option>
          <option value="pending">等待中</option>
          <option value="running">运行中</option>
          <option value="success">成功</option>
          <option value="failed">失败</option>
        </select>
        <input v-model="searchTarget" type="text" placeholder="搜索目标" class="search-input" @keyup.enter="handleSearch" />
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="tasks-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>任务ID</th>
            <th>类型</th>
            <th>目标</th>
            <th>状态</th>
            <th>进度</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.id">
            <td>{{ task.id }}</td>
            <td>{{ task.job_id }}</td>
            <td>{{ formatType(task.job_type) }}</td>
            <td>{{ task.target }}</td>
            <td>
              <span :class="getStatusClass(task.status)">{{ formatStatus(task.status) }}</span>
            </td>
            <td>
              <div class="progress-bar-small">
                <div class="progress-fill" :style="{ width: task.progress + '%' }" :class="getProgressClass(task.status)"></div>
              </div>
              <span class="progress-text">{{ task.progress }}%</span>
            </td>
            <td>{{ formatDate(task.created_at) }}</td>
            <td>
              <button class="btn-view" @click="openDetailDialog(task)">详情</button>
            </td>
          </tr>
          <tr v-if="tasks.length === 0">
            <td colspan="8" class="empty-text">暂无数据</td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button :disabled="page <= 1" @click="handlePageChange(page - 1)">上一页</button>
        <span class="page-info">第 {{ page }} / {{ totalPages }} 页</span>
        <button :disabled="page >= totalPages" @click="handlePageChange(page + 1)">下一页</button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="detailDialogVisible" class="dialog-overlay" @click.self="closeDetailDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>任务详情</h3>
          <button class="dialog-close" @click="closeDetailDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="selectedTask">
            <p><strong>任务ID:</strong> {{ selectedTask.job_id }}</p>
            <p><strong>类型:</strong> {{ formatType(selectedTask.job_type) }}</p>
            <p><strong>目标:</strong> {{ selectedTask.target }}</p>
            <p><strong>状态:</strong> <span :class="getStatusClass(selectedTask.status)">{{ formatStatus(selectedTask.status) }}</span></p>
            <p><strong>进度:</strong> {{ selectedTask.progress }}%</p>
            <p v-if="selectedTask.error_message"><strong>错误信息:</strong> <span class="error-text">{{ selectedTask.error_message }}</span></p>
            <p v-if="selectedTask.result"><strong>结果:</strong> <pre class="result-pre">{{ JSON.stringify(selectedTask.result, null, 2) }}</pre></p>
            <p><strong>创建时间:</strong> {{ formatDate(selectedTask.created_at) }}</p>
            <p><strong>更新时间:</strong> {{ formatDate(selectedTask.updated_at) }}</p>
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
import { getTasks } from '@/api/task'

export default {
  name: 'Tasks',
  data() {
    return {
      tasks: [],
      loading: false,
      error: '',
      searchTarget: '',
      filterType: '',
      filterStatus: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      detailDialogVisible: false,
      selectedTask: null,
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize) || 1
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
        const params = { page: this.page, page_size: this.pageSize }
        if (this.searchTarget) params.search = this.searchTarget
        if (this.filterType) params.job_type = this.filterType
        if (this.filterStatus) params.status = this.filterStatus
        const res = await getTasks(params)
        this.tasks = res.results || res || []
        this.totalCount = res.count || this.tasks.length
      } catch (e) {
        this.error = e.message || '加载任务列表失败'
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.page = 1
      this.loadTasks()
    },
    handleFilter() {
      this.page = 1
      this.loadTasks()
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadTasks()
    },
    openDetailDialog(task) {
      this.selectedTask = task
      this.detailDialogVisible = true
    },
    closeDetailDialog() {
      this.detailDialogVisible = false
      this.selectedTask = null
    },
    formatType(type) {
      const map = {
        os_install: '系统安装',
        os_migrate: '系统迁移',
        safeguard_deploy: '安全部署',
        safeguard_rollback: '安全回滚',
        hardware_collect: '硬件采集',
        repo_sync: '仓库同步',
      }
      return map[type] || type
    },
    formatStatus(status) {
      const map = {
        pending: '等待中',
        running: '运行中',
        success: '成功',
        failed: '失败',
      }
      return map[status] || status
    },
    getStatusClass(status) {
      const map = {
        pending: 'status-pending',
        running: 'status-running',
        success: 'status-success',
        failed: 'status-failed',
      }
      return map[status] || ''
    },
    getProgressClass(status) {
      const map = {
        pending: 'progress-pending',
        running: 'progress-running',
        success: 'progress-success',
        failed: 'progress-failed',
      }
      return map[status] || ''
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString()
    }
  }
}
</script>

<style scoped>
.tasks-container { padding: 20px; max-width: 1400px; margin: 0 auto; min-height: calc(100vh - 100px); }
.tasks-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
.tasks-header h2 { margin: 0; color: #333; }
.header-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.filter-select, .search-input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; }
.search-input { width: 180px; }
.loading, .error { text-align: center; padding: 40px; }
.error { color: #f56c6c; }
.tasks-table { background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); overflow-x: auto; }
table { width: 100%; border-collapse: collapse; min-width: 900px; }
th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; }
th { background: #f5f5f5; font-weight: 600; }
.empty-text { text-align: center; color: #999; }
.progress-bar-small { width: 100px; height: 8px; background: #ebeef5; border-radius: 4px; overflow: hidden; display: inline-block; vertical-align: middle; }
.progress-fill { height: 100%; transition: width 0.3s; }
.progress-text { font-size: 12px; color: #666; margin-left: 6px; }
.progress-pending { background: #909399; }
.progress-running { background: #409eff; }
.progress-success { background: #67c23a; }
.progress-failed { background: #f56c6c; }
.status-pending { color: #909399; }
.status-running { color: #409eff; }
.status-success { color: #67c23a; }
.status-failed { color: #f56c6c; }
.btn-view { padding: 6px 12px; background: #409eff; color: white; border: none; border-radius: 4px; cursor: pointer; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 12px; padding: 16px; border-top: 1px solid #eee; }
.pagination button { padding: 6px 16px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; }
.pagination button:disabled { color: #ccc; cursor: not-allowed; }
.dialog-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: white; border-radius: 8px; width: 500px; max-width: 90%; }
.dialog-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #eee; }
.dialog-header h3 { margin: 0; }
.dialog-close { background: none; border: none; font-size: 24px; cursor: pointer; color: #999; }
.dialog-body { padding: 20px; }
.dialog-body p { margin: 8px 0; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 20px; border-top: 1px solid #eee; }
.btn-cancel { padding: 8px 16px; background: #fff; color: #333; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; }
.error-text { color: #f56c6c; }
.result-pre { background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px; overflow-x: auto; white-space: pre-wrap; word-break: break-all; }
</style>
