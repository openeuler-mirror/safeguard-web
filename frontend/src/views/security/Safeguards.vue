<template>
  <div class="safeguards-container">
    <div class="safeguards-header">
      <h2>Safeguard 部署管理</h2>
      <div class="header-actions">
        <input
          v-model="searchName"
          type="text"
          placeholder="搜索名称"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <select v-model="filterStatus" class="filter-select" @change="handleFilter">
          <option value="">全部状态</option>
          <option value="pending">等待中</option>
          <option value="running">运行中</option>
          <option value="success">成功</option>
          <option value="failed">失败</option>
        </select>
        <button class="btn-primary" @click="openCreateDialog">创建部署</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="safeguards-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>安全组件</th>
            <th>架构</th>
            <th>目标主机</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="sg in safeguards" :key="sg.id">
            <td>{{ sg.id }}</td>
            <td>{{ sg.name }}</td>
            <td>{{ sg.safeguard_type }}</td>
            <td>{{ formatArch(sg.arch) }}</td>
            <td>{{ sg.host || '-' }}</td>
            <td>
              <span :class="getStatusClass(sg.status)">{{ formatStatus(sg.status) }}</span>
            </td>
            <td>{{ formatDate(sg.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(sg)">编辑</button>
              <button v-if="sg.status === 'pending' || sg.status === 'failed'" class="btn-primary" @click="handleDeploy(sg)">部署</button>
              <button v-if="sg.status === 'success'" class="btn-warning" @click="handleRollback(sg)">回滚</button>
              <button class="btn-danger" @click="confirmDelete(sg)">删除</button>
            </td>
          </tr>
          <tr v-if="safeguards.length === 0">
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
          <h3>{{ isEdit ? '编辑部署' : '创建部署' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>名称 <span class="required">*</span></label>
            <input v-model="form.name" type="text" placeholder="请输入部署名称" :class="{ 'input-error': errors.name }" />
            <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
          </div>
          <div class="form-item">
            <label>安全组件类型</label>
            <select v-model="form.safeguard_type">
              <option value="safeguardx86">Safeguard X86</option>
            </select>
          </div>
          <div class="form-item">
            <label>架构</label>
            <select v-model="form.arch">
              <option value="x86">X86</option>
              <option value="arm">ARM</option>
            </select>
          </div>
          <div class="form-item">
            <label>目标主机IP</label>
            <input v-model="form.host" type="text" placeholder="留空表示本地部署" />
          </div>
          <div class="form-item">
            <label>用户名</label>
            <input v-model="form.username" type="text" placeholder="SSH用户名" />
          </div>
          <div class="form-item">
            <label>密码</label>
            <input v-model="form.password" type="password" placeholder="SSH密码" />
          </div>
          <div class="form-item">
            <label>端口</label>
            <input v-model="form.port" type="text" placeholder="默认22" />
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
          <p>确定删除部署 <strong>{{ selectedSafeguard?.name }}</strong> 吗？</p>
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
import { getSafeguards, createSafeguard, updateSafeguard, deleteSafeguard, deploySafeguard, rollbackSafeguard } from '@/api/security'

export default {
  name: 'Safeguards',
  data() {
    return {
      safeguards: [],
      loading: false,
      error: '',
      searchName: '',
      filterStatus: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      dialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedSafeguard: null,
      formError: '',
      errors: {},
      form: {
        name: '',
        safeguard_type: 'safeguardx86',
        arch: 'x86',
        host: '',
        username: '',
        password: '',
        port: '22',
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
    this.loadSafeguards()
  },
  methods: {
    async loadSafeguards() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        if (this.searchName) params.search = this.searchName
        if (this.filterStatus) params.status = this.filterStatus
        const res = await getSafeguards(params)
        this.safeguards = res.results || res || []
        this.totalCount = res.count || this.safeguards.length
      } catch (e) {
        this.error = e.message || '加载部署列表失败'
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.page = 1
      this.loadSafeguards()
    },
    handleFilter() {
      this.page = 1
      this.loadSafeguards()
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadSafeguards()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        name: '',
        safeguard_type: 'safeguardx86',
        arch: 'x86',
        host: '',
        username: '',
        password: '',
        port: '22',
        description: ''
      }
      this.dialogVisible = true
    },
    openEditDialog(sg) {
      this.isEdit = true
      this.selectedSafeguard = sg
      this.formError = ''
      this.errors = {}
      this.form = {
        name: sg.name,
        safeguard_type: sg.safeguard_type,
        arch: sg.arch,
        host: sg.host || '',
        username: sg.username || '',
        password: sg.password || '',
        port: sg.port || '22',
        description: sg.description || ''
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

      if (!this.form.name.trim()) {
        this.errors.name = '请输入名称'
        return
      }

      try {
        if (this.isEdit) {
          await updateSafeguard(this.selectedSafeguard.id, this.form)
        } else {
          await createSafeguard(this.form)
        }
        this.closeDialog()
        this.loadSafeguards()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
      }
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    confirmDelete(sg) {
      this.selectedSafeguard = sg
      this.deleteDialogVisible = true
    },
    async handleDelete() {
      try {
        await deleteSafeguard(this.selectedSafeguard.id)
        this.closeDeleteDialog()
        this.loadSafeguards()
      } catch (e) {
        alert(e.message || '删除失败')
      }
    },
    async handleDeploy(sg) {
      try {
        await deploySafeguard(sg.id)
        alert('部署任务已启动')
        this.loadSafeguards()
      } catch (e) {
        alert(e.message || '部署启动失败')
      }
    },
    async handleRollback(sg) {
      try {
        await rollbackSafeguard(sg.id)
        alert('回滚任务已启动')
        this.loadSafeguards()
      } catch (e) {
        alert(e.message || '回滚启动失败')
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString()
    },
    formatArch(arch) {
      const map = { x86: 'X86', arm: 'ARM' }
      return map[arch] || arch
    },
    formatStatus(status) {
      const map = {
        pending: '等待中',
        running: '运行中',
        success: '成功',
        failed: '失败'
      }
      return map[status] || status
    },
    getStatusClass(status) {
      const map = {
        pending: 'status-pending',
        running: 'status-running',
        success: 'status-success',
        failed: 'status-failed'
      }
      return map[status] || ''
    }
  }
}
</script>

<style scoped>
.safeguards-container {
  padding: 20px;
}

.safeguards-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.safeguards-header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn-primary {
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.btn-edit {
  padding: 4px 12px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
}

.btn-warning {
  padding: 4px 12px;
  background-color: #faad14;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
}

.btn-danger {
  padding: 4px 12px;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.loading, .error {
  padding: 20px;
  text-align: center;
}

.error {
  color: #ff4d4f;
}

.safeguards-table table {
  width: 100%;
  border-collapse: collapse;
}

.safeguards-table th,
.safeguards-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

.safeguards-table th {
  background-color: #fafafa;
  font-weight: 600;
}

.empty-text {
  text-align: center;
  color: #999;
  padding: 40px !important;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.pagination button {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
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
  border-bottom: 1px solid #e8e8e8;
}

.dialog-header h3 {
  margin: 0;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
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
  border-top: 1px solid #e8e8e8;
}

.form-item {
  margin-bottom: 16px;
}

.form-item label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-item .required {
  color: #ff4d4f;
}

.form-item input,
.form-item select,
.form-item textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-item input.input-error,
.form-item select.input-error {
  border-color: #ff4d4f;
}

.field-error {
  color: #ff4d4f;
  font-size: 12px;
  margin-top: 4px;
}

.form-error-summary {
  color: #ff4d4f;
  margin-bottom: 16px;
  padding: 10px;
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
}

.warning-text {
  color: #ff4d4f;
  font-size: 12px;
}

.btn-cancel {
  padding: 8px 16px;
  background-color: #fafafa;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
}

.status-pending {
  color: #faad14;
}

.status-running {
  color: #1890ff;
}

.status-success {
  color: #52c41a;
}

.status-failed {
  color: #ff4d4f;
}
</style>