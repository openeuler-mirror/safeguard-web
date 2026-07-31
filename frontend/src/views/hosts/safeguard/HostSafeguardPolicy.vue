<template>
  <div class="host-safeguard-policy">
    <div class="page-header">
      <button class="btn-back" @click="goBack">← 返回</button>
      <h2>{{ host?.hostname || '主机' }} - Safeguard 策略</h2>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="policy-content">
      <div v-if="currentPolicy" class="policy-card">
        <h3>当前策略</h3>
        <div class="policy-info">
          <div class="info-row">
            <span class="info-label">策略模板:</span>
            <span class="info-value">{{ currentPolicy.template_name || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">绑定时间:</span>
            <span class="info-value">{{ formatDate(currentPolicy.bound_at) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">状态:</span>
            <StatusBadge :type="currentPolicy.status === 'active' ? 'success' : 'warning'" :text="currentPolicy.status === 'active' ? '已激活' : '未激活'" />
          </div>
        </div>
        <div class="policy-config">
          <h4>配置详情</h4>
          <div class="config-list">
            <div class="config-item">
              <span class="config-label">启用防火墙</span>
              <StatusBadge :type="currentPolicy.config?.enable_firewall ? 'success' : 'danger'" :text="currentPolicy.config?.enable_firewall ? '是' : '否'" />
            </div>
            <div class="config-item">
              <span class="config-label">启用防病毒</span>
              <StatusBadge :type="currentPolicy.config?.enable_antivirus ? 'success' : 'danger'" :text="currentPolicy.config?.enable_antivirus ? '是' : '否'" />
            </div>
            <div class="config-item">
              <span class="config-label">启用文件监控</span>
              <StatusBadge :type="currentPolicy.config?.enable_file_monitor ? 'success' : 'danger'" :text="currentPolicy.config?.enable_file_monitor ? '是' : '否'" />
            </div>
            <div class="config-item">
              <span class="config-label">自动更新间隔</span>
              <span class="config-value">{{ currentPolicy.config?.auto_update_hours || 24 }} 小时</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-policy-card">
        <h3>暂未绑定策略</h3>
        <p>点击下方按钮绑定策略模板</p>
      </div>

      <div class="action-section">
        <button class="btn-primary" @click="openBindDialog">
          {{ currentPolicy ? '更换策略' : '绑定策略' }}
        </button>
      </div>
    </div>

    <!-- 绑定策略弹窗 -->
    <div v-if="bindDialogVisible" class="dialog-overlay" @click.self="closeBindDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ currentPolicy ? '更换策略' : '绑定策略' }}</h3>
          <button class="dialog-close" @click="closeBindDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>选择策略模板 <span class="required">*</span></label>
            <select v-model="bindForm.template_id" :class="{ 'input-error': errors.template_id }">
              <option :value="null">请选择</option>
              <option v-for="template in templates" :key="template.id" :value="template.id">{{ template.name }}</option>
            </select>
            <span v-if="errors.template_id" class="field-error">{{ errors.template_id }}</span>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeBindDialog">取消</button>
          <button class="btn-primary" @click="submitBind" :disabled="submitting">{{ submitting ? '提交中...' : '确定' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getHost } from '@/api/host'
import { getHostPolicy, bindHostPolicy } from '@/api/safeguard/policy'
import { getPolicyTemplates } from '@/api/safeguard/policy'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

export default {
  name: 'HostSafeguardPolicy',
  components: { StatusBadge },
  data() {
    return {
      hostId: null,
      host: null,
      currentPolicy: null,
      templates: [],
      loading: false,
      error: '',
      bindDialogVisible: false,
      formError: '',
      errors: {},
      submitting: false,
      bindForm: {
        template_id: null
      }
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
        const [hostRes, policyRes, templatesRes] = await Promise.allSettled([
          getHost(this.hostId),
          getHostPolicy(this.hostId),
          getPolicyTemplates()
        ])
        if (hostRes.status === 'fulfilled') {
          this.host = hostRes.value
        }
        if (policyRes.status === 'fulfilled') {
          this.currentPolicy = policyRes.value || null
        }
        if (templatesRes.status === 'fulfilled') {
          this.templates = templatesRes.value?.results || templatesRes.value || []
        }
      } catch (e) {
        this.error = e.message || '加载数据失败'
      } finally {
        this.loading = false
      }
    },
    openBindDialog() {
      this.bindForm.template_id = null
      this.formError = ''
      this.errors = {}
      this.bindDialogVisible = true
    },
    closeBindDialog() {
      this.bindDialogVisible = false
    },
    async submitBind() {
      this.formError = ''
      this.errors = {}

      if (!this.bindForm.template_id) {
        this.errors.template_id = '请选择策略模板'
        return
      }

      this.submitting = true
      try {
        await bindHostPolicy(this.hostId, { template_id: this.bindForm.template_id })
        this.closeBindDialog()
        alert('策略绑定成功')
        await this.loadData()
      } catch (e) {
        this.formError = e.message || '操作失败'
      } finally {
        this.submitting = false
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
.host-safeguard-policy {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
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
  padding: 10px 24px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-primary:disabled {
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

.policy-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.policy-card, .empty-policy-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.policy-card h3, .empty-policy-card h3 {
  margin: 0 0 16px 0;
  color: #333;
}

.empty-policy-card p {
  color: #909399;
  margin: 0;
}

.policy-info {
  margin-bottom: 24px;
}

.info-row {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-label {
  width: 120px;
  color: #909399;
}

.info-value {
  color: #333;
}

.policy-config h4 {
  margin: 0 0 12px 0;
  color: #333;
}

.config-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.config-label {
  color: #333;
}

.config-value {
  color: #666;
}

.action-section {
  display: flex;
  justify-content: center;
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

.form-item select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  background: white;
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