<template>
  <div class="policy-templates">
    <div class="page-header">
      <h2>策略模板管理</h2>
      <div class="header-actions">
        <input
          v-model="searchText"
          type="text"
          placeholder="搜索模板名称"
          class="search-input"
          @keyup.enter="loadTemplates"
        />
        <button class="btn-primary" @click="openCreateDialog">创建模板</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="templates-grid">
      <div v-for="template in templates" :key="template.id" class="template-card">
        <div class="card-header">
          <h3>{{ template.name }}</h3>
          <div class="card-actions">
            <button class="btn-action" @click="viewTemplate(template)" title="查看详情">👁️</button>
            <button class="btn-action" @click="openEditDialog(template)" title="编辑">✏️</button>
            <button class="btn-action" @click="cloneTemplate(template)" title="克隆">📋</button>
            <button class="btn-action" @click="openApplyDialog(template)" title="应用到主机">🚀</button>
            <button class="btn-action btn-danger" @click="confirmDelete(template)" title="删除">🗑️</button>
          </div>
        </div>
        <p class="card-description">{{ template.description || '暂无描述' }}</p>
        <div class="card-meta">
          <span><StatusBadge type="info" :text="template.is_default ? '默认模板' : '自定义模板'" /></span>
          <span class="meta-date">创建时间: {{ formatDate(template.created_at) }}</span>
        </div>
      </div>
      <div v-if="templates.length === 0" class="empty-state">
        暂无策略模板，点击上方按钮创建一个
      </div>
    </div>

    <!-- 创建/编辑弹窗 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog dialog-large">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑策略模板' : '创建策略模板' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>模板名称 <span class="required">*</span></label>
            <input v-model="form.name" type="text" :class="{ 'input-error': errors.name }" />
            <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="form.description" rows="3" />
          </div>
          <div class="form-section">
            <h4>策略配置</h4>
            <div class="config-grid">
              <div class="config-item">
                <label>
                  <input type="checkbox" v-model="form.config.enable_firewall" />
                  启用防火墙
                </label>
              </div>
              <div class="config-item">
                <label>
                  <input type="checkbox" v-model="form.config.enable_antivirus" />
                  启用防病毒
                </label>
              </div>
              <div class="config-item">
                <label>
                  <input type="checkbox" v-model="form.config.enable_file_monitor" />
                  启用文件监控
                </label>
              </div>
              <div class="config-item">
                <label>自动更新间隔 (小时)</label>
                <input type="number" v-model.number="form.config.auto_update_hours" min="1" />
              </div>
            </div>
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
          <p>确定要删除策略模板 <strong>{{ selectedTemplate?.name }}</strong> 吗？</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDeleteDialog">取消</button>
          <button class="btn-danger" @click="handleDelete" :disabled="deleting">{{ deleting ? '删除中...' : '确认删除' }}</button>
        </div>
      </div>
    </div>

    <!-- 应用策略弹窗 -->
    <div v-if="applyDialogVisible" class="dialog-overlay" @click.self="closeApplyDialog">
      <div class="dialog dialog-large">
        <div class="dialog-header">
          <h3>应用策略模板 - {{ selectedTemplate?.name }}</h3>
          <button class="dialog-close" @click="closeApplyDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-item">
            <label>选择主机 <span class="required">*</span></label>
            <div class="host-checkbox-list">
              <label v-for="host in availableHosts" :key="host.id" class="checkbox-label">
                <input type="checkbox" :value="host.id" v-model="applyForm.host_ids" />
                {{ host.hostname }} ({{ host.ip_address }})
              </label>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeApplyDialog">取消</button>
          <button class="btn-primary" @click="submitApply" :disabled="applying">{{ applying ? '应用中...' : '应用' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  getPolicyTemplates,
  createPolicyTemplate,
  updatePolicyTemplate,
  deletePolicyTemplate,
  clonePolicyTemplate,
  applyPolicy
} from '@/api/safeguard/policy'
import { getHosts } from '@/api/host'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

export default {
  name: 'PolicyTemplates',
  components: { StatusBadge },
  data() {
    return {
      templates: [],
      availableHosts: [],
      searchText: '',
      loading: false,
      error: '',
      dialogVisible: false,
      isEdit: false,
      selectedTemplate: null,
      formError: '',
      errors: {},
      submitting: false,
      form: {
        name: '',
        description: '',
        config: {
          enable_firewall: false,
          enable_antivirus: false,
          enable_file_monitor: false,
          auto_update_hours: 24
        }
      },
      deleteDialogVisible: false,
      deleting: false,
      applyDialogVisible: false,
      applying: false,
      applyForm: {
        host_ids: []
      }
    }
  },
  mounted() {
    this.loadTemplates()
    this.loadHosts()
  },
  methods: {
    async loadTemplates() {
      this.loading = true
      this.error = ''
      try {
        const params = {}
        if (this.searchText) params.search = this.searchText
        const res = await getPolicyTemplates(params)
        this.templates = res?.results || res || []
      } catch (e) {
        this.error = e.message || '加载模板列表失败'
      } finally {
        this.loading = false
      }
    },
    async loadHosts() {
      try {
        const res = await getHosts()
        this.availableHosts = res?.results || res || []
      } catch (e) {
        console.error('加载主机列表失败', e)
      }
    },
    viewTemplate(template) {
      this.$router.push(`/safeguard/policy-templates/${template.id}`)
    },
    openCreateDialog() {
      this.isEdit = false
      this.selectedTemplate = null
      this.formError = ''
      this.errors = {}
      this.form = {
        name: '',
        description: '',
        config: {
          enable_firewall: false,
          enable_antivirus: false,
          enable_file_monitor: false,
          auto_update_hours: 24
        }
      }
      this.dialogVisible = true
    },
    openEditDialog(template) {
      this.isEdit = true
      this.selectedTemplate = template
      this.formError = ''
      this.errors = {}
      this.form = {
        name: template.name,
        description: template.description || '',
        config: template.config || {
          enable_firewall: false,
          enable_antivirus: false,
          enable_file_monitor: false,
          auto_update_hours: 24
        }
      }
      this.dialogVisible = true
    },
    closeDialog() {
      this.dialogVisible = false
    },
    async submitForm() {
      this.formError = ''
      this.errors = {}

      if (!this.form.name.trim()) {
        this.errors.name = '请输入模板名称'
        return
      }

      this.submitting = true
      try {
        if (this.isEdit) {
          await updatePolicyTemplate(this.selectedTemplate.id, this.form)
        } else {
          await createPolicyTemplate(this.form)
        }
        this.closeDialog()
        await this.loadTemplates()
      } catch (e) {
        this.formError = e.message || '操作失败'
      } finally {
        this.submitting = false
      }
    },
    async cloneTemplate(template) {
      try {
        await clonePolicyTemplate(template.id)
        alert('模板克隆成功')
        await this.loadTemplates()
      } catch (e) {
        alert(e.message || '克隆失败')
      }
    },
    confirmDelete(template) {
      this.selectedTemplate = template
      this.deleteDialogVisible = true
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    async handleDelete() {
      this.deleting = true
      try {
        await deletePolicyTemplate(this.selectedTemplate.id)
        this.closeDeleteDialog()
        await this.loadTemplates()
      } catch (e) {
        alert(e.message || '删除失败')
      } finally {
        this.deleting = false
      }
    },
    openApplyDialog(template) {
      this.selectedTemplate = template
      this.applyForm.host_ids = []
      this.applyDialogVisible = true
    },
    closeApplyDialog() {
      this.applyDialogVisible = false
    },
    async submitApply() {
      if (this.applyForm.host_ids.length === 0) {
        alert('请至少选择一个主机')
        return
      }
      this.applying = true
      try {
        await applyPolicy(this.selectedTemplate.id, this.applyForm.host_ids)
        alert('策略下发任务已创建')
        this.closeApplyDialog()
        this.$router.push('/safeguard/policy-tasks')
      } catch (e) {
        alert(e.message || '应用失败')
      } finally {
        this.applying = false
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString()
    }
  }
}
</script>

<style scoped>
.policy-templates {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 240px;
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

.loading, .error {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 16px;
}

.error {
  color: #f56c6c;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.template-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.card-header h3 {
  margin: 0;
  color: #333;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  padding: 4px 8px;
  background: transparent;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-action:hover {
  background: #f5f5f5;
}

.btn-action.btn-danger:hover {
  background: #fef0f0;
}

.card-description {
  color: #909399;
  margin-bottom: 12px;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.meta-date {
  color: #909399;
  font-size: 13px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  color: #909399;
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
  max-height: 90vh;
  overflow: hidden;
}

.dialog-large {
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
  overflow-y: auto;
  max-height: 60vh;
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

.form-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.form-section h4 {
  margin: 0 0 16px 0;
  color: #333;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.config-item label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: normal;
}

.config-item input[type="number"] {
  width: 100px;
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

.host-checkbox-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  cursor: pointer;
}
</style>