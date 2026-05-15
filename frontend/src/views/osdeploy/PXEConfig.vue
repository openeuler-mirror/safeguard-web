<template>
  <div class="pxe-config-container">
    <div class="pxe-config-header">
      <h2>PXE 服务器配置</h2>
      <div class="header-actions">
        <button class="btn-primary" @click="openCreateDialog">添加服务器</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="pxe-config-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>服务器IP</th>
            <th>网卡</th>
            <th>DHCP起始IP</th>
            <th>DHCP结束IP</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="server in servers" :key="server.id">
            <td>{{ server.id }}</td>
            <td>{{ server.server_ip }}</td>
            <td>{{ server.interface }}</td>
            <td>{{ server.dhcp_range_start }}</td>
            <td>{{ server.dhcp_range_end }}</td>
            <td>
              <span :class="getStatusClass(server.status)">
                {{ formatStatus(server.status) }}
              </span>
            </td>
            <td>{{ formatDate(server.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(server)">编辑</button>
              <button class="btn-danger" @click="confirmDelete(server)">删除</button>
            </td>
          </tr>
          <tr v-if="servers.length === 0">
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
          <h3>{{ isEdit ? '编辑PXE服务器' : '添加PXE服务器' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>服务器IP <span class="required">*</span></label>
            <input v-model="form.server_ip" type="text" placeholder="如: 192.168.1.100" :class="{ 'input-error': errors.server_ip }" />
            <span v-if="errors.server_ip" class="field-error">{{ errors.server_ip }}</span>
          </div>
          <div class="form-item">
            <label>网卡 <span class="required">*</span></label>
            <input v-model="form.interface" type="text" placeholder="如: eth0" :class="{ 'input-error': errors.interface }" />
            <span v-if="errors.interface" class="field-error">{{ errors.interface }}</span>
          </div>
          <div class="form-item">
            <label>DHCP起始IP <span class="required">*</span></label>
            <input v-model="form.dhcp_range_start" type="text" placeholder="如: 192.168.1.10" :class="{ 'input-error': errors.dhcp_range_start }" />
            <span v-if="errors.dhcp_range_start" class="field-error">{{ errors.dhcp_range_start }}</span>
          </div>
          <div class="form-item">
            <label>DHCP结束IP <span class="required">*</span></label>
            <input v-model="form.dhcp_range_end" type="text" placeholder="如: 192.168.1.200" :class="{ 'input-error': errors.dhcp_range_end }" />
            <span v-if="errors.dhcp_range_end" class="field-error">{{ errors.dhcp_range_end }}</span>
          </div>
          <div class="form-item">
            <label>状态</label>
            <select v-model="form.status">
              <option value="active">活跃</option>
              <option value="inactive">未激活</option>
            </select>
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
          <p>确定删除 PXE 服务器 <strong>{{ selectedServer?.server_ip }}</strong> 吗？</p>
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
import { getPXEServers, createPXEServer, updatePXEServer, deletePXEServer } from '@/api/osdeploy/pxe'

export default {
  name: 'PXEConfig',
  data() {
    return {
      servers: [],
      loading: false,
      error: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      dialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedServer: null,
      formError: '',
      errors: {},
      form: {
        server_ip: '',
        interface: 'eth0',
        dhcp_range_start: '',
        dhcp_range_end: '',
        status: 'active'
      }
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize) || 1
    }
  },
  mounted() {
    this.loadServers()
  },
  methods: {
    async loadServers() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        const res = await getPXEServers(params)
        this.servers = res.results || res || []
        this.totalCount = res.count || this.servers.length
      } catch (e) {
        this.error = e.message || '加载PXE服务器列表失败'
      } finally {
        this.loading = false
      }
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadServers()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        server_ip: '',
        interface: 'eth0',
        dhcp_range_start: '',
        dhcp_range_end: '',
        status: 'active'
      }
      this.dialogVisible = true
    },
    openEditDialog(server) {
      this.isEdit = true
      this.selectedServer = server
      this.formError = ''
      this.errors = {}
      this.form = {
        server_ip: server.server_ip,
        interface: server.interface,
        dhcp_range_start: server.dhcp_range_start,
        dhcp_range_end: server.dhcp_range_end,
        status: server.status
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

      if (!this.form.server_ip.trim()) {
        this.errors.server_ip = '请输入服务器IP'
        return
      }
      if (!this.form.interface.trim()) {
        this.errors.interface = '请输入网卡名称'
        return
      }
      if (!this.form.dhcp_range_start.trim()) {
        this.errors.dhcp_range_start = '请输入DHCP起始IP'
        return
      }
      if (!this.form.dhcp_range_end.trim()) {
        this.errors.dhcp_range_end = '请输入DHCP结束IP'
        return
      }

      try {
        if (this.isEdit) {
          await updatePXEServer(this.selectedServer.id, this.form)
        } else {
          await createPXEServer(this.form)
        }
        this.closeDialog()
        this.loadServers()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
      }
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    confirmDelete(server) {
      this.selectedServer = server
      this.deleteDialogVisible = true
    },
    async handleDelete() {
      try {
        await deletePXEServer(this.selectedServer.id)
        this.closeDeleteDialog()
        this.loadServers()
      } catch (e) {
        alert(e.message || '删除失败')
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString()
    },
    formatStatus(status) {
      const statusMap = {
        active: '活跃',
        inactive: '未激活'
      }
      return statusMap[status] || status
    },
    getStatusClass(status) {
      const classMap = {
        active: 'status-active',
        inactive: 'status-inactive'
      }
      return classMap[status] || ''
    }
  }
}
</script>

<style scoped>
.pxe-config-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.pxe-config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pxe-config-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
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

.pxe-config-table {
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

.status-active { color: #67c23a; }
.status-inactive { color: #909399; }

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

.form-item input,
.form-item select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
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

.btn-danger {
  padding: 8px 16px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>