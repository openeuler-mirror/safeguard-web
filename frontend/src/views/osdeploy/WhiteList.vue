<template>
  <div class="whitelist-container">
    <div class="whitelist-header">
      <h2>MAC地址白名单</h2>
      <div class="header-actions">
        <button class="btn-import" @click="openImportDialog">批量导入</button>
        <button class="btn-primary" @click="openCreateDialog">添加白名单</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="whitelist-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>MAC地址</th>
            <th>主机名</th>
            <th>IP地址</th>
            <th>状态</th>
            <th>描述</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in whitelist" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.mac_address }}</td>
            <td>{{ item.hostname || '-' }}</td>
            <td>{{ item.ip_address || '-' }}</td>
            <td>
              <span :class="item.is_active ? 'status-active' : 'status-inactive'">
                {{ item.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td>{{ item.description || '-' }}</td>
            <td>{{ formatDate(item.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(item)">编辑</button>
              <button class="btn-danger" @click="confirmDelete(item)">删除</button>
            </td>
          </tr>
          <tr v-if="whitelist.length === 0">
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
          <h3>{{ isEdit ? '编辑白名单' : '添加白名单' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>MAC地址 <span class="required">*</span></label>
            <input v-model="form.mac_address" type="text" placeholder="如: 00:11:22:33:44:55" :class="{ 'input-error': errors.mac_address }" />
            <span v-if="errors.mac_address" class="field-error">{{ errors.mac_address }}</span>
          </div>
          <div class="form-item">
            <label>主机名</label>
            <input v-model="form.hostname" type="text" placeholder="请输入主机名" />
          </div>
          <div class="form-item">
            <label>IP地址</label>
            <input v-model="form.ip_address" type="text" placeholder="如: 192.168.1.100" />
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="form.description" placeholder="请输入描述信息" rows="3"></textarea>
          </div>
          <div class="form-item">
            <label>
              <input v-model="form.is_active" type="checkbox" />
              启用
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="submitForm">确定</button>
        </div>
      </div>
    </div>

    <!-- 导入弹窗 -->
    <div v-if="importDialogVisible" class="dialog-overlay" @click.self="closeImportDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>批量导入</h3>
          <button class="dialog-close" @click="closeImportDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-item">
            <label>选择文件</label>
            <input type="file" ref="fileInput" accept=".xlsx,.xls,.csv" @change="handleFileChange" />
            <span class="help-text">支持 .xlsx, .xls, .csv 格式</span>
          </div>
          <div v-if="uploadProgress" class="upload-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
            </div>
            <span>{{ uploadProgress }}%</span>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeImportDialog">取消</button>
          <button class="btn-primary" @click="handleImport" :disabled="!selectedFile || uploading">
            {{ uploading ? '导入中...' : '开始导入' }}
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
          <p>确定删除白名单 <strong>{{ selectedItem?.mac_address }}</strong> 吗？</p>
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
import { getWhiteList, createWhiteList, updateWhiteList, deleteWhiteList, importWhiteList } from '@/api/osdeploy/whitelist'

export default {
  name: 'WhiteList',
  data() {
    return {
      whitelist: [],
      loading: false,
      error: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      dialogVisible: false,
      importDialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedItem: null,
      selectedFile: null,
      uploading: false,
      uploadProgress: 0,
      formError: '',
      errors: {},
      form: {
        mac_address: '',
        hostname: '',
        ip_address: '',
        description: '',
        is_active: true
      }
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize) || 1
    }
  },
  mounted() {
    this.loadWhiteList()
  },
  methods: {
    async loadWhiteList() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        const res = await getWhiteList(params)
        this.whitelist = res.results || res || []
        this.totalCount = res.count || this.whitelist.length
      } catch (e) {
        this.error = e.message || '加载白名单失败'
      } finally {
        this.loading = false
      }
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadWhiteList()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        mac_address: '',
        hostname: '',
        ip_address: '',
        description: '',
        is_active: true
      }
      this.dialogVisible = true
    },
    openEditDialog(item) {
      this.isEdit = true
      this.selectedItem = item
      this.formError = ''
      this.errors = {}
      this.form = {
        mac_address: item.mac_address,
        hostname: item.hostname || '',
        ip_address: item.ip_address || '',
        description: item.description || '',
        is_active: item.is_active
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

      if (!this.form.mac_address.trim()) {
        this.errors.mac_address = '请输入MAC地址'
        return
      }

      // 简单MAC格式校验
      const macRegex = /^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$/
      if (!macRegex.test(this.form.mac_address)) {
        this.errors.mac_address = 'MAC地址格式不正确，应为如: 00:11:22:33:44:55'
        return
      }

      try {
        if (this.isEdit) {
          await updateWhiteList(this.selectedItem.id, this.form)
        } else {
          await createWhiteList(this.form)
        }
        this.closeDialog()
        this.loadWhiteList()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
      }
    },
    openImportDialog() {
      this.selectedFile = null
      this.uploadProgress = 0
      this.importDialogVisible = true
    },
    closeImportDialog() {
      this.importDialogVisible = false
      this.selectedFile = null
      this.uploadProgress = 0
    },
    handleFileChange(e) {
      const file = e.target.files[0]
      if (file) {
        this.selectedFile = file
      }
    },
    async handleImport() {
      if (!this.selectedFile) return

      this.uploading = true
      this.uploadProgress = 0
      try {
        // 模拟进度
        this.uploadProgress = 50
        await importWhiteList(this.selectedFile)
        this.uploadProgress = 100
        this.closeImportDialog()
        this.loadWhiteList()
        alert('导入成功')
      } catch (e) {
        alert(e.message || '导入失败')
      } finally {
        this.uploading = false
      }
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    confirmDelete(item) {
      this.selectedItem = item
      this.deleteDialogVisible = true
    },
    async handleDelete() {
      try {
        await deleteWhiteList(this.selectedItem.id)
        this.closeDeleteDialog()
        this.loadWhiteList()
      } catch (e) {
        alert(e.message || '删除失败')
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
.whitelist-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.whitelist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.whitelist-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-primary, .btn-import {
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

.btn-import {
  background: #67c23a;
  color: white;
}

.btn-import:hover {
  background: #85ce61;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #f56c6c;
}

.whitelist-table {
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

.form-item input[type="text"],
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