<template>
  <div class="listeners-container">
    <div class="listeners-header">
      <h2>监听器</h2>
      <div class="header-actions">
        <select v-model="filterLB" class="filter-select" @change="handleFilter">
          <option value="">全部负载均衡器</option>
          <option v-for="lb in lbs" :key="lb.id" :value="lb.id">{{ lb.name }}</option>
        </select>
        <select v-model="filterProtocol" class="filter-select" @change="handleFilter">
          <option value="">全部协议</option>
          <option value="tcp">TCP</option>
          <option value="http">HTTP</option>
          <option value="https">HTTPS</option>
        </select>
        <input
          v-model="searchName"
          type="text"
          placeholder="搜索名称"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="btn-primary" @click="openCreateDialog">创建监听器</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="listeners-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>负载均衡器</th>
            <th>协议</th>
            <th>端口</th>
            <th>描述</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="listener in listeners" :key="listener.id">
            <td>{{ listener.id }}</td>
            <td>{{ listener.name || '-' }}</td>
            <td>{{ listener.loadbalancer_name }}</td>
            <td>
              <span :class="getProtocolClass(listener.protocol)">{{ formatProtocol(listener.protocol) }}</span>
            </td>
            <td>{{ listener.port }}</td>
            <td>{{ listener.description || '-' }}</td>
            <td>{{ formatDate(listener.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(listener)">编辑</button>
              <button class="btn-danger" @click="confirmDelete(listener)">删除</button>
            </td>
          </tr>
          <tr v-if="listeners.length === 0">
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

    <!-- 创建/编辑弹窗 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑监听器' : '创建监听器' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>负载均衡器 <span class="required">*</span></label>
            <select v-model="form.loadbalancer" :class="{ 'input-error': errors.loadbalancer }">
              <option value="">请选择负载均衡器</option>
              <option v-for="lb in lbs" :key="lb.id" :value="lb.id">{{ lb.name }}</option>
            </select>
            <span v-if="errors.loadbalancer" class="field-error">{{ errors.loadbalancer }}</span>
          </div>
          <div class="form-item">
            <label>名称</label>
            <input v-model="form.name" type="text" placeholder="请输入名称(可选)" />
          </div>
          <div class="form-item">
            <label>协议 <span class="required">*</span></label>
            <select v-model="form.protocol" :class="{ 'input-error': errors.protocol }">
              <option value="tcp">TCP</option>
              <option value="http">HTTP</option>
              <option value="https">HTTPS</option>
            </select>
            <span v-if="errors.protocol" class="field-error">{{ errors.protocol }}</span>
          </div>
          <div class="form-item">
            <label>端口 <span class="required">*</span></label>
            <input v-model.number="form.port" type="number" placeholder="如: 80" min="1" max="65535" :class="{ 'input-error': errors.port }" />
            <span v-if="errors.port" class="field-error">{{ errors.port }}</span>
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
          <p>确定删除监听器 <strong>{{ selectedListener?.name || selectedListener?.id }}</strong> 吗？</p>
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
import { getListeners, createListener, updateListener, deleteListener, getLBs } from '@/api/network'

export default {
  name: 'Listeners',
  data() {
    return {
      listeners: [],
      lbs: [],
      loading: false,
      error: '',
      searchName: '',
      filterLB: '',
      filterProtocol: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      dialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedListener: null,
      formError: '',
      errors: {},
      form: {
        loadbalancer: '',
        name: '',
        protocol: 'tcp',
        port: 80,
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
    this.loadLBs()
    this.loadListeners()
  },
  methods: {
    async loadLBs() {
      try {
        const res = await getLBs({ page_size: 100 })
        this.lbs = res.results || res || []
      } catch (e) {
        console.error('加载负载均衡器失败:', e)
      }
    },
    async loadListeners() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        if (this.searchName) params.search = this.searchName
        if (this.filterLB) params.loadbalancer = this.filterLB
        if (this.filterProtocol) params.protocol = this.filterProtocol
        const res = await getListeners(params)
        this.listeners = res.results || res || []
        this.totalCount = res.count || this.listeners.length
      } catch (e) {
        this.error = e.message || '加载监听器列表失败'
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.page = 1
      this.loadListeners()
    },
    handleFilter() {
      this.page = 1
      this.loadListeners()
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadListeners()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        loadbalancer: '',
        name: '',
        protocol: 'tcp',
        port: 80,
        description: ''
      }
      this.dialogVisible = true
    },
    openEditDialog(listener) {
      this.isEdit = true
      this.selectedListener = listener
      this.formError = ''
      this.errors = {}
      this.form = {
        loadbalancer: listener.loadbalancer,
        name: listener.name || '',
        protocol: listener.protocol,
        port: listener.port,
        description: listener.description || ''
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

      if (!this.form.loadbalancer) {
        this.errors.loadbalancer = '请选择负载均衡器'
        return
      }
      if (!this.form.port || this.form.port < 1 || this.form.port > 65535) {
        this.errors.port = '请输入有效端口(1-65535)'
        return
      }

      try {
        if (this.isEdit) {
          await updateListener(this.selectedListener.id, this.form)
        } else {
          await createListener(this.form)
        }
        this.closeDialog()
        this.loadListeners()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
      }
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    confirmDelete(listener) {
      this.selectedListener = listener
      this.deleteDialogVisible = true
    },
    async handleDelete() {
      try {
        await deleteListener(this.selectedListener.id)
        this.closeDeleteDialog()
        this.loadListeners()
      } catch (e) {
        alert(e.message || '删除失败')
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString()
    },
    formatProtocol(protocol) {
      const map = { tcp: 'TCP', http: 'HTTP', https: 'HTTPS' }
      return map[protocol] || protocol
    },
    getProtocolClass(protocol) {
      const map = { tcp: 'protocol-tcp', http: 'protocol-http', https: 'protocol-https' }
      return map[protocol] || ''
    }
  }
}
</script>

<style scoped>
.listeners-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.listeners-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.listeners-header h2 {
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

.listeners-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
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

.protocol-tcp { color: #409eff; }
.protocol-http { color: #67c23a; }
.protocol-https { color: #f56c6c; }

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