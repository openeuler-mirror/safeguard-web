<template>
  <div class="auto-install-container">
    <div class="auto-install-content">
      <div class="form-card">
        <h3>装机配置</h3>
        <div v-if="formError" class="form-error-summary">{{ formError }}</div>

        <div class="form-item">
          <label>目标主机 <span class="required">*</span></label>
          <select v-model="form.host_id" :class="{ 'input-error': errors.host_id }">
            <option value="">请选择主机</option>
            <option v-for="h in hosts" :key="h.id" :value="h.id">
              {{ h.hostname }} ({{ h.ip_address }})
            </option>
          </select>
          <span v-if="errors.host_id" class="field-error">{{ errors.host_id }}</span>
        </div>

        <div class="form-item">
          <label>PXE服务器 <span class="required">*</span></label>
          <select v-model="form.pxe_server_id" :class="{ 'input-error': errors.pxe_server_id }">
            <option value="">请选择PXE服务器</option>
            <option v-for="p in pxeServers" :key="p.id" :value="p.id">
              {{ p.server_ip }} ({{ p.interface }})
            </option>
          </select>
          <span v-if="errors.pxe_server_id" class="field-error">{{ errors.pxe_server_id }}</span>
        </div>

        <div class="form-item">
          <label>Kickstart模板 <span class="required">*</span></label>
          <select v-model="form.kickstart_id" :class="{ 'input-error': errors.kickstart_id }">
            <option value="">请选择模板</option>
            <option v-for="k in kickstarts" :key="k.id" :value="k.id">
              {{ k.name }}
            </option>
          </select>
          <span v-if="errors.kickstart_id" class="field-error">{{ errors.kickstart_id }}</span>
        </div>

        <div class="form-item">
          <label>仓库 <span class="required">*</span></label>
          <select v-model="form.repo_id" :class="{ 'input-error': errors.repo_id }">
            <option value="">请选择仓库</option>
            <option v-for="r in repos" :key="r.id" :value="r.id">
              {{ r.name }} ({{ r.repo_type }})
            </option>
          </select>
          <span v-if="errors.repo_id" class="field-error">{{ errors.repo_id }}</span>
        </div>

        <div class="form-actions">
          <button class="btn-primary" @click="handleSubmit" :disabled="submitting">
            {{ submitting ? '提交中...' : '开始装机' }}
          </button>
        </div>
      </div>

      <!-- 近期任务 -->
      <div class="recent-jobs">
        <h3>近期任务</h3>
        <div v-if="loadingJobs" class="loading-small">加载中...</div>
        <div v-else-if="recentJobs.length === 0" class="empty-text">暂无任务记录</div>
        <div v-else class="job-list">
          <div v-for="job in recentJobs" :key="job.id" class="job-item">
            <div class="job-info">
              <span class="job-target">{{ job.target }}</span>
              <span :class="getStatusClass(job.status)">{{ formatStatus(job.status) }}</span>
            </div>
            <div class="job-meta">
              <span>{{ formatJobType(job.job_type) }}</span>
              <span>{{ formatDate(job.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 任务追踪弹窗 -->
    <div v-if="taskDialogVisible" class="dialog-overlay" @click.self="closeTaskDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>装机进度追踪</h3>
          <button class="dialog-close" @click="closeTaskDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="task-info">
            <p><strong>任务ID:</strong> {{ activeJobId }}</p>
            <p><strong>状态:</strong> <span :class="getStatusClass(activeJobStatus)">{{ formatStatus(activeJobStatus) }}</span></p>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar" :style="{ width: activeJobProgress + '%' }" :class="getProgressClass(activeJobStatus)"></div>
          </div>
          <p class="progress-text">{{ activeJobProgress }}%</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeTaskDialog">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getHosts } from '@/api/host'
import { getPXEServers } from '@/api/osdeploy/pxe'
import { getKickstarts } from '@/api/osdeploy/kickstart'
import { getRepos } from '@/api/osdeploy/repo'
import { getJobs } from '@/api/osdeploy/job'
import { autoInstall } from '@/api/osdeploy/auto_install'

export default {
  name: 'AutoInstall',
  data() {
    return {
      hosts: [],
      pxeServers: [],
      kickstarts: [],
      repos: [],
      recentJobs: [],
      loadingJobs: false,
      submitting: false,
      formError: '',
      errors: {},
      form: {
        host_id: '',
        pxe_server_id: '',
        kickstart_id: '',
        repo_id: ''
      },
      taskDialogVisible: false,
      activeJobId: null,
      activeJobStatus: null,
      activeJobProgress: 0,
      pollTimer: null
    }
  },
  mounted() {
    this.loadHosts()
    this.loadPXEServers()
    this.loadKickstarts()
    this.loadRepos()
    this.loadRecentJobs()
  },
  methods: {
    async loadHosts() {
      try {
        const res = await getHosts({ page_size: 100 })
        this.hosts = res.results || res || []
      } catch (e) {
        console.error('加载主机列表失败', e)
      }
    },
    async loadPXEServers() {
      try {
        const res = await getPXEServers({ page_size: 100 })
        this.pxeServers = res.results || res || []
      } catch (e) {
        console.error('加载PXE服务器列表失败', e)
      }
    },
    async loadKickstarts() {
      try {
        const res = await getKickstarts({ page_size: 100 })
        this.kickstarts = res.results || res || []
      } catch (e) {
        console.error('加载Kickstart模板列表失败', e)
      }
    },
    async loadRepos() {
      try {
        const res = await getRepos({ page_size: 100 })
        this.repos = res.results || res || []
      } catch (e) {
        console.error('加载仓库列表失败', e)
      }
    },
    async loadRecentJobs() {
      this.loadingJobs = true
      try {
        const res = await getJobs({ page_size: 5, job_type: 'osdeploy' })
        this.recentJobs = res.results || res || []
      } catch (e) {
        console.error('加载任务列表失败', e)
      } finally {
        this.loadingJobs = false
      }
    },
    async handleSubmit() {
      this.formError = ''
      this.errors = {}

      if (!this.form.host_id) {
        this.errors.host_id = '请选择目标主机'
        return
      }
      if (!this.form.pxe_server_id) {
        this.errors.pxe_server_id = '请选择PXE服务器'
        return
      }
      if (!this.form.kickstart_id) {
        this.errors.kickstart_id = '请选择Kickstart模板'
        return
      }
      if (!this.form.repo_id) {
        this.errors.repo_id = '请选择仓库'
        return
      }

      this.submitting = true
      try {
        const res = await autoInstall({
          host_id: this.form.host_id,
          kickstart_id: this.form.kickstart_id,
          repo_id: this.form.repo_id,
        })
        this.activeJobId = res.job_id
        this.activeJobStatus = 'running'
        this.activeJobProgress = 0
        this.taskDialogVisible = true
        this.startPolling()
        this.loadRecentJobs()
      } catch (e) {
        this.formError = e.message || '提交失败，请稍后重试'
      } finally {
        this.submitting = false
      }
    },
    startPolling() {
      if (this.pollTimer) clearInterval(this.pollTimer)
      this.pollTimer = setInterval(async () => {
        if (!this.activeJobId || this.activeJobStatus === 'success' || this.activeJobStatus === 'failed') {
          clearInterval(this.pollTimer)
          this.pollTimer = null
          return
        }
        try {
          const res = await getJobs({ job_id: this.activeJobId })
          const job = (res.results || res || []).find(j => j.job_id === this.activeJobId)
          if (job) {
            this.activeJobStatus = job.status
            this.activeJobProgress = job.progress
          }
        } catch (e) {
          console.error('轮询任务状态失败', e)
        }
      }, 3000)
    },
    closeTaskDialog() {
      this.taskDialogVisible = false
      if (this.pollTimer) {
        clearInterval(this.pollTimer)
        this.pollTimer = null
      }
    },
    formatStatus(status) {
      const statusMap = {
        pending: '等待中',
        running: '运行中',
        success: '成功',
        failed: '失败'
      }
      return statusMap[status] || status
    },
    formatJobType(type) {
      const typeMap = {
        osdeploy: 'OS部署',
        hardware: '硬件采集'
      }
      return typeMap[type] || type
    },
    getStatusClass(status) {
      const classMap = {
        pending: 'status-pending',
        running: 'status-running',
        success: 'status-success',
        failed: 'status-failed'
      }
      return classMap[status] || ''
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
.auto-install-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.auto-install-header {
  margin-bottom: 20px;
}

.auto-install-header h2 {
  margin: 0;
  color: #333;
}

.auto-install-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 900px) {
  .auto-install-content {
    grid-template-columns: 1fr;
  }
}

.form-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.form-card h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 16px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
}

.form-item select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
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

.form-actions {
  margin-top: 24px;
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

.btn-primary:hover {
  background: #66b1ff;
}

.btn-primary:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}

.recent-jobs {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.recent-jobs h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 16px;
}

.loading-small {
  text-align: center;
  padding: 20px;
  color: #666;
}

.empty-text {
  text-align: center;
  padding: 20px;
  color: #999;
}

.job-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.job-item {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.job-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.job-target {
  font-weight: 500;
  color: #333;
}

.job-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

.status-pending { color: #909399; }
.status-running { color: #409eff; }
.status-success { color: #67c23a; }
.status-failed { color: #f56c6c; }

.dialog-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); display: flex; align-items: center;
  justify-content: center; z-index: 1000;
}
.dialog { background: white; border-radius: 8px; width: 480px; max-width: 90%; }
.dialog-header { display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid #eee; }
.dialog-header h3 { margin: 0; color: #333; }
.dialog-close { background: none; border: none; font-size: 24px; cursor: pointer; color: #999; }
.dialog-body { padding: 20px; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 10px;
  padding: 16px 20px; border-top: 1px solid #eee; }
.task-info { margin-bottom: 16px; }
.task-info p { margin: 4px 0; }
.progress-bar-container { height: 20px; background: #ebeef5; border-radius: 10px; overflow: hidden; }
.progress-bar { height: 100%; background: #409eff; transition: width 0.3s; }
.progress-bar.success { background: #67c23a; }
.progress-bar.failed { background: #f56c6c; }
.progress-text { text-align: center; margin-top: 8px; color: #666; }
</style>