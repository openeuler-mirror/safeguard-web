<template>
  <div class="migrations-container">
    <div class="migrations-header">
      <h2>系统迁移</h2>
      <div class="header-actions">
        <select v-model="filterType" class="filter-select" @change="handleFilter">
          <option value="">全部类型</option>
          <option value="init">初始化</option>
          <option value="migrate">迁移</option>
          <option value="back">回滚</option>
        </select>
        <select v-model="filterStatus" class="filter-select" @change="handleFilter">
          <option value="">全部状态</option>
          <option value="pending">等待中</option>
          <option value="running">运行中</option>
          <option value="success">成功</option>
          <option value="failed">失败</option>
        </select>
        <input v-model="searchTarget" type="text" placeholder="搜索目标主机" class="search-input" @keyup.enter="handleSearch" />
        <button class="btn-primary" @click="openInitDialog">迁移初始化</button>
        <button class="btn-primary" @click="openMigrateDialog">执行迁移</button>
        <button class="btn-warning" @click="openBackDialog">迁移回滚</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="migrations-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>任务ID</th>
            <th>任务类型</th>
            <th>迁移类型</th>
            <th>目标主机</th>
            <th>状态</th>
            <th>进度</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.id">
            <td>{{ job.id }}</td>
            <td>{{ job.job_id }}</td>
            <td>{{ formatJobType(job.job_type) }}</td>
            <td>{{ job.migrate_type || '-' }}</td>
            <td>{{ job.target_host }}</td>
            <td>
              <span :class="getStatusClass(job.status)">{{ formatStatus(job.status) }}</span>
            </td>
            <td>
              <div class="progress-bar-small">
                <div class="progress-fill" :style="{ width: job.progress + '%' }" :class="getProgressClass(job.status)"></div>
              </div>
              <span class="progress-text">{{ job.progress }}%</span>
            </td>
            <td>{{ formatDate(job.created_at) }}</td>
            <td>
              <button class="btn-view" @click="openDetailDialog(job)">详情</button>
            </td>
          </tr>
          <tr v-if="jobs.length === 0">
            <td colspan="9" class="empty-text">暂无数据</td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button :disabled="page <= 1" @click="handlePageChange(page - 1)">上一页</button>
        <span class="page-info">第 {{ page }} / {{ totalPages }} 页</span>
        <button :disabled="page >= totalPages" @click="handlePageChange(page + 1)">下一页</button>
      </div>
    </div>

    <!-- 初始化弹窗 -->
    <div v-if="initDialogVisible" class="dialog-overlay" @click.self="closeInitDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>迁移初始化</h3>
          <button class="dialog-close" @click="closeInitDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>主机IP <span class="required">*</span></label>
            <input v-model="initForm.host" type="text" placeholder="例如: 192.168.1.100" />
          </div>
          <div class="form-group">
            <label>端口</label>
            <input v-model="initForm.port" type="text" placeholder="22" />
          </div>
          <div class="form-group">
            <label>用户名 <span class="required">*</span></label>
            <input v-model="initForm.username" type="text" placeholder="root" />
          </div>
          <div class="form-group">
            <label>密码 <span class="required">*</span></label>
            <input v-model="initForm.password" type="password" placeholder="请输入密码" />
          </div>
          <div class="form-group">
            <label>主机列表 (JSON数组)</label>
            <textarea v-model="initForm.hosts" rows="3" placeholder='["host1", "host2"]'></textarea>
          </div>
          <div class="form-group">
            <label>迁移类型</label>
            <select v-model="initForm.type">
              <option value="">请选择</option>
              <option value="centos_to_culinux">CentOS 迁移到 CUlinux</option>
              <option value="openeuler_to_culinux">openEuler 迁移到 CUlinux</option>
            </select>
          </div>
          <div class="form-group">
            <label>Redis密码</label>
            <input v-model="initForm.redispasswd" type="password" placeholder="可选" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeInitDialog">取消</button>
          <button class="btn-primary" :disabled="submitting" @click="submitInit">确定</button>
        </div>
      </div>
    </div>

    <!-- 迁移弹窗 -->
    <div v-if="migrateDialogVisible" class="dialog-overlay" @click.self="closeMigrateDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>执行迁移</h3>
          <button class="dialog-close" @click="closeMigrateDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>任务名称</label>
            <input v-model="migrateForm.jobname" type="text" placeholder="可选" />
          </div>
          <div class="form-group">
            <label>主机IP <span class="required">*</span></label>
            <input v-model="migrateForm.host" type="text" placeholder="例如: 192.168.1.100" />
          </div>
          <div class="form-group">
            <label>端口</label>
            <input v-model="migrateForm.port" type="text" placeholder="22" />
          </div>
          <div class="form-group">
            <label>用户名 <span class="required">*</span></label>
            <input v-model="migrateForm.username" type="text" placeholder="root" />
          </div>
          <div class="form-group">
            <label>密码 <span class="required">*</span></label>
            <input v-model="migrateForm.password" type="password" placeholder="请输入密码" />
          </div>
          <div class="form-group">
            <label>主机列表 (JSON数组)</label>
            <textarea v-model="migrateForm.hosts" rows="3" placeholder='["host1", "host2"]'></textarea>
          </div>
          <div class="form-group">
            <label>迁移类型</label>
            <select v-model="migrateForm.type">
              <option value="">请选择</option>
              <option value="centos_to_culinux">CentOS 迁移到 CUlinux</option>
              <option value="openeuler_to_culinux">openEuler 迁移到 CUlinux</option>
            </select>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeMigrateDialog">取消</button>
          <button class="btn-primary" :disabled="submitting" @click="submitMigrate">确定</button>
        </div>
      </div>
    </div>

    <!-- 回滚弹窗 -->
    <div v-if="backDialogVisible" class="dialog-overlay" @click.self="closeBackDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>迁移回滚</h3>
          <button class="dialog-close" @click="closeBackDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>任务名称</label>
            <input v-model="backForm.jobname" type="text" placeholder="可选" />
          </div>
          <div class="form-group">
            <label>主机IP <span class="required">*</span></label>
            <input v-model="backForm.host" type="text" placeholder="例如: 192.168.1.100" />
          </div>
          <div class="form-group">
            <label>端口</label>
            <input v-model="backForm.port" type="text" placeholder="22" />
          </div>
          <div class="form-group">
            <label>用户名 <span class="required">*</span></label>
            <input v-model="backForm.username" type="text" placeholder="root" />
          </div>
          <div class="form-group">
            <label>密码 <span class="required">*</span></label>
            <input v-model="backForm.password" type="password" placeholder="请输入密码" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeBackDialog">取消</button>
          <button class="btn-warning" :disabled="submitting" @click="submitBack">确定</button>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="detailDialogVisible" class="dialog-overlay" @click.self="closeDetailDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>迁移任务详情</h3>
          <button class="dialog-close" @click="closeDetailDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="selectedJob">
            <p><strong>任务ID:</strong> {{ selectedJob.job_id }}</p>
            <p><strong>任务类型:</strong> {{ formatJobType(selectedJob.job_type) }}</p>
            <p><strong>迁移类型:</strong> {{ selectedJob.migrate_type || '-' }}</p>
            <p><strong>目标主机:</strong> {{ selectedJob.target_host }}</p>
            <p><strong>状态:</strong> <span :class="getStatusClass(selectedJob.status)">{{ formatStatus(selectedJob.status) }}</span></p>
            <p><strong>进度:</strong> {{ selectedJob.progress }}%</p>
            <p v-if="selectedJob.error_message"><strong>错误信息:</strong> <span class="error-text">{{ selectedJob.error_message }}</span></p>
            <p v-if="selectedJob.result"><strong>结果:</strong> <pre class="result-pre">{{ JSON.stringify(selectedJob.result, null, 2) }}</pre></p>
            <p><strong>创建时间:</strong> {{ formatDate(selectedJob.created_at) }}</p>
            <p><strong>更新时间:</strong> {{ formatDate(selectedJob.updated_at) }}</p>
            <div v-if="statusDetail" class="status-detail">
              <h4>实时状态</h4>
              <pre class="result-pre">{{ JSON.stringify(statusDetail, null, 2) }}</pre>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-primary" :disabled="statusLoading" @click="fetchStatus">刷新状态</button>
          <button class="btn-cancel" @click="closeDetailDialog">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getMigrates, createMigrateInit, createMigrate, createMigrateBack, getMigrateStatus } from '@/api/migrate'

export default {
  name: 'Migrations',
  data() {
    return {
      jobs: [],
      loading: false,
      error: '',
      searchTarget: '',
      filterType: '',
      filterStatus: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      submitting: false,
      initDialogVisible: false,
      migrateDialogVisible: false,
      backDialogVisible: false,
      detailDialogVisible: false,
      selectedJob: null,
      statusDetail: null,
      statusLoading: false,
      initForm: { host: '', port: '22', username: '', password: '', hosts: '', type: '', redispasswd: '' },
      migrateForm: { jobname: '', host: '', port: '22', username: '', password: '', hosts: '', type: '' },
      backForm: { jobname: '', host: '', port: '22', username: '', password: '' },
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize) || 1
    }
  },
  mounted() {
    this.loadJobs()
  },
  methods: {
    async loadJobs() {
      this.loading = true
      this.error = ''
      try {
        const params = { page: this.page, page_size: this.pageSize }
        if (this.searchTarget) params.search = this.searchTarget
        if (this.filterType) params.job_type = this.filterType
        if (this.filterStatus) params.status = this.filterStatus
        const res = await getMigrates(params)
        this.jobs = res.results || res || []
        this.totalCount = res.count || this.jobs.length
      } catch (e) {
        this.error = e.message || '加载迁移任务列表失败'
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.page = 1
      this.loadJobs()
    },
    handleFilter() {
      this.page = 1
      this.loadJobs()
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadJobs()
    },
    openInitDialog() {
      this.initForm = { host: '', port: '22', username: '', password: '', hosts: '', type: '', redispasswd: '' }
      this.initDialogVisible = true
    },
    closeInitDialog() {
      this.initDialogVisible = false
    },
    async submitInit() {
      if (!this.initForm.host || !this.initForm.username || !this.initForm.password) {
        alert('请填写必填项')
        return
      }
      this.submitting = true
      try {
        const data = { ...this.initForm }
        if (data.hosts) {
          try { data.hosts = JSON.parse(data.hosts) } catch { data.hosts = [data.hosts] }
        }
        if (data.type) data.type = [data.type]
        await createMigrateInit(data)
        this.closeInitDialog()
        this.loadJobs()
      } catch (e) {
        alert(e.message || '创建初始化任务失败')
      } finally {
        this.submitting = false
      }
    },
    openMigrateDialog() {
      this.migrateForm = { jobname: '', host: '', port: '22', username: '', password: '', hosts: '', type: '' }
      this.migrateDialogVisible = true
    },
    closeMigrateDialog() {
      this.migrateDialogVisible = false
    },
    async submitMigrate() {
      if (!this.migrateForm.host || !this.migrateForm.username || !this.migrateForm.password) {
        alert('请填写必填项')
        return
      }
      this.submitting = true
      try {
        const data = { ...this.migrateForm }
        if (data.hosts) {
          try { data.hosts = JSON.parse(data.hosts) } catch { data.hosts = [data.hosts] }
        }
        if (data.type) data.type = [data.type]
        await createMigrate(data)
        this.closeMigrateDialog()
        this.loadJobs()
      } catch (e) {
        alert(e.message || '创建迁移任务失败')
      } finally {
        this.submitting = false
      }
    },
    openBackDialog() {
      this.backForm = { jobname: '', host: '', port: '22', username: '', password: '' }
      this.backDialogVisible = true
    },
    closeBackDialog() {
      this.backDialogVisible = false
    },
    async submitBack() {
      if (!this.backForm.host || !this.backForm.username || !this.backForm.password) {
        alert('请填写必填项')
        return
      }
      this.submitting = true
      try {
        await createMigrateBack({ ...this.backForm })
        this.closeBackDialog()
        this.loadJobs()
      } catch (e) {
        alert(e.message || '创建回滚任务失败')
      } finally {
        this.submitting = false
      }
    },
    openDetailDialog(job) {
      this.selectedJob = job
      this.statusDetail = null
      this.detailDialogVisible = true
    },
    closeDetailDialog() {
      this.detailDialogVisible = false
      this.selectedJob = null
      this.statusDetail = null
    },
    async fetchStatus() {
      if (!this.selectedJob) return
      this.statusLoading = true
      try {
        const res = await getMigrateStatus(this.selectedJob.id)
        this.statusDetail = res.data || res
      } catch (e) {
        alert(e.message || '获取状态失败')
      } finally {
        this.statusLoading = false
      }
    },
    formatJobType(type) {
      const map = { init: '初始化', migrate: '迁移', back: '回滚' }
      return map[type] || type
    },
    formatStatus(status) {
      const map = { pending: '等待中', running: '运行中', success: '成功', failed: '失败' }
      return map[status] || status
    },
    getStatusClass(status) {
      const map = { pending: 'status-pending', running: 'status-running', success: 'status-success', failed: 'status-failed' }
      return map[status] || ''
    },
    getProgressClass(status) {
      const map = { pending: 'progress-pending', running: 'progress-running', success: 'progress-success', failed: 'progress-failed' }
      return map[status] || ''
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString()
    }
  }
}
</script>

<style scoped>
.migrations-container { padding: 20px; max-width: 1400px; margin: 0 auto; min-height: calc(100vh - 100px); }
.migrations-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
.migrations-header h2 { margin: 0; color: #333; }
.header-actions { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.filter-select, .search-input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; }
.search-input { width: 180px; }
.btn-primary { padding: 8px 16px; background: #409eff; color: white; border: none; border-radius: 4px; cursor: pointer; }
.btn-primary:hover { background: #66b1ff; }
.btn-primary:disabled { background: #a0cfff; cursor: not-allowed; }
.btn-warning { padding: 8px 16px; background: #e6a23c; color: white; border: none; border-radius: 4px; cursor: pointer; }
.btn-warning:hover { background: #ebb563; }
.btn-warning:disabled { background: #f3d19e; cursor: not-allowed; }
.loading, .error { text-align: center; padding: 40px; }
.error { color: #f56c6c; }
.migrations-table { background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); overflow-x: auto; }
table { width: 100%; border-collapse: collapse; min-width: 1000px; }
th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; }
th { background: #f5f5f5; font-weight: 600; }
.empty-text { text-align: center; color: #999; }
.progress-bar-small { width: 100px; height: 8px; background: #ebeef5; border-radius: 4px; overflow: hidden; display: inline-block; vertical-align: middle; }
.progress-fill { height: 100%; transition: width 0.3s; }
.progress-text { font-size: 12px; color: #666; margin-left: 6px; }
.progress-pending { background: #909399; }
.progress-running { background: #409eff; }
.progress-success { background: #67c23a; }
.progress-failed { background: #f56c6c; }
.status-pending { color: #909399; }
.status-running { color: #409eff; }
.status-success { color: #67c23a; }
.status-failed { color: #f56c6c; }
.btn-view { padding: 6px 12px; background: #409eff; color: white; border: none; border-radius: 4px; cursor: pointer; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 12px; padding: 16px; border-top: 1px solid #eee; }
.pagination button { padding: 6px 16px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; }
.pagination button:disabled { color: #ccc; cursor: not-allowed; }
.dialog-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: white; border-radius: 8px; width: 500px; max-width: 90%; max-height: 90vh; overflow-y: auto; }
.dialog-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #eee; }
.dialog-header h3 { margin: 0; }
.dialog-close { background: none; border: none; font-size: 24px; cursor: pointer; color: #999; }
.dialog-body { padding: 20px; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 20px; border-top: 1px solid #eee; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 500; color: #333; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
.form-group textarea { resize: vertical; }
.required { color: #f56c6c; }
.btn-cancel { padding: 8px 16px; background: #fff; color: #333; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; }
.error-text { color: #f56c6c; }
.result-pre { background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px; overflow-x: auto; white-space: pre-wrap; word-break: break-all; }
.status-detail { margin-top: 16px; padding-top: 16px; border-top: 1px solid #eee; }
.status-detail h4 { margin: 0 0 8px 0; color: #333; }
</style>
