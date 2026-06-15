<template>
  <div class="repos-container">
    <div class="repos-header">
      <div class="header-actions">
        <select v-model="filterRepoType" class="filter-select" @change="handleFilter">
          <option value="">全部类型</option>
          <option value="yum">YUM</option>
          <option value="iso">ISO</option>
          <option value="http">HTTP</option>
        </select>
        <select v-model="filterDefault" class="filter-select" @change="handleFilter">
          <option value="">全部</option>
          <option value="true">默认仓库</option>
        </select>
        <input
          v-model="searchName"
          type="text"
          placeholder="搜索仓库名称"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="btn-primary" @click="openCreateDialog">创建仓库</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="repos-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>仓库名称</th>
            <th>类型</th>
            <th>仓库地址</th>
            <th>默认</th>
            <th>描述</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="repo in repos" :key="repo.id">
            <td>{{ repo.id }}</td>
            <td>{{ repo.name }}</td>
            <td>
              <span :class="getRepoTypeClass(repo.repo_type)">
                {{ formatRepoType(repo.repo_type) }}
              </span>
            </td>
            <td class="url-cell" :title="repo.base_url">{{ repo.base_url }}</td>
            <td>
              <span v-if="repo.is_default" class="tag-default">默认</span>
              <span v-else>-</span>
            </td>
            <td>{{ repo.description || '-' }}</td>
            <td>{{ formatDate(repo.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(repo)">编辑</button>
              <button class="btn-sync" @click="handleSync(repo)">同步</button>
              <button v-if="repo.status === 'inactive'" class="btn-enable" @click="handleEnable(repo)">启用</button>
              <button v-else class="btn-disable" @click="handleDisable(repo)">禁用</button>
              <button class="btn-check" @click="handleCheck(repo)">检查</button>
              <button class="btn-danger" @click="confirmDelete(repo)">删除</button>
            </td>
          </tr>
          <tr v-if="repos.length === 0">
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
          <h3>{{ isEdit ? '编辑仓库' : '创建仓库' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>仓库名称 <span class="required">*</span></label>
            <input v-model="form.name" type="text" placeholder="请输入仓库名称" :class="{ 'input-error': errors.name }" />
            <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
          </div>
          <div class="form-item">
            <label>仓库类型 <span class="required">*</span></label>
            <select v-model="form.repo_type" :class="{ 'input-error': errors.repo_type }">
              <option value="yum">YUM</option>
              <option value="iso">ISO</option>
              <option value="http">HTTP</option>
            </select>
            <span v-if="errors.repo_type" class="field-error">{{ errors.repo_type }}</span>
          </div>
          <div class="form-item">
            <label>仓库地址 <span class="required">*</span></label>
            <input v-model="form.base_url" type="text" placeholder="如: http://mirror.example.com/centos" :class="{ 'input-error': errors.base_url }" />
            <span v-if="errors.base_url" class="field-error">{{ errors.base_url }}</span>
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="form.description" placeholder="请输入描述信息" rows="3"></textarea>
          </div>
          <div class="form-item">
            <label>
              <input v-model="form.is_default" type="checkbox" />
              设为默认仓库
            </label>
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
          <p>确定删除仓库 <strong>{{ selectedRepo?.name }}</strong> 吗？</p>
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
import { getRepos, createRepo, updateRepo, deleteRepo, syncRepo, enableRepo, disableRepo, checkRepo } from '@/api/osdeploy/repo'

export default {
  name: 'Repos',
  data() {
    return {
      repos: [],
      loading: false,
      error: '',
      searchName: '',
      filterRepoType: '',
      filterDefault: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      dialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedRepo: null,
      formError: '',
      errors: {},
      form: {
        name: '',
        repo_type: 'yum',
        base_url: '',
        description: '',
        is_default: false
      }
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize) || 1
    }
  },
  mounted() {
    this.loadRepos()
  },
  methods: {
    async loadRepos() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        if (this.searchName) params.search = this.searchName
        if (this.filterRepoType) params.repo_type = this.filterRepoType
        if (this.filterDefault === 'true') params.is_default = true
        const res = await getRepos(params)
        this.repos = res.results || res || []
        this.totalCount = res.count || this.repos.length
      } catch (e) {
        this.error = e.message || '加载仓库列表失败'
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.page = 1
      this.loadRepos()
    },
    handleFilter() {
      this.page = 1
      this.loadRepos()
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadRepos()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        name: '',
        repo_type: 'yum',
        base_url: '',
        description: '',
        is_default: false
      }
      this.dialogVisible = true
    },
    openEditDialog(repo) {
      this.isEdit = true
      this.selectedRepo = repo
      this.formError = ''
      this.errors = {}
      this.form = {
        name: repo.name,
        repo_type: repo.repo_type,
        base_url: repo.base_url,
        description: repo.description || '',
        is_default: repo.is_default
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
        this.errors.name = '请输入仓库名称'
        return
      }
      if (!this.form.base_url.trim()) {
        this.errors.base_url = '请输入仓库地址'
        return
      }

      try {
        if (this.isEdit) {
          await updateRepo(this.selectedRepo.id, this.form)
        } else {
          await createRepo(this.form)
        }
        this.closeDialog()
        this.loadRepos()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
      }
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    confirmDelete(repo) {
      this.selectedRepo = repo
      this.deleteDialogVisible = true
    },
    async handleDelete() {
      try {
        await deleteRepo(this.selectedRepo.id)
        this.closeDeleteDialog()
        this.loadRepos()
      } catch (e) {
        alert(e.message || '删除失败')
      }
    },
    async handleSync(repo) {
      try {
        await syncRepo(repo.id)
        alert('同步成功')
        this.loadRepos()
      } catch (e) {
        alert(e.message || '同步失败')
      }
    },
    async handleEnable(repo) {
      try {
        await enableRepo(repo.id)
        alert('启用成功')
        this.loadRepos()
      } catch (e) {
        alert(e.message || '启用失败')
      }
    },
    async handleDisable(repo) {
      try {
        await disableRepo(repo.id)
        alert('禁用成功')
        this.loadRepos()
      } catch (e) {
        alert(e.message || '禁用失败')
      }
    },
    async handleCheck(repo) {
      try {
        const res = await checkRepo(repo.id)
        alert(res.available ? '仓库可访问' : `仓库不可访问: ${res.message}`)
      } catch (e) {
        alert(e.message || '检查失败')
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString()
    },
    formatRepoType(type) {
      const typeMap = {
        yum: 'YUM',
        iso: 'ISO',
        http: 'HTTP'
      }
      return typeMap[type] || type
    },
    getRepoTypeClass(type) {
      const classMap = {
        yum: 'type-yum',
        iso: 'type-iso',
        http: 'type-http'
      }
      return classMap[type] || ''
    }
  }
}
</script>

<style scoped>
.repos-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.repos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.repos-header h2 {
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
  width: 140px;
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

.repos-table {
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

.url-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-default {
  background: #67c23a;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.type-yum { color: #409eff; }
.type-iso { color: #f56c6c; }
.type-http { color: #909399; }

.btn-edit, .btn-sync, .btn-enable, .btn-disable, .btn-check, .btn-danger {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 6px;
}

.btn-edit { background: #67c23a; color: white; }
.btn-edit:hover { background: #85ce61; }
.btn-sync { background: #e6a23c; color: white; }
.btn-sync:hover { background: #ebb563; }
.btn-enable { background: #409eff; color: white; }
.btn-enable:hover { background: #66b1ff; }
.btn-disable { background: #909399; color: white; }
.btn-disable:hover { background: #a6a9ad; }
.btn-check { background: #13c2c2; color: white; }
.btn-check:hover { background: #36cfc9; }
.btn-danger { background: #f56c6c; color: white; }
.btn-danger:hover { background: #f78989; }

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

.btn-danger {
  padding: 8px 16px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>