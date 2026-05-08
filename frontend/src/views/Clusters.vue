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
          <div class="form-item">
            <label>集群名称 <span class="required">*</span></label>
            <input
              v-model="form.name"
              type="text"
              placeholder="请输入集群名称"
              maxlength="100"
            />
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea
              v-model="form.description"
              placeholder="请输入描述"
              rows="3"
            ></textarea>
          </div>
          <div class="form-item">
            <label>vCenter ID</label>
            <input
              v-model="form.vcenter_id"
              type="text"
              placeholder="请输入vCenter ID"
              maxlength="100"
            />
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
  </div>
</template>

<script>
import { getClusters, createCluster, updateCluster, deleteCluster } from '@/api/host'

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
      isEdit: false,
      selectedCluster: null,
      form: {
        name: '',
        description: '',
        vcenter_id: ''
      }
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
      this.form = { name: '', description: '', vcenter_id: '' }
      this.dialogVisible = true
    },
    openEditDialog(cluster) {
      this.isEdit = true
      this.selectedCluster = cluster
      this.form = {
        name: cluster.name,
        description: cluster.description || '',
        vcenter_id: cluster.vcenter_id || ''
      }
      this.dialogVisible = true
    },
    closeDialog() {
      this.dialogVisible = false
    },
    async submitForm() {
      if (!this.form.name.trim()) {
        alert('请输入集群名称')
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
        alert(e.response?.data?.error || '操作失败')
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
}

.btn-edit, .btn-delete {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 8px;
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
