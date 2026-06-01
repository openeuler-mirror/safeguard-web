<template>
  <div class="kickstarts-container">
    <div class="kickstarts-header">
      <h2>Kickstart 模板管理</h2>
      <div class="header-actions">
        <select v-model="filterRepo" class="filter-select" @change="handleFilter">
          <option value="">全部仓库</option>
          <option v-for="r in repos" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
        <input
          v-model="searchName"
          type="text"
          placeholder="搜索模板名称"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="btn-primary" @click="openCreateDialog">创建模板</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="kickstarts-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>模板名称</th>
            <th>仓库</th>
            <th>内核参数</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ks in kickstarts" :key="ks.id">
            <td>{{ ks.id }}</td>
            <td>{{ ks.name }}</td>
            <td>{{ ks.repo_name || '-' }}</td>
            <td>{{ formatKernelOptions(ks.kernel_options) }}</td>
            <td>{{ formatDate(ks.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(ks)">编辑</button>
              <button class="btn-preview" @click="openPreviewDialog(ks)">预览</button>
              <button class="btn-validate" @click="handleValidate(ks)">验证</button>
              <button class="btn-generate" @click="openGenerateDialog(ks)">生成</button>
              <button class="btn-danger" @click="confirmDelete(ks)">删除</button>
            </td>
          </tr>
          <tr v-if="kickstarts.length === 0">
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
      <div class="dialog dialog-wide">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑模板' : '创建模板' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>模板名称 <span class="required">*</span></label>
            <input v-model="form.name" type="text" placeholder="请输入模板名称" :class="{ 'input-error': errors.name }" />
            <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
          </div>
          <div class="form-item">
            <label>关联仓库</label>
            <select v-model="form.repo">
              <option :value="null">无</option>
              <option v-for="r in repos" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>
          <div class="form-item">
            <label>模板内容 <span class="required">*</span></label>
            <textarea v-model="form.content" placeholder="请输入 Kickstart 模板内容" rows="15" class="code-textarea" :class="{ 'input-error': errors.content }"></textarea>
            <span v-if="errors.content" class="field-error">{{ errors.content }}</span>
          </div>
          <div class="form-item">
            <label>内核参数 (JSON)</label>
            <input v-model="form.kernel_options_json" type="text" placeholder='{"ksdevice": "eth0", "inst.stage2": "..."}' />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="submitForm">确定</button>
        </div>
      </div>
    </div>

    <!-- 预览弹窗 -->
    <div v-if="previewDialogVisible" class="dialog-overlay" @click.self="closePreviewDialog">
      <div class="dialog dialog-wide">
        <div class="dialog-header">
          <h3>预览 - {{ selectedKickstart?.name }}</h3>
          <button class="dialog-close" @click="closePreviewDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="preview-actions">
            <button class="btn-primary" @click="openVarsDialog">变量替换预览</button>
          </div>
          <pre class="code-preview">{{ selectedKickstart?.content }}</pre>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closePreviewDialog">关闭</button>
        </div>
      </div>
    </div>

    <!-- 变量替换弹窗 -->
    <div v-if="varsDialogVisible" class="dialog-overlay" @click.self="closeVarsDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>变量替换预览</h3>
          <button class="dialog-close" @click="closeVarsDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-item">
            <label>变量 (JSON格式)</label>
            <textarea v-model="varsJson" placeholder='{"hostname": "test", "ip": "192.168.1.1"}' rows="6"></textarea>
            <span class="help-text">使用 {"key": "value"} 格式，如 {"hostname": "server1"}</span>
          </div>
          <div v-if="previewContent" class="preview-result">
            <label>预览结果</label>
            <pre class="code-preview">{{ previewContent }}</pre>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeVarsDialog">取消</button>
          <button class="btn-primary" @click="doPreview">预览</button>
        </div>
      </div>
    </div>

    <!-- 生成Kickstart弹窗 -->
    <div v-if="generateDialogVisible" class="dialog-overlay" @click.self="closeGenerateDialog">
      <div class="dialog dialog-wide">
        <div class="dialog-header">
          <h3>生成 Kickstart - {{ selectedKickstart?.name }}</h3>
          <button class="dialog-close" @click="closeGenerateDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-item">
            <label>变量 (JSON格式)</label>
            <textarea v-model="generateVarsJson" placeholder='{"hostname": "server1", "ip_address": "192.168.1.10"}' rows="6"></textarea>
          </div>
          <div v-if="generateContent" class="preview-result">
            <label>生成结果</label>
            <pre class="code-preview">{{ generateContent }}</pre>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeGenerateDialog">关闭</button>
          <button class="btn-primary" @click="doGenerate">生成</button>
        </div>
      </div>
    </div>

    <!-- 自动全量生成弹窗 -->
    <div v-if="autoGenerateDialogVisible" class="dialog-overlay" @click.self="closeAutoGenerateDialog">
      <div class="dialog dialog-wide">
        <div class="dialog-header">
          <h3>自动全量生成 Kickstart</h3>
          <button class="dialog-close" @click="closeAutoGenerateDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-item">
            <label>目标主机</label>
            <select v-model="autoGenHostId">
              <option value="">请选择主机</option>
              <option v-for="h in hosts" :key="h.id" :value="h.id">{{ h.hostname }} ({{ h.ip_address }})</option>
            </select>
          </div>
          <div class="form-item">
            <label>仓库</label>
            <select v-model="autoGenRepoId">
              <option value="">请选择仓库</option>
              <option v-for="r in repos" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>
          <div class="form-item">
            <label>操作系统类型</label>
            <select v-model="autoGenOsType">
              <option value="culinux">CuLinux</option>
              <option value="centos7">CentOS 7</option>
              <option value="openeuler">openEuler</option>
            </select>
          </div>
          <div v-if="generateContent" class="preview-result">
            <label>生成结果</label>
            <pre class="code-preview">{{ generateContent }}</pre>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeAutoGenerateDialog">关闭</button>
          <button class="btn-primary" @click="doAutoGenerate">生成</button>
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
          <p>确定删除模板 <strong>{{ selectedKickstart?.name }}</strong> 吗？</p>
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
import { getKickstarts, createKickstart, updateKickstart, deleteKickstart, validateKickstart, previewKickstart, generateKickstart, autoGenerateKickstart } from '@/api/osdeploy/kickstart'
import { getRepos } from '@/api/osdeploy/repo'
import { getHosts } from '@/api/host'

export default {
  name: 'Kickstarts',
  data() {
    return {
      kickstarts: [],
      repos: [],
      loading: false,
      error: '',
      searchName: '',
      filterRepo: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      dialogVisible: false,
      previewDialogVisible: false,
      varsDialogVisible: false,
      generateDialogVisible: false,
      autoGenerateDialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedKickstart: null,
      formError: '',
      errors: {},
      varsJson: '{}',
      previewContent: '',
      generateVarsJson: '{}',
      generateContent: '',
      autoGenHostId: '',
      autoGenRepoId: '',
      autoGenOsType: 'culinux',
      hosts: [],
      form: {
        name: '',
        repo: null,
        content: '',
        kernel_options_json: ''
      }
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize) || 1
    }
  },
  mounted() {
    this.loadKickstarts()
    this.loadRepos()
  },
  methods: {
    async loadKickstarts() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        if (this.searchName) params.search = this.searchName
        if (this.filterRepo) params.repo = this.filterRepo
        const res = await getKickstarts(params)
        this.kickstarts = res.results || res || []
        this.totalCount = res.count || this.kickstarts.length
        // 填充仓库名称
        this.kickstarts.forEach(ks => {
          const repo = this.repos.find(r => r.id === ks.repo)
          ks.repo_name = repo ? repo.name : null
        })
      } catch (e) {
        this.error = e.message || '加载模板列表失败'
      } finally {
        this.loading = false
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
    handleSearch() {
      this.page = 1
      this.loadKickstarts()
    },
    handleFilter() {
      this.page = 1
      this.loadKickstarts()
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadKickstarts()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        name: '',
        repo: null,
        content: '',
        kernel_options_json: ''
      }
      this.dialogVisible = true
    },
    openEditDialog(ks) {
      this.isEdit = true
      this.selectedKickstart = ks
      this.formError = ''
      this.errors = {}
      this.form = {
        name: ks.name,
        repo: ks.repo,
        content: ks.content,
        kernel_options_json: ks.kernel_options ? JSON.stringify(ks.kernel_options) : ''
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

      if (!this.form.name.trim()) {
        this.errors.name = '请输入模板名称'
        return
      }
      if (!this.form.content.trim()) {
        this.errors.content = '请输入模板内容'
        return
      }

      try {
        const data = { ...this.form }
        if (!data.repo) data.repo = null
        // 解析内核参数
        if (data.kernel_options_json) {
          try {
            data.kernel_options = JSON.parse(data.kernel_options_json)
          } catch (e) {
            data.kernel_options = {}
          }
        } else {
          data.kernel_options = {}
        }
        delete data.kernel_options_json

        if (this.isEdit) {
          await updateKickstart(this.selectedKickstart.id, data)
        } else {
          await createKickstart(data)
        }
        this.closeDialog()
        this.loadKickstarts()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
      }
    },
    openPreviewDialog(ks) {
      this.selectedKickstart = ks
      this.previewContent = ''
      this.varsJson = '{}'
      this.previewDialogVisible = true
    },
    closePreviewDialog() {
      this.previewDialogVisible = false
      this.selectedKickstart = null
    },
    openVarsDialog() {
      this.varsDialogVisible = true
    },
    closeVarsDialog() {
      this.varsDialogVisible = false
      this.varsJson = '{}'
      this.previewContent = ''
    },
    async doPreview() {
      try {
        const vars = JSON.parse(this.varsJson || '{}')
        const res = await previewKickstart(this.selectedKickstart.id, vars)
        this.previewContent = res.content || ''
      } catch (e) {
        alert(e.message || '预览失败')
      }
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    confirmDelete(ks) {
      this.selectedKickstart = ks
      this.deleteDialogVisible = true
    },
    async handleDelete() {
      try {
        await deleteKickstart(this.selectedKickstart.id)
        this.closeDeleteDialog()
        this.loadKickstarts()
      } catch (e) {
        alert(e.message || '删除失败')
      }
    },
    async handleValidate(ks) {
      try {
        await validateKickstart(ks.id)
        alert('验证通过')
      } catch (e) {
        alert(e.message || '验证失败')
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString()
    },
    formatKernelOptions(options) {
      if (!options || Object.keys(options).length === 0) return '-'
      return JSON.stringify(options)
    }
  }
}
</script>

<style scoped>
.kickstarts-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.kickstarts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.kickstarts-header h2 {
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
  width: 180px;
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

.kickstarts-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
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

.btn-edit, .btn-preview, .btn-validate, .btn-danger {
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

.btn-preview {
  background: #909399;
  color: white;
}

.btn-preview:hover {
  background: #a6a9ad;
}

.btn-validate {
  background: #e6a23c;
  color: white;
}

.btn-validate:hover {
  background: #ebb563;
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

.dialog-wide {
  width: 800px;
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
.form-item select,
.form-item textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-family: inherit;
}

.form-item textarea {
  resize: vertical;
}

.code-textarea {
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.code-preview {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  max-height: 400px;
  overflow-y: auto;
}

.preview-actions {
  margin-bottom: 12px;
}

.preview-result {
  margin-top: 16px;
}

.preview-result label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-weight: 500;
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
</style>