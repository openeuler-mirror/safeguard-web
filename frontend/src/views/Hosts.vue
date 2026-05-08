<template>
  <div class="hosts-container">
    <div class="hosts-header">
      <h2>主机管理</h2>
      <div class="header-actions">
        <select v-model="filterCluster" class="filter-select" @change="handleFilter">
          <option value="">全部集群</option>
          <option v-for="c in clusterTree" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select v-model="filterStatus" class="filter-select" @change="handleFilter">
          <option value="">全部状态</option>
          <option value="online">在线</option>
          <option value="offline">离线</option>
        </select>
        <input
          v-model="searchName"
          type="text"
          placeholder="搜索主机名/IP"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="btn-primary" @click="openCreateDialog">创建主机</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="hosts-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>主机名</th>
            <th>IP地址</th>
            <th>端口</th>
            <th>用户名</th>
            <th>集群</th>
            <th>状态</th>
            <th>操作系统</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="host in hosts" :key="host.id">
            <td>{{ host.id }}</td>
            <td>{{ host.hostname }}</td>
            <td>{{ host.ip_address }}</td>
            <td>{{ host.port }}</td>
            <td>{{ host.username }}</td>
            <td>{{ host.cluster_name || '-' }}</td>
            <td>
              <span :class="host.status === 'online' ? 'status-online' : 'status-offline'">
                {{ host.status === 'online' ? '在线' : '离线' }}
              </span>
            </td>
            <td>{{ host.os_type || '-' }}</td>
            <td>{{ formatDate(host.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(host)">编辑</button>
              <button class="btn-danger" @click="confirmDelete(host)">删除</button>
            </td>
          </tr>
          <tr v-if="hosts.length === 0">
            <td colspan="10" class="empty-text">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建/编辑弹窗 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑主机' : '创建主机' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>主机名 <span class="required">*</span></label>
            <input v-model="form.hostname" type="text" placeholder="请输入主机名" :class="{ 'input-error': errors.hostname }" />
            <span v-if="errors.hostname" class="field-error">{{ errors.hostname }}</span>
          </div>
          <div class="form-item">
            <label>IP地址 <span class="required">*</span></label>
            <input v-model="form.ip_address" type="text" placeholder="请输入IP地址" :class="{ 'input-error': errors.ip_address }" />
            <span v-if="errors.ip_address" class="field-error">{{ errors.ip_address }}</span>
          </div>
          <div class="form-item">
            <label>端口</label>
            <input v-model.number="form.port" type="number" placeholder="22" :class="{ 'input-error': errors.port }" />
            <span v-if="errors.port" class="field-error">{{ errors.port }}</span>
          </div>
          <div class="form-item">
            <label>用户名 <span class="required">*</span></label>
            <input v-model="form.username" type="text" placeholder="请输入用户名" :class="{ 'input-error': errors.username }" />
            <span v-if="errors.username" class="field-error">{{ errors.username }}</span>
          </div>
          <div class="form-item">
            <label>密码</label>
            <input v-model="form.password" type="password" placeholder="请输入密码" :class="{ 'input-error': errors.password }" />
            <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
          </div>
          <div class="form-item">
            <label>集群</label>
            <select v-model="form.cluster" :class="{ 'input-error': errors.cluster }">
              <option :value="null">无</option>
              <option v-for="c in clusterTree" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
            <span v-if="errors.cluster" class="field-error">{{ errors.cluster }}</span>
          </div>
          <div class="form-item">
            <label>状态</label>
            <select v-model="form.status" :class="{ 'input-error': errors.status }">
              <option value="offline">离线</option>
              <option value="online">在线</option>
            </select>
            <span v-if="errors.status" class="field-error">{{ errors.status }}</span>
          </div>
          <div class="form-item">
            <label>操作系统</label>
            <input v-model="form.os_type" type="text" placeholder="如: CentOS 7.9" :class="{ 'input-error': errors.os_type }" />
            <span v-if="errors.os_type" class="field-error">{{ errors.os_type }}</span>
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
          <p>确定删除主机 <strong>{{ selectedHost?.hostname }}</strong> 吗？</p>
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
import { getHosts, createHost, updateHost, deleteHost, getClusterTree } from '@/api/host'

export default {
  name: 'Hosts',
  data() {
    return {
      hosts: [],
      clusterTree: [],
      loading: false,
      error: '',
      searchName: '',
      filterCluster: '',
      filterStatus: '',
      dialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedHost: null,
      formError: '',
      errors: {},
      form: {
        hostname: '',
        ip_address: '',
        port: 22,
        username: '',
        password: '',
        cluster: null,
        status: 'offline',
        os_type: ''
      }
    }
  },
  mounted() {
    this.loadHosts()
    this.loadClusterTree()
  },
  methods: {
    async loadHosts() {
      this.loading = true
      this.error = ''
      try {
        const params = {}
        if (this.searchName) params.search = this.searchName
        if (this.filterCluster) params.cluster = this.filterCluster
        if (this.filterStatus) params.status = this.filterStatus
        const res = await getHosts(params)
        this.hosts = res.data.results || res.data
      } catch (e) {
        this.error = e.response?.data?.error || '加载主机列表失败'
      } finally {
        this.loading = false
      }
    },
    async loadClusterTree() {
      try {
        const res = await getClusterTree()
        this.clusterTree = res.data || []
      } catch (e) {
        console.error('加载集群树下拉失败', e)
      }
    },
    handleSearch() {
      this.loadHosts()
    },
    handleFilter() {
      this.loadHosts()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        hostname: '',
        ip_address: '',
        port: 22,
        username: '',
        password: '',
        cluster: null,
        status: 'offline',
        os_type: ''
      }
      this.dialogVisible = true
    },
    openEditDialog(host) {
      this.isEdit = true
      this.selectedHost = host
      this.formError = ''
      this.errors = {}
      this.form = {
        hostname: host.hostname,
        ip_address: host.ip_address,
        port: host.port,
        username: host.username,
        password: '',
        cluster: host.cluster,
        status: host.status,
        os_type: host.os_type || ''
      }
      this.dialogVisible = true
    },
    closeDialog() {
      this.dialogVisible = false
      this.formError = ''
      this.errors = {}
    },
    async submitForm() {
      // 清除之前的错误
      this.formError = ''
      this.errors = {}

      // 前端验证
      if (!this.form.hostname.trim()) {
        this.errors.hostname = '请输入主机名'
        return
      }
      if (!this.form.ip_address.trim()) {
        this.errors.ip_address = '请输入IP地址'
        return
      }
      if (!this.form.username.trim()) {
        this.errors.username = '请输入用户名'
        return
      }

      try {
        const data = { ...this.form }
        if (!data.password) delete data.password
        if (!data.cluster) data.cluster = null
        if (this.isEdit) {
          await updateHost(this.selectedHost.id, data)
        } else {
          await createHost(data)
        }
        this.closeDialog()
        this.loadHosts()
      } catch (e) {
        const errorData = e.response?.data
        if (errorData) {
          // 解析字段错误
          const fieldErrors = {}
          let generalError = ''

          for (const [field, messages] of Object.entries(errorData)) {
            if (Array.isArray(messages)) {
              if (field === 'detail' || field === 'non_field_errors') {
                generalError = messages.join(', ')
              } else {
                fieldErrors[field] = messages.join(', ')
              }
            } else if (typeof messages === 'string') {
              if (field === 'detail') {
                generalError = messages
              } else {
                fieldErrors[field] = messages
              }
            }
          }

          if (generalError) {
            this.formError = generalError
          }
          this.errors = fieldErrors
        } else {
          this.formError = '操作失败，请稍后重试'
        }
      }
    },
    confirmDelete(host) {
      this.selectedHost = host
      this.deleteDialogVisible = true
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    async handleDelete() {
      try {
        await deleteHost(this.selectedHost.id)
        this.closeDeleteDialog()
        this.loadHosts()
      } catch (e) {
        alert(e.response?.data?.error || '删除失败')
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.hosts-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.hosts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.hosts-header h2 {
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

.hosts-table {
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

.status-online {
  color: #67c23a;
}

.status-offline {
  color: #909399;
}

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

.required {
  color: #f56c6c;
}

.form-item input,
.form-item select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-item select {
  background: white;
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

.btn-danger {
  padding: 8px 16px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-danger:hover {
  background: #f78989;
}
</style>
