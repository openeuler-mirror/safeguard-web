<template>
  <div class="file-monitor-rules">
    <div class="page-header">
      <button class="btn-back" @click="goBack">← 返回</button>
      <h2>{{ host?.hostname || '主机' }} - 文件监控规则</h2>
      <button class="btn-primary" @click="openCreateDialog">创建规则</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="rules-table">
      <table>
        <thead>
          <tr>
            <th>路径</th>
            <th>监控类型</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rule in rules" :key="rule.id">
            <td>{{ rule.path }}</td>
            <td>{{ rule.monitor_types?.join(', ') || '-' }}</td>
            <td>
              <StatusBadge :type="rule.enabled ? 'success' : 'info'" :text="rule.enabled ? '已启用' : '已禁用'" />
            </td>
            <td>{{ formatDate(rule.created_at) }}</td>
            <td>
              <button class="btn-action" @click="openEditDialog(rule)">编辑</button>
              <button class="btn-action" @click="toggleEnabled(rule)">{{ rule.enabled ? '禁用' : '启用' }}</button>
              <button class="btn-action btn-danger" @click="confirmDelete(rule)">删除</button>
            </td>
          </tr>
          <tr v-if="rules.length === 0">
            <td colspan="5" class="empty-text">暂无规则</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建/编辑弹窗 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑规则' : '创建规则' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>监控路径 <span class="required">*</span></label>
            <input v-model="form.path" type="text" placeholder="/path/to/monitor" :class="{ 'input-error': errors.path }" />
            <span v-if="errors.path" class="field-error">{{ errors.path }}</span>
          </div>
          <div class="form-item">
            <label>监控类型 <span class="required">*</span></label>
            <div class="checkbox-group">
              <label v-for="type in monitorTypes" :key="type" class="checkbox-label">
                <input type="checkbox" :value="type" v-model="form.monitor_types" />
                {{ type }}
              </label>
            </div>
          </div>
          <div class="form-item">
            <label>
              <input type="checkbox" v-model="form.enabled" />
              启用规则
            </label>
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="form.description" rows="2" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="submitForm" :disabled="submitting">{{ submitting ? '提交中...' : '确定' }}</button>
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
          <p>确定要删除规则 <strong>{{ selectedRule?.path }}</strong> 吗？</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDeleteDialog">取消</button>
          <button class="btn-danger" @click="handleDelete" :disabled="deleting">{{ deleting ? '删除中...' : '确认删除' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getHost } from '@/api/host'
import {
  getFileMonitorRules,
  createFileMonitorRule,
  updateFileMonitorRule,
  deleteFileMonitorRule
} from '@/api/safeguard/file-monitor'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

export default {
  name: 'FileMonitorRules',
  components: { StatusBadge },
  data() {
    return {
      hostId: null,
      host: null,
      rules: [],
      monitorTypes: ['read', 'write', 'create', 'delete', 'modify'],
      loading: false,
      error: '',
      dialogVisible: false,
      isEdit: false,
      selectedRule: null,
      formError: '',
      errors: {},
      submitting: false,
      form: {
        path: '',
        monitor_types: [],
        enabled: true,
        description: ''
      },
      deleteDialogVisible: false,
      deleting: false
    }
  },
  mounted() {
    this.hostId = this.$route.params.id
    if (this.hostId) {
      this.loadData()
    }
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = ''
      try {
        const hostRes = await getHost(this.hostId)
        this.host = hostRes
        await this.loadRules()
      } catch (e) {
        this.error = e.message || '加载数据失败'
      } finally {
        this.loading = false
      }
    },
    async loadRules() {
      try {
        const res = await getFileMonitorRules({ host_id: this.hostId })
        this.rules = res?.results || res || []
      } catch (e) {
        this.error = e.message || '获取规则失败'
      }
    },
    openCreateDialog() {
      this.isEdit = false
      this.selectedRule = null
      this.formError = ''
      this.errors = {}
      this.form = {
        path: '',
        monitor_types: [],
        enabled: true,
        description: ''
      }
      this.dialogVisible = true
    },
    openEditDialog(rule) {
      this.isEdit = true
      this.selectedRule = rule
      this.formError = ''
      this.errors = {}
      this.form = {
        path: rule.path,
        monitor_types: rule.monitor_types || [],
        enabled: rule.enabled !== false,
        description: rule.description || ''
      }
      this.dialogVisible = true
    },
    closeDialog() {
      this.dialogVisible = false
    },
    async submitForm() {
      this.formError = ''
      this.errors = {}

      if (!this.form.path.trim()) {
        this.errors.path = '请输入监控路径'
        return
      }
      if (!this.form.monitor_types || this.form.monitor_types.length === 0) {
        alert('请至少选择一种监控类型')
        return
      }

      this.submitting = true
      try {
        const data = { ...this.form, host_id: this.hostId }
        if (this.isEdit) {
          await updateFileMonitorRule(this.selectedRule.id, data)
        } else {
          await createFileMonitorRule(data)
        }
        this.closeDialog()
        await this.loadRules()
      } catch (e) {
        this.formError = e.message || '操作失败'
      } finally {
        this.submitting = false
      }
    },
    async toggleEnabled(rule) {
      try {
        await updateFileMonitorRule(rule.id, { ...rule, enabled: !rule.enabled })
        await this.loadRules()
      } catch (e) {
        alert(e.message || '操作失败')
      }
    },
    confirmDelete(rule) {
      this.selectedRule = rule
      this.deleteDialogVisible = true
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    async handleDelete() {
      this.deleting = true
      try {
        await deleteFileMonitorRule(this.selectedRule.id)
        this.closeDeleteDialog()
        await this.loadRules()
      } catch (e) {
        alert(e.message || '删除失败')
      } finally {
        this.deleting = false
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString()
    },
    goBack() {
      this.$router.push(`/hosts/${this.hostId}/dashboard`)
    }
  }
}
</script>

<style scoped>
.file-monitor-rules {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.btn-back {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.btn-back:hover {
  background: #eee;
}

.btn-primary {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-danger {
  padding: 8px 16px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-danger:hover:not(:disabled) {
  background: #f78989;
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.btn-action {
  padding: 6px 12px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  margin-right: 6px;
}

.btn-action:hover {
  background: #66b1ff;
}

.btn-action.btn-danger {
  background: #f56c6c;
}

.btn-action.btn-danger:hover {
  background: #f78989;
}

.loading, .error {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 16px;
}

.error {
  color: #f56c6c;
}

.rules-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
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

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-weight: normal;
}

.form-error-summary {
  background: #fef0f0;
  border: 1px solid #fde2e2;
  color: #f56c6c;
  padding: 10px 12px;
  border-radius: 4px;
  margin-bottom: 16px;
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
</style>
