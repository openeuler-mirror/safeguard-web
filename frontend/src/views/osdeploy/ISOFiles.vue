<template>
  <div class="iso-files-container">
    <div class="iso-files-header">
      <h2>ISO 文件管理</h2>
      <div class="header-actions">
        <button class="btn-upload" @click="openUploadDialog">上传ISO文件</button>
        <button class="btn-primary" @click="openCreateDialog">添加记录</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="iso-files-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>文件名</th>
            <th>文件大小</th>
            <th>MD5</th>
            <th>状态</th>
            <th>描述</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="iso in isoFiles" :key="iso.id">
            <td>{{ iso.id }}</td>
            <td>{{ iso.filename }}</td>
            <td>{{ formatSize(iso.size) }}</td>
            <td class="md5-cell" :title="iso.md5sum">{{ iso.md5sum || '-' }}</td>
            <td>
              <span :class="getStatusClass(iso.status)">
                {{ formatStatus(iso.status) }}
              </span>
            </td>
            <td>{{ iso.description || '-' }}</td>
            <td>{{ formatDate(iso.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(iso)">编辑</button>
              <button class="btn-danger" @click="confirmDelete(iso)">删除</button>
            </td>
          </tr>
          <tr v-if="isoFiles.length === 0">
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
          <h3>{{ isEdit ? '编辑ISO文件' : '添加ISO文件记录' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>文件名 <span class="required">*</span></label>
            <input v-model="form.filename" type="text" placeholder="如: CentOS-7-x86_64-Everything.iso" :class="{ 'input-error': errors.filename }" />
            <span v-if="errors.filename" class="field-error">{{ errors.filename }}</span>
          </div>
          <div class="form-item">
            <label>文件大小 (字节) <span class="required">*</span></label>
            <input v-model.number="form.size" type="number" placeholder="如: 4294967296" :class="{ 'input-error': errors.size }" />
            <span v-if="errors.size" class="field-error">{{ errors.size }}</span>
          </div>
          <div class="form-item">
            <label>MD5校验码</label>
            <input v-model="form.md5sum" type="text" placeholder="32位MD5校验码" />
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

    <!-- 上传弹窗 -->
    <div v-if="uploadDialogVisible" class="dialog-overlay" @click.self="closeUploadDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>上传ISO文件</h3>
          <button class="dialog-close" @click="closeUploadDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-item">
            <label>选择ISO文件</label>
            <input type="file" ref="fileInput" accept=".iso" @change="handleFileChange" />
            <span class="help-text">请选择 .iso 格式的文件</span>
          </div>
          <div v-if="uploadProgress > 0" class="upload-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
            </div>
            <span>{{ uploadProgress }}%</span>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeUploadDialog">取消</button>
          <button class="btn-primary" @click="handleUpload" :disabled="!selectedFile || uploading">
            {{ uploading ? '上传中...' : '开始上传' }}
          </button>
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
          <p>确定删除 ISO 文件 <strong>{{ selectedItem?.filename }}</strong> 吗？</p>
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
import { getISOFiles, createISOFile, updateISOFile, deleteISOFile, uploadISOFile } from '@/api/osdeploy/iso'

export default {
  name: 'ISOFiles',
  data() {
    return {
      isoFiles: [],
      loading: false,
      error: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      dialogVisible: false,
      uploadDialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedItem: null,
      selectedFile: null,
      uploading: false,
      uploadProgress: 0,
      formError: '',
      errors: {},
      form: {
        filename: '',
        size: '',
        md5sum: '',
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
    this.loadISOFiles()
  },
  methods: {
    async loadISOFiles() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        const res = await getISOFiles(params)
        this.isoFiles = res.results || res || []
        this.totalCount = res.count || this.isoFiles.length
      } catch (e) {
        this.error = e.message || '加载ISO文件列表失败'
      } finally {
        this.loading = false
      }
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadISOFiles()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        filename: '',
        size: '',
        md5sum: '',
        description: ''
      }
      this.dialogVisible = true
    },
    openEditDialog(iso) {
      this.isEdit = true
      this.selectedItem = iso
      this.formError = ''
      this.errors = {}
      this.form = {
        filename: iso.filename,
        size: iso.size,
        md5sum: iso.md5sum || '',
        description: iso.description || ''
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

      if (!this.form.filename.trim()) {
        this.errors.filename = '请输入文件名'
        return
      }
      if (!this.form.size) {
        this.errors.size = '请输入文件大小'
        return
      }

      try {
        if (this.isEdit) {
          await updateISOFile(this.selectedItem.id, this.form)
        } else {
          await createISOFile(this.form)
        }
        this.closeDialog()
        this.loadISOFiles()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
      }
    },
    openUploadDialog() {
      this.selectedFile = null
      this.uploadProgress = 0
      this.uploadDialogVisible = true
    },
    closeUploadDialog() {
      this.uploadDialogVisible = false
      this.selectedFile = null
      this.uploadProgress = 0
    },
    handleFileChange(e) {
      const file = e.target.files[0]
      if (file) {
        this.selectedFile = file
      }
    },
    async handleUpload() {
      if (!this.selectedFile) return

      this.uploading = true
      this.uploadProgress = 0
      try {
        this.uploadProgress = 50
        await uploadISOFile(this.selectedFile)
        this.uploadProgress = 100
        this.closeUploadDialog()
        this.loadISOFiles()
        alert('上传成功')
      } catch (e) {
        alert(e.message || '上传失败')
      } finally {
        this.uploading = false
      }
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    confirmDelete(iso) {
      this.selectedItem = iso
      this.deleteDialogVisible = true
    },
    async handleDelete() {
      try {
        await deleteISOFile(this.selectedItem.id)
        this.closeDeleteDialog()
        this.loadISOFiles()
      } catch (e) {
        alert(e.message || '删除失败')
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString()
    },
    formatSize(bytes) {
      if (!bytes) return '-'
      const units = ['B', 'KB', 'MB', 'GB', 'TB']
      let i = 0
      let size = parseFloat(bytes)
      while (size >= 1024 && i < units.length - 1) {
        size /= 1024
        i++
      }
      return size.toFixed(2) + ' ' + units[i]
    },
    formatStatus(status) {
      const statusMap = {
        available: '可用',
        uploading: '上传中',
        processing: '处理中',
        unavailable: '不可用'
      }
      return statusMap[status] || status
    },
    getStatusClass(status) {
      const classMap = {
        available: 'status-available',
        uploading: 'status-uploading',
        processing: 'status-processing',
        unavailable: 'status-unavailable'
      }
      return classMap[status] || ''
    }
  }
}
</script>

<style scoped>
.iso-files-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.iso-files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.iso-files-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-primary, .btn-upload {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-upload {
  background: #e6a23c;
  color: white;
}

.btn-upload:hover {
  background: #ebb563;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #f56c6c;
}

.iso-files-table {
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

.md5-cell {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: monospace;
  font-size: 12px;
}

.status-available { color: #67c23a; }
.status-uploading { color: #e6a23c; }
.status-processing { color: #409eff; }
.status-unavailable { color: #f56c6c; }

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
.form-item textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-item input[type="file"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.help-text {
  display: block;
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
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

.upload-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e4e4e4;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #409eff;
  transition: width 0.3s;
}
</style>