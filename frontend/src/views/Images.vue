<template>
  <div class="images-container">
    <div class="images-header">
      <h2>镜像管理</h2>
      <div class="header-actions">
        <select v-model="filterHost" class="filter-select" @change="handleFilter">
          <option value="">全部宿主机</option>
          <option v-for="h in hostList" :key="h.id" :value="h.id">{{ h.hostname }} ({{ h.ip_address }})</option>
        </select>
        <input
          v-model="searchName"
          type="text"
          placeholder="搜索镜像名称"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="btn-primary" @click="openCreateDialog">添加镜像</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="images-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>镜像名称</th>
            <th>操作系统类型</th>
            <th>镜像路径</th>
            <th>宿主机</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="img in images" :key="img.id">
            <td>{{ img.id }}</td>
            <td>{{ img.name }}</td>
            <td>{{ getOsTypeText(img.ostype) }}</td>
            <td class="path-text">{{ img.path }}</td>
            <td>{{ img.host_name || '-' }}</td>
            <td>{{ formatDate(img.created_at) }}</td>
            <td>
              <button class="btn-action btn-refresh" @click="handleRefresh(img)" title="刷新">刷新</button>
              <button class="btn-edit" @click="openEditDialog(img)">编辑</button>
              <button class="btn-delete" @click="confirmDelete(img)">删除</button>
            </td>
          </tr>
          <tr v-if="images.length === 0">
            <td colspan="7" class="empty-text">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建/编辑弹窗 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑镜像' : '添加镜像' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>镜像ID <span class="required">*</span></label>
            <input v-model="form.id" type="text" placeholder="请输入镜像ID" :class="{ 'input-error': errors.id }" :disabled="isEdit" />
            <span v-if="errors.id" class="field-error">{{ errors.id }}</span>
          </div>
          <div class="form-item">
            <label>镜像名称 <span class="required">*</span></label>
            <input v-model="form.name" type="text" placeholder="请输入镜像名称" :class="{ 'input-error': errors.name }" />
            <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
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
            <label>操作系统类型</label>
            <select v-model="form.ostype">
              <option value="">未知</option>
              <option value="centos">CentOS</option>
              <option value="culinux">CULinux</option>
              <option value="openeuler">OpenEuler</option>
              <option value="ubuntu">Ubuntu</option>
              <option value="debian">Debian</option>
            </select>
          </div>
          <div class="form-item">
            <label>镜像路径 <span class="required">*</span></label>
            <input v-model="form.path" type="text" placeholder="如: /var/lib/libvirt/images/xxx.qcow2" :class="{ 'input-error': errors.path }" />
            <span v-if="errors.path" class="field-error">{{ errors.path }}</span>
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
          <p>确定删除镜像 <strong>{{ selectedImage?.name }}</strong> 吗？</p>
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
import { getImages, createImage, updateImage, deleteImage, refreshImages, getHosts } from '@/api/host'

export default {
  name: 'Images',
  data() {
    return {
      images: [],
      hostList: [],
      loading: false,
      error: '',
      searchName: '',
      filterHost: '',
      dialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedImage: null,
      formError: '',
      errors: {},
      form: {
        id: '',
        name: '',
        host: null,
        ostype: '',
        path: ''
      }
    }
  },
  mounted() {
    this.loadImages()
    this.loadHostList()
  },
  methods: {
    async loadImages() {
      this.loading = true
      this.error = ''
      try {
        const params = {}
        if (this.searchName) params.search = this.searchName
        if (this.filterHost) params.host = this.filterHost
        const res = await getImages(params)
        this.images = res.results || res || []
      } catch (e) {
        this.error = e.message || '加载镜像列表失败'
      } finally {
        this.loading = false
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
      this.loadImages()
    },
    handleFilter() {
      this.loadImages()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        id: '',
        name: '',
        host: null,
        ostype: '',
        path: ''
      }
      this.dialogVisible = true
    },
    openEditDialog(img) {
      this.isEdit = true
      this.selectedImage = img
      this.formError = ''
      this.errors = {}
      this.form = {
        id: img.id,
        name: img.name,
        host: img.host,
        ostype: img.ostype || '',
        path: img.path
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

      if (!this.form.id.trim()) {
        this.errors.id = '请输入镜像ID'
        return
      }
      if (!this.form.name.trim()) {
        this.errors.name = '请输入镜像名称'
        return
      }
      if (!this.form.host) {
        this.errors.host = '请选择宿主机'
        return
      }
      if (!this.form.path.trim()) {
        this.errors.path = '请输入镜像路径'
        return
      }

      try {
        const data = { ...this.form }
        if (this.isEdit) {
          await updateImage(this.selectedImage.id, data)
        } else {
          await createImage(data)
        }
        this.closeDialog()
        this.loadImages()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
        this.errors = {}
      }
    },
    confirmDelete(img) {
      this.selectedImage = img
      this.deleteDialogVisible = true
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    async handleDelete() {
      try {
        await deleteImage(this.selectedImage.id)
        this.closeDeleteDialog()
        this.loadImages()
      } catch (e) {
        alert(e.message || '删除失败')
      }
    },
    async handleRefresh(img) {
      try {
        await refreshImages(img.id)
        this.loadImages()
      } catch (e) {
        alert(e.message || '刷新失败')
      }
    },
    getOsTypeText(ostype) {
      const typeMap = {
        'centos': 'CentOS',
        'culinux': 'CULinux',
        'openeuler': 'OpenEuler',
        'ubuntu': 'Ubuntu',
        'debian': 'Debian',
        'unknown': '未知'
      }
      return typeMap[ostype] || ostype || '未知'
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
.images-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.images-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.images-header h2 {
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
  width: 160px;
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

.images-table {
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

.path-text {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: monospace;
  font-size: 12px;
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

.btn-refresh {
  background: #409eff;
  color: white;
}

.btn-refresh:hover {
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