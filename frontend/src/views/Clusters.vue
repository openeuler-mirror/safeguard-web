<template>
  <div class="clusters-container">
    <div class="clusters-header">
      <h2>集群管理</h2>
      <div class="header-actions">
        <input
          v-model="searchName"
          type="text"
          placeholder="搜索集群名称"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="btn-primary" @click="openCreateDialog">创建集群</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="clusters-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>集群名称</th>
            <th>描述</th>
            <th>vCenter ID</th>
            <th>主机数量</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cluster in clusters" :key="cluster.id">
            <td>{{ cluster.id }}</td>
            <td>{{ cluster.name }}</td>
            <td>{{ cluster.description || '-' }}</td>
            <td>{{ cluster.vcenter_id || '-' }}</td>
            <td>{{ cluster.host_count || 0 }}</td>
            <td>{{ formatDate(cluster.created_at) }}</td>
            <td>
              <button class="btn-info" @click="openHostDialog(cluster)">主机</button>
              <button class="btn-edit" @click="openEditDialog(cluster)">编辑</button>
              <button class="btn-delete" @click="confirmDelete(cluster)">删除</button>
            </td>
          </tr>
          <tr v-if="clusters.length === 0">
            <td colspan="7" class="empty-text">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建/编辑弹窗 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑集群' : '创建集群' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>集群名称 <span class="required">*</span></label>
            <input
              v-model="form.name"
              type="text"
              placeholder="请输入集群名称"
              maxlength="100"
              :class="{ 'input-error': errors.name }"
            />
            <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea
              v-model="form.description"
              placeholder="请输入描述"
              rows="3"
              :class="{ 'input-error': errors.description }"
            ></textarea>
            <span v-if="errors.description" class="field-error">{{ errors.description }}</span>
          </div>
          <div class="form-item">
            <label>vCenter ID</label>
            <input
              v-model="form.vcenter_id"
              type="text"
              placeholder="请输入vCenter ID"
              maxlength="100"
              :class="{ 'input-error': errors.vcenter_id }"
            />
            <span v-if="errors.vcenter_id" class="field-error">{{ errors.vcenter_id }}</span>
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
          <p>确定删除集群 <strong>{{ selectedCluster?.name }}</strong> 吗？</p>
          <p class="warning-text">删除后无法恢复</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDeleteDialog">取消</button>
          <button class="btn-danger" @click="handleDelete">确认删除</button>
        </div>
      </div>
    </div>

    <!-- 查看主机弹窗 -->
    <div v-if="hostDialogVisible" class="dialog-overlay" @click.self="closeHostDialog">
      <div class="dialog dialog-wide">
        <div class="dialog-header">
          <h3>{{ selectedCluster?.name }} - 主机列表</h3>
          <button class="dialog-close" @click="closeHostDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="hostsLoading" class="loading">加载中...</div>
          <div v-else-if="clusterHosts.length === 0" class="empty-text">该集群下没有主机</div>
          <table v-else class="hosts-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>主机名</th>
                <th>IP地址</th>
                <th>端口</th>
                <th>状态</th>
                <th>操作系统</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="host in clusterHosts" :key="host.id">
                <td>{{ host.id }}</td>
                <td>{{ host.hostname }}</td>
                <td>{{ host.ip_address }}</td>
                <td>{{ host.port }}</td>
                <td>
                  <span :class="host.status === 'online' ? 'status-online' : 'status-offline'">
                    {{ host.status === 'online' ? '在线' : '离线' }}
                  </span>
                </td>
                <td>{{ host.os_type || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeHostDialog">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getClusters, createCluster, updateCluster, deleteCluster, getClusterHosts } from '@/api/host'

export default {
  name: 'Clusters',
  data() {
    return {
      clusters: [],
      loading: false,
      error: '',
      searchName: '',
      dialogVisible: false,
      deleteDialogVisible: false,
      hostDialogVisible: false,
      isEdit: false,
      selectedCluster: null,
      formError: '',
      errors: {},
      form: {
        name: '',
        description: '',
        vcenter_id: ''
      },
      clusterHosts: [],
      hostsLoading: false
    }
  },
  mounted() {
    this.loadClusters()
  },
  methods: {
    async loadClusters() {
      this.loading = true
      this.error = ''
      try {
        const res = await getClusters()
        this.clusters = res.data.results || res.data
      } catch (e) {
        this.error = e.response?.data?.error || '加载集群列表失败'
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.loadClusters()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = { name: '', description: '', vcenter_id: '' }
      this.dialogVisible = true
    },
    openEditDialog(cluster) {
      this.isEdit = true
      this.selectedCluster = cluster
      this.formError = ''
      this.errors = {}
      this.form = {
        name: cluster.name,
        description: cluster.description || '',
        vcenter_id: cluster.vcenter_id || ''
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
        this.errors.name = '请输入集群名称'
        return
      }
      try {
        if (this.isEdit) {
          await updateCluster(this.selectedCluster.id, this.form)
        } else {
          await createCluster(this.form)
        }
        this.closeDialog()
        this.loadClusters()
      } catch (e) {
        const errorData = e.response?.data
        if (errorData) {
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
    confirmDelete(cluster) {
      this.selectedCluster = cluster
      this.deleteDialogVisible = true
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    async handleDelete() {
      try {
        await deleteCluster(this.selectedCluster.id)
        this.closeDeleteDialog()
        this.loadClusters()
      } catch (e) {
        alert(e.response?.data?.error || '删除失败')
      }
    },
    async openHostDialog(cluster) {
      this.selectedCluster = cluster
      this.hostDialogVisible = true
      this.clusterHosts = []
      this.hostsLoading = true
      try {
        const res = await getClusterHosts(cluster.id)
        this.clusterHosts = res.data
      } catch (e) {
        alert('加载主机列表失败')
      } finally {
        this.hostsLoading = false
      }
    },
    closeHostDialog() {
      this.hostDialogVisible = false
      this.clusterHosts = []
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
.clusters-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.clusters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.clusters-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
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

.clusters-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
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
  padding: 20px;
}

.btn-edit, .btn-delete, .btn-info {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 8px;
}

.btn-info {
  background: #909399;
  color: white;
}

.btn-info:hover {
  background: #a6a9ab;
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
  width: 480px;
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

/* 主机列表表格 */
.hosts-table {
  width: 100%;
  border-collapse: collapse;
}

.hosts-table th,
.hosts-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.hosts-table th {
  background: #f5f5f5;
  font-weight: 600;
}

.status-online {
  color: #67c23a;
}

.status-offline {
  color: #909399;
}
</style>
