<template>
  <div class="outipsn-container">
    <div class="outipsn-header">
      <div class="header-actions">
        <button class="btn-primary" @click="openCreateDialog">添加记录</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="outipsn-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>MAC地址</th>
            <th>序列号</th>
            <th>描述</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in outipsnList" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.mac_address }}</td>
            <td>{{ item.sn }}</td>
            <td>{{ item.description || '-' }}</td>
            <td>{{ formatDate(item.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(item)">编辑</button>
              <button class="btn-danger" @click="confirmDelete(item)">删除</button>
            </td>
          </tr>
          <tr v-if="outipsnList.length === 0">
            <td colspan="6" class="empty-text">暂无数据</td>
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
          <h3>{{ isEdit ? '编辑记录' : '添加记录' }}</h3>
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
            <label>序列号 <span class="required">*</span></label>
            <input v-model="form.sn" type="text" placeholder="请输入序列号" :class="{ 'input-error': errors.sn }" />
            <span v-if="errors.sn" class="field-error">{{ errors.sn }}</span>
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
          <p>确定删除记录 <strong>{{ selectedItem?.mac_address }}</strong> 吗？</p>
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
import { getOutIpSNs, createOutIpSN, updateOutIpSN, deleteOutIpSN } from '@/api/osdeploy/outipsn'

export default {
  name: 'OutIpSN',
  data() {
    return {
      outipsnList: [],
      loading: false,
      error: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      dialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedItem: null,
      formError: '',
      errors: {},
      form: {
        mac_address: '',
        sn: '',
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
    this.loadOutIpSNs()
  },
  methods: {
    async loadOutIpSNs() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        const res = await getOutIpSNs(params)
        this.outipsnList = res.results || res || []
        this.totalCount = res.count || this.outipsnList.length
      } catch (e) {
        this.error = e.message || '加载记录失败'
      } finally {
        this.loading = false
      }
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadOutIpSNs()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        mac_address: '',
        sn: '',
        description: ''
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
        sn: item.sn,
        description: item.description || ''
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

      if (!this.form.sn.trim()) {
        this.errors.sn = '请输入序列号'
        return
      }

      try {
        if (this.isEdit) {
          await updateOutIpSN(this.selectedItem.id, this.form)
        } else {
          await createOutIpSN(this.form)
        }
        this.closeDialog()
        this.loadOutIpSNs()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
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
        await deleteOutIpSN(this.selectedItem.id)
        this.closeDeleteDialog()
        this.loadOutIpSNs()
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
.outipsn-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.outipsn-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.outipsn-header h2 {
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

.outipsn-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 700px;
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