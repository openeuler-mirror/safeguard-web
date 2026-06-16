<template>
  <div class="members-container">
    <div class="members-header">
      <div class="header-actions">
        <select v-model="filterPool" class="filter-select" @change="handleFilter">
          <option value="">全部后端池</option>
          <option v-for="pool in pools" :key="pool.id" :value="pool.id">{{ pool.name }}</option>
        </select>
        <select v-model="filterEnabled" class="filter-select" @change="handleFilter">
          <option value="">全部状态</option>
          <option value="true">已启用</option>
          <option value="false">已禁用</option>
        </select>
        <button class="btn-primary" @click="openCreateDialog">添加成员</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="members-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>后端池</th>
            <th>地址</th>
            <th>端口</th>
            <th>权重</th>
            <th>状态</th>
            <th>描述</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="member in members" :key="member.id">
            <td>{{ member.id }}</td>
            <td>{{ member.pool_name }}</td>
            <td>{{ member.address }}</td>
            <td>{{ member.port }}</td>
            <td>{{ member.weight }}</td>
            <td>
              <span :class="member.is_enabled ? 'status-enabled' : 'status-disabled'">
                {{ member.is_enabled ? '已启用' : '已禁用' }}
              </span>
            </td>
            <td>{{ member.description || '-' }}</td>
            <td>{{ formatDate(member.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(member)">编辑</button>
              <button class="btn-danger" @click="confirmDelete(member)">删除</button>
            </td>
          </tr>
          <tr v-if="members.length === 0">
            <td colspan="9" class="empty-text">暂无数据</td>
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
          <h3>{{ isEdit ? '编辑成员' : '添加成员' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>后端池 <span class="required">*</span></label>
            <select v-model="form.pool" :class="{ 'input-error': errors.pool }" :disabled="isEdit">
              <option value="">请选择后端池</option>
              <option v-for="pool in pools" :key="pool.id" :value="pool.id">{{ pool.name }}</option>
            </select>
            <span v-if="errors.pool" class="field-error">{{ errors.pool }}</span>
          </div>
          <div class="form-item">
            <label>地址 <span class="required">*</span></label>
            <input v-model="form.address" type="text" placeholder="如: 192.168.1.100" :class="{ 'input-error': errors.address }" />
            <span v-if="errors.address" class="field-error">{{ errors.address }}</span>
          </div>
          <div class="form-item">
            <label>端口 <span class="required">*</span></label>
            <input v-model.number="form.port" type="number" placeholder="如: 8080" min="1" max="65535" :class="{ 'input-error': errors.port }" />
            <span v-if="errors.port" class="field-error">{{ errors.port }}</span>
          </div>
          <div class="form-item">
            <label>权重</label>
            <input v-model.number="form.weight" type="number" placeholder="默认1" min="1" max="100" />
          </div>
          <div class="form-item">
            <label>
              <input v-model="form.is_enabled" type="checkbox" />
              启用此成员
            </label>
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
          <p>确定删除成员 <strong>{{ selectedMember?.address }}</strong> 吗？</p>
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
import { getMembers, createMember, updateMember, deleteMember, getPools } from '@/api/network'

export default {
  name: 'Members',
  data() {
    return {
      members: [],
      pools: [],
      loading: false,
      error: '',
      filterPool: '',
      filterEnabled: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      dialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedMember: null,
      formError: '',
      errors: {},
      form: {
        pool: '',
        address: '',
        port: 80,
        weight: 1,
        is_enabled: true,
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
    this.loadPools()
    this.loadMembers()
  },
  methods: {
    async loadPools() {
      try {
        const res = await getPools({ page_size: 100 })
        this.pools = res.results || res || []
      } catch (e) {
        console.error('加载后端池失败:', e)
      }
    },
    async loadMembers() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        if (this.filterPool) params.pool = this.filterPool
        if (this.filterEnabled !== '') params.is_enabled = this.filterEnabled === 'true'
        const res = await getMembers(params)
        this.members = res.results || res || []
        this.totalCount = res.count || this.members.length
      } catch (e) {
        this.error = e.message || '加载池成员列表失败'
      } finally {
        this.loading = false
      }
    },
    handleFilter() {
      this.page = 1
      this.loadMembers()
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadMembers()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        pool: this.filterPool || '',
        address: '',
        port: 80,
        weight: 1,
        is_enabled: true,
        description: ''
      }
      this.dialogVisible = true
    },
    openEditDialog(member) {
      this.isEdit = true
      this.selectedMember = member
      this.formError = ''
      this.errors = {}
      this.form = {
        pool: member.pool,
        address: member.address,
        port: member.port,
        weight: member.weight,
        is_enabled: member.is_enabled,
        description: member.description || ''
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

      if (!this.form.pool) {
        this.errors.pool = '请选择后端池'
        return
      }
      if (!this.form.address.trim()) {
        this.errors.address = '请输入地址'
        return
      }
      if (!this.form.port || this.form.port < 1 || this.form.port > 65535) {
        this.errors.port = '请输入有效端口(1-65535)'
        return
      }

      try {
        if (this.isEdit) {
          await updateMember(this.selectedMember.id, this.form)
        } else {
          await createMember(this.form)
        }
        this.closeDialog()
        this.loadMembers()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
      }
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    confirmDelete(member) {
      this.selectedMember = member
      this.deleteDialogVisible = true
    },
    async handleDelete() {
      try {
        await deleteMember(this.selectedMember.id)
        this.closeDeleteDialog()
        this.loadMembers()
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
.members-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.members-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.members-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 140px;
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

.members-table {
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

.status-enabled {
  color: #67c23a;
}

.status-disabled {
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
.form-item select,
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
</style>