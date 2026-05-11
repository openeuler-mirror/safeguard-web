<template>
  <div class="vms-container">
    <div class="vms-header">
      <h2>虚拟机管理</h2>
      <div class="header-actions">
        <select v-model="filterCluster" class="filter-select" @change="handleFilter">
          <option value="">全部集群</option>
          <option v-for="c in clusterTree" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select v-model="filterHost" class="filter-select" @change="handleFilter">
          <option value="">全部宿主机</option>
          <option v-for="h in hostList" :key="h.id" :value="h.id">{{ h.hostname }}</option>
        </select>
        <select v-model="filterStatus" class="filter-select" @change="handleFilter">
          <option value="">全部状态</option>
          <option value="stopped">已停止</option>
          <option value="running">运行中</option>
          <option value="paused">暂停</option>
          <option value="suspended">挂起</option>
        </select>
        <input
          v-model="searchName"
          type="text"
          placeholder="搜索VM名称/UUID/IP"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="btn-primary" @click="openCreateDialog">创建虚拟机</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="vms-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>VM名称</th>
            <th>UUID</th>
            <th>宿主机</th>
            <th>集群</th>
            <th>状态</th>
            <th>vCPU</th>
            <th>内存</th>
            <th>磁盘</th>
            <th>IP地址</th>
            <th>MAC地址</th>
            <th>操作系统</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="vm in vms" :key="vm.id">
            <td>{{ vm.id }}</td>
            <td>{{ vm.name }}</td>
            <td class="uuid-text">{{ vm.uuid }}</td>
            <td>{{ vm.host_name || '-' }}</td>
            <td>{{ vm.cluster_name || '-' }}</td>
            <td>
              <span :class="getStatusClass(vm.status)">
                {{ getStatusText(vm.status) }}
              </span>
            </td>
            <td>{{ vm.vcpu }}</td>
            <td>{{ formatBytes(vm.memory) }}</td>
            <td>{{ formatBytes(vm.disk) }}</td>
            <td>{{ vm.ip_address || '-' }}</td>
            <td>{{ vm.mac_address || '-' }}</td>
            <td>{{ vm.os_type || '-' }}</td>
            <td>{{ formatDate(vm.created_at) }}</td>
            <td>
              <button v-if="vm.status !== 'running'" class="btn-action btn-start" @click="handleStart(vm)" title="启动">启动</button>
              <button v-if="vm.status === 'running'" class="btn-action btn-stop" @click="handleStop(vm)" title="停止">停止</button>
              <button v-if="vm.status === 'running'" class="btn-action btn-reboot" @click="handleReboot(vm)" title="重启">重启</button>
              <button class="btn-edit" @click="openEditDialog(vm)">编辑</button>
              <button class="btn-delete" @click="confirmDelete(vm)">删除</button>
            </td>
          </tr>
          <tr v-if="vms.length === 0">
            <td colspan="14" class="empty-text">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建/编辑弹窗 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑虚拟机' : '创建虚拟机' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>VM名称 <span class="required">*</span></label>
            <input v-model="form.name" type="text" placeholder="请输入VM名称" :class="{ 'input-error': errors.name }" />
            <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
          </div>
          <div class="form-item">
            <label>UUID <span class="required">*</span></label>
            <input v-model="form.uuid" type="text" placeholder="请输入UUID" :class="{ 'input-error': errors.uuid }" />
            <span v-if="errors.uuid" class="field-error">{{ errors.uuid }}</span>
          </div>
          <div class="form-item">
            <label>宿主机 <span class="required">*</span></label>
            <select v-model="form.host" :class="{ 'input-error': errors.host }">
              <option :value="null">请选择宿主机</option>
              <option v-for="h in hostList" :key="h.id" :value="h.id">{{ h.hostname }} ({{ h.ip_address }})</option>
            </select>
            <span v-if="errors.host" class="field-error">{{ errors.host }}</span>
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
              <option value="stopped">已停止</option>
              <option value="running">运行中</option>
              <option value="paused">暂停</option>
              <option value="suspended">挂起</option>
            </select>
            <span v-if="errors.status" class="field-error">{{ errors.status }}</span>
          </div>
          <div class="form-row">
            <div class="form-item">
              <label>vCPU</label>
              <input v-model.number="form.vcpu" type="number" min="1" placeholder="1" :class="{ 'input-error': errors.vcpu }" />
              <span v-if="errors.vcpu" class="field-error">{{ errors.vcpu }}</span>
            </div>
            <div class="form-item">
              <label>内存(字节)</label>
              <input v-model.number="form.memory" type="number" min="0" placeholder="如: 4294967296" :class="{ 'input-error': errors.memory }" />
              <span v-if="errors.memory" class="field-error">{{ errors.memory }}</span>
            </div>
          </div>
          <div class="form-row">
            <div class="form-item">
              <label>磁盘(字节)</label>
              <input v-model.number="form.disk" type="number" min="0" placeholder="如: 107374182400" :class="{ 'input-error': errors.disk }" />
              <span v-if="errors.disk" class="field-error">{{ errors.disk }}</span>
            </div>
            <div class="form-item">
              <label>IP地址</label>
              <input v-model="form.ip_address" type="text" placeholder="如: 192.168.1.100" :class="{ 'input-error': errors.ip_address }" />
              <span v-if="errors.ip_address" class="field-error">{{ errors.ip_address }}</span>
            </div>
          </div>
          <div class="form-row">
            <div class="form-item">
              <label>MAC地址</label>
              <input v-model="form.mac_address" type="text" placeholder="如: 00:0c:29:ab:cd:ef" :class="{ 'input-error': errors.mac_address }" />
              <span v-if="errors.mac_address" class="field-error">{{ errors.mac_address }}</span>
            </div>
            <div class="form-item">
              <label>操作系统</label>
              <input v-model="form.os_type" type="text" placeholder="如: CentOS 7.9" :class="{ 'input-error': errors.os_type }" />
              <span v-if="errors.os_type" class="field-error">{{ errors.os_type }}</span>
            </div>
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
          <p>确定删除虚拟机 <strong>{{ selectedVM?.name }}</strong> 吗？</p>
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
import { getVMs, createVM, updateVM, deleteVM, startVM, stopVM, rebootVM, getClusterTree, getHosts } from '@/api/host'

export default {
  name: 'VMs',
  data() {
    return {
      vms: [],
      clusterTree: [],
      hostList: [],
      loading: false,
      error: '',
      searchName: '',
      filterCluster: '',
      filterHost: '',
      filterStatus: '',
      dialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedVM: null,
      formError: '',
      errors: {},
      form: {
        name: '',
        uuid: '',
        host: null,
        cluster: null,
        status: 'stopped',
        vcpu: 1,
        memory: 0,
        disk: 0,
        ip_address: '',
        mac_address: '',
        os_type: ''
      }
    }
  },
  mounted() {
    this.loadVMs()
    this.loadClusterTree()
    this.loadHostList()
  },
  methods: {
    async loadVMs() {
      this.loading = true
      this.error = ''
      try {
        const params = {}
        if (this.searchName) params.search = this.searchName
        if (this.filterCluster) params.cluster = this.filterCluster
        if (this.filterHost) params.host = this.filterHost
        if (this.filterStatus) params.status = this.filterStatus
        const res = await getVMs(params)
        this.vms = res.results || res || []
      } catch (e) {
        this.error = e.message || '加载虚拟机列表失败'
      } finally {
        this.loading = false
      }
    },
    async loadClusterTree() {
      try {
        const res = await getClusterTree()
        this.clusterTree = res || []
      } catch (e) {
        console.error('加载集群树下拉失败', e)
      }
    },
    async loadHostList() {
      try {
        const res = await getHosts()
        this.hostList = res.results || res || []
      } catch (e) {
        console.error('加载宿主机列表失败', e)
      }
    },
    handleSearch() {
      this.loadVMs()
    },
    handleFilter() {
      this.loadVMs()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        name: '',
        uuid: '',
        host: null,
        cluster: null,
        status: 'stopped',
        vcpu: 1,
        memory: 0,
        disk: 0,
        ip_address: '',
        mac_address: '',
        os_type: ''
      }
      this.dialogVisible = true
    },
    openEditDialog(vm) {
      this.isEdit = true
      this.selectedVM = vm
      this.formError = ''
      this.errors = {}
      this.form = {
        name: vm.name,
        uuid: vm.uuid,
        host: vm.host,
        cluster: vm.cluster,
        status: vm.status,
        vcpu: vm.vcpu,
        memory: vm.memory,
        disk: vm.disk,
        ip_address: vm.ip_address || '',
        mac_address: vm.mac_address || '',
        os_type: vm.os_type || ''
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
        this.errors.name = '请输入VM名称'
        return
      }
      if (!this.form.uuid.trim()) {
        this.errors.uuid = '请输入UUID'
        return
      }
      if (!this.form.host) {
        this.errors.host = '请选择宿主机'
        return
      }

      try {
        const data = { ...this.form }
        if (!data.cluster) data.cluster = null
        if (this.isEdit) {
          await updateVM(this.selectedVM.id, data)
        } else {
          await createVM(data)
        }
        this.closeDialog()
        this.loadVMs()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
        this.errors = {}
      }
    },
    confirmDelete(vm) {
      this.selectedVM = vm
      this.deleteDialogVisible = true
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    async handleDelete() {
      try {
        await deleteVM(this.selectedVM.id)
        this.closeDeleteDialog()
        this.loadVMs()
      } catch (e) {
        alert(e.message || '删除失败')
      }
    },
    async handleStart(vm) {
      try {
        await startVM(vm.id)
        this.loadVMs()
      } catch (e) {
        alert(e.message || '启动失败')
      }
    },
    async handleStop(vm) {
      try {
        await stopVM(vm.id)
        this.loadVMs()
      } catch (e) {
        alert(e.message || '停止失败')
      }
    },
    async handleReboot(vm) {
      try {
        await rebootVM(vm.id)
        this.loadVMs()
      } catch (e) {
        alert(e.message || '重启失败')
      }
    },
    getStatusClass(status) {
      const statusMap = {
        'running': 'status-running',
        'stopped': 'status-stopped',
        'paused': 'status-paused',
        'suspended': 'status-suspended'
      }
      return statusMap[status] || 'status-unknown'
    },
    getStatusText(status) {
      const statusMap = {
        'running': '运行中',
        'stopped': '已停止',
        'paused': '暂停',
        'suspended': '挂起'
      }
      return statusMap[status] || status
    },
    formatBytes(bytes) {
      if (!bytes || bytes === 0) return '-'
      const gb = bytes / (1024 * 1024 * 1024)
      if (gb >= 1) {
        return gb.toFixed(2) + ' GB'
      }
      const mb = bytes / (1024 * 1024)
      if (mb >= 1) {
        return mb.toFixed(2) + ' MB'
      }
      return bytes + ' B'
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
.vms-container {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.vms-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.vms-header h2 {
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
  width: 200px;
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

.vms-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1400px;
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

.uuid-text {
  font-family: monospace;
  font-size: 12px;
  color: #666;
}

.status-running {
  color: #67c23a;
}

.status-stopped {
  color: #909399;
}

.status-paused {
  color: #e6a23c;
}

.status-suspended {
  color: #f56c6c;
}

.status-unknown {
  color: #999;
}

.btn-edit, .btn-delete, .btn-action {
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

.btn-delete {
  background: #f56c6c;
  color: white;
}

.btn-delete:hover {
  background: #f78989;
}

.btn-action {
  color: white;
  min-width: 50px;
}

.btn-start {
  background: #67c23a;
}

.btn-start:hover {
  background: #85ce61;
}

.btn-stop {
  background: #e6a23c;
}

.btn-stop:hover {
  background: #ebb563;
}

.btn-reboot {
  background: #409eff;
}

.btn-reboot:hover {
  background: #66b1ff;
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
  width: 600px;
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

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-item {
  flex: 1;
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
