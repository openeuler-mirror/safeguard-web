<template>
  <div class="health-monitors-container">
    <div class="health-monitors-header">
      <div class="header-actions">
        <select v-model="filterPool" class="filter-select" @change="handleFilter">
          <option value="">全部后端池</option>
          <option v-for="pool in pools" :key="pool.id" :value="pool.id">{{ pool.name }}</option>
        </select>
        <select v-model="filterType" class="filter-select" @change="handleFilter">
          <option value="">全部类型</option>
          <option value="tcp">TCP</option>
          <option value="http">HTTP</option>
          <option value="ping">PING</option>
        </select>
        <button class="btn-primary" @click="openCreateDialog">创建健康检查</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="health-monitors-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>后端池</th>
            <th>类型</th>
            <th>检查间隔(秒)</th>
            <th>超时(秒)</th>
            <th>重试次数</th>
            <th>描述</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="monitor in monitors" :key="monitor.id">
            <td>{{ monitor.id }}</td>
            <td>{{ monitor.pool_name }}</td>
            <td>
              <span :class="getTypeClass(monitor.monitor_type)">{{ formatType(monitor.monitor_type) }}</span>
            </td>
            <td>{{ monitor.interval }}</td>
            <td>{{ monitor.timeout }}</td>
            <td>{{ monitor.retry }}</td>
            <td>{{ monitor.description || '-' }}</td>
            <td>{{ formatDate(monitor.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(monitor)">编辑</button>
              <button class="btn-danger" @click="confirmDelete(monitor)">删除</button>
            </td>
          </tr>
          <tr v-if="monitors.length === 0">
            <td colspan="9" class="empty-text">暂无数据</td>
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

    <!-- 创建/编辑弹窗 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑健康检查' : '创建健康检查' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>后端池 <span class="required">*</span></label>
            <select v-model="form.pool" :class="{ 'input-error': errors.pool }" :disabled="isEdit">
              <option value="">请选择后端池</option>
              <option v-for="pool in pools" :key="pool.id" :value="pool.id">{{ pool.name }}</option>
            </select>
            <span v-if="errors.pool" class="field-error">{{ errors.pool }}</span>
          </div>
          <div class="form-item">
            <label>检查类型 <span class="required">*</span></label>
            <select v-model="form.monitor_type" :class="{ 'input-error': errors.monitor_type }">
              <option value="tcp">TCP</option>
              <option value="http">HTTP</option>
              <option value="ping">PING</option>
            </select>
            <span v-if="errors.monitor_type" class="field-error">{{ errors.monitor_type }}</span>
          </div>
          <div class="form-item">
            <label>检查间隔(秒)</label>
            <input v-model.number="form.interval" type="number" placeholder="默认5" min="1" max="3600" />
          </div>
          <div class="form-item">
            <label>超时(秒)</label>
            <input v-model.number="form.timeout" type="number" placeholder="默认3" min="1" max="300" />
          </div>
          <div class="form-item">
            <label>重试次数</label>
            <input v-model.number="form.retry" type="number" placeholder="默认3" min="1" max="10" />
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="form.description" placeholder="请输入描述信息" rows="3"></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="submitForm">确定</button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="deleteDialogVisible" class="dialog-overlay" @click.self="closeDeleteDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>确认删除</h3>
          <button class="dialog-close" @click="closeDeleteDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <p>确定删除后端池 <strong>{{ selectedMonitor?.pool_name }}</strong> 的健康检查吗？</p>
          <p class="warning-text">删除后无法恢复</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDeleteDialog">取消</button>
          <button class="btn-danger" @click="handleDelete">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getHealthMonitors, createHealthMonitor, updateHealthMonitor, deleteHealthMonitor, getPools } from '@/api/network'

export default {
  name: 'HealthMonitors',
  data() {
    return {
      monitors: [],
      pools: [],
      loading: false,
      error: '',
      filterPool: '',
      filterType: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      dialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedMonitor: null,
      formError: '',
      errors: {},
      form: {
        pool: '',
        monitor_type: 'tcp',
        interval: 5,
        timeout: 3,
        retry: 3,
        description: ''
      }
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize) || 1
    }
  },
  mounted() {
    this.loadPools()
    this.loadMonitors()
  },
  methods: {
    async loadPools() {
      try {
        const res = await getPools({ page_size: 100 })
        this.pools = res.results || res || []
      } catch (e) {
        console.error('加载后端池失败:', e)
      }
    },
    async loadMonitors() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        if (this.filterPool) params.pool = this.filterPool
        if (this.filterType) params.monitor_type = this.filterType
        const res = await getHealthMonitors(params)
        this.monitors = res.results || res || []
        this.totalCount = res.count || this.monitors.length
      } catch (e) {
        this.error = e.message || '加载健康检查列表失败'
      } finally {
        this.loading = false
      }
    },
    handleFilter() {
      this.page = 1
      this.loadMonitors()
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadMonitors()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        pool: this.filterPool || '',
        monitor_type: 'tcp',
        interval: 5,
        timeout: 3,
        retry: 3,
        description: ''
      }
      this.dialogVisible = true
    },
    openEditDialog(monitor) {
      this.isEdit = true
      this.selectedMonitor = monitor
      this.formError = ''
      this.errors = {}
      this.form = {
        pool: monitor.pool,
        monitor_type: monitor.monitor_type,
        interval: monitor.interval,
        timeout: monitor.timeout,
        retry: monitor.retry,
        description: monitor.description || ''
      }
      this.dialogVisible = true
    },
    closeDialog() {
      this.dialogVisible = false
      this.formError = ''
      this.errors = {}
    },
    async submitForm() {
      this.formError = ''
      this.errors = {}

      if (!this.form.pool) {
        this.errors.pool = '请选择后端池'
        return
      }

      try {
        if (this.isEdit) {
          await updateHealthMonitor(this.selectedMonitor.id, this.form)
        } else {
          await createHealthMonitor(this.form)
        }
        this.closeDialog()
        this.loadMonitors()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
      }
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    confirmDelete(monitor) {
      this.selectedMonitor = monitor
      this.deleteDialogVisible = true
    },
    async handleDelete() {
      try {
        await deleteHealthMonitor(this.selectedMonitor.id)
        this.closeDeleteDialog()
        this.loadMonitors()
      } catch (e) {
        alert(e.message || '删除失败')
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString()
    },
    formatType(type) {
      const map = { tcp: 'TCP', http: 'HTTP', ping: 'PING' }
      return map[type] || type
    },
    getTypeClass(type) {
      const map = { tcp: 'type-tcp', http: 'type-http', ping: 'type-ping' }
      return map[type] || ''
    }
  }
}
</script>

<style scoped>
.health-monitors-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.health-monitors-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.health-monitors-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 140px;
}

.btn-primary {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover {
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

.health-monitors-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 900px;
}

th, td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
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

.type-tcp { color: #409eff; }
.type-http { color: #67c23a; }
.type-ping { color: #f56c6c; }

.btn-edit, .btn-danger {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 6px;
}

.btn-edit {
  background: #67c23a;
  color: white;
}

.btn-edit:hover {
  background: #85ce61;
}

.btn-danger {
  background: #f56c6c;
  color: white;
}

.btn-danger:hover {
  background: #f78989;
}

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

.form-item {
  margin-bottom: 16px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-item label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-weight: 500;
}

.form-item input[type="text"],
.form-item input[type="number"],
.form-item select,
.form-item textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-item textarea {
  resize: vertical;
}

.required {
  color: #f56c6c;
}

.form-error-summary {
  background: #fef0f0;
  border: 1px solid #fde2e2;
  color: #f56c6c;
  padding: 10px 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
}

.input-error {
  border-color: #f56c6c !important;
}

.field-error {
  display: block;
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}

.warning-text {
  color: #f56c6c;
  font-size: 14px;
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
</style>