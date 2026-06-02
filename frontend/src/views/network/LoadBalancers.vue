<template>
  <div class="lbs-container">
    <div class="lbs-header">
      <h2>负载均衡器</h2>
      <div class="header-actions">
        <input
          v-model="searchName"
          type="text"
          placeholder="搜索名称"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <select v-model="filterStatus" class="filter-select" @change="handleFilter">
          <option value="">全部状态</option>
          <option value="active">活跃</option>
          <option value="inactive">未激活</option>
        </select>
        <button class="btn-primary" @click="openCreateDialog">创建负载均衡器</button>
        <button class="btn-info" @click="toggleExtension"
          >{{ showExtension ? '收起扩展' : '扩展视图' }}</button
        >
      </div>
    </div>

    <!-- 扩展视图 -->
    <div v-if="showExtension" class="extension-panel">
      <div class="extension-row">
        <div class="extension-item">
          <label>项目ID</label>
          <input v-model="extProjectId" type="text" placeholder="输入项目ID" />
          <button class="btn-primary btn-small" @click="handleByProject">按项目查询</button>
        </div>
        <div class="extension-item">
          <label>K8s集群</label>
          <input v-model="extK8sCluster" type="text" placeholder="输入K8s集群名" />
          <button class="btn-primary btn-small" @click="handleByK8s">按K8s查询</button>
        </div>
        <div class="extension-item">
          <label>可用区</label>
          <button class="btn-primary btn-small" @click="handleLoadAzNames">加载AZ列表</button>
          <div v-if="azNames.length" class="az-tags">
            <span v-for="az in azNames" :key="az" class="az-tag">{{ az }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="lbs-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>VIP地址</th>
            <th>端口</th>
            <th>算法</th>
            <th>状态</th>
            <th>描述</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lb in lbs" :key="lb.id">
            <td>{{ lb.id }}</td>
            <td>{{ lb.name }}</td>
            <td>{{ lb.vip_address }}</td>
            <td>{{ lb.port }}</td>
            <td>{{ formatAlgorithm(lb.algorithm) }}</td>
            <td>
              <span :class="getStatusClass(lb.status)">{{ formatStatus(lb.status) }}</span>
            </td>
            <td>{{ lb.description || '-' }}</td>
            <td>{{ formatDate(lb.created_at) }}</td>
            <td>
              <button class="btn-edit" @click="openEditDialog(lb)">编辑</button>
              <button class="btn-danger" @click="confirmDelete(lb)">删除</button>
            </td>
          </tr>
          <tr v-if="lbs.length === 0">
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
          <h3>{{ isEdit ? '编辑负载均衡器' : '创建负载均衡器' }}</h3>
          <button class="dialog-close" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="formError" class="form-error-summary">{{ formError }}</div>
          <div class="form-item">
            <label>名称 <span class="required">*</span></label>
            <input v-model="form.name" type="text" placeholder="请输入名称" :class="{ 'input-error': errors.name }" />
            <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
          </div>
          <div class="form-item">
            <label>VIP地址 <span class="required">*</span></label>
            <input v-model="form.vip_address" type="text" placeholder="如: 192.168.1.100" :class="{ 'input-error': errors.vip_address }" />
            <span v-if="errors.vip_address" class="field-error">{{ errors.vip_address }}</span>
          </div>
          <div class="form-item">
            <label>端口 <span class="required">*</span></label>
            <input v-model.number="form.port" type="number" placeholder="如: 80" min="1" max="65535" :class="{ 'input-error': errors.port }" />
            <span v-if="errors.port" class="field-error">{{ errors.port }}</span>
          </div>
          <div class="form-item">
            <label>负载算法</label>
            <select v-model="form.algorithm">
              <option value="round_robin">轮询</option>
              <option value="least_conn">最少连接</option>
              <option value="source">源IP</option>
            </select>
          </div>
          <div class="form-item">
            <label>状态</label>
            <select v-model="form.status">
              <option value="active">活跃</option>
              <option value="inactive">未激活</option>
            </select>
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
          <p>确定删除负载均衡器 <strong>{{ selectedLB?.name }}</strong> 吗？</p>
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
import { getLBs, createLB, updateLB, deleteLB, getLBsByProject, getLBsByK8s, getLBAzNames } from '@/api/network'

export default {
  name: 'LoadBalancers',
  data() {
    return {
      lbs: [],
      loading: false,
      error: '',
      searchName: '',
      filterStatus: '',
      page: 1,
      pageSize: 20,
      totalCount: 0,
      dialogVisible: false,
      deleteDialogVisible: false,
      isEdit: false,
      selectedLB: null,
      formError: '',
      errors: {},
      form: {
        name: '',
        vip_address: '',
        port: 80,
        algorithm: 'round_robin',
        status: 'active',
        description: ''
      },
      showExtension: false,
      extProjectId: '',
      extK8sCluster: '',
      azNames: []
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize) || 1
    }
  },
  mounted() {
    this.loadLBs()
  },
  methods: {
    async loadLBs() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        if (this.searchName) params.search = this.searchName
        if (this.filterStatus) params.status = this.filterStatus
        const res = await getLBs(params)
        this.lbs = res.results || res || []
        this.totalCount = res.count || this.lbs.length
      } catch (e) {
        this.error = e.message || '加载负载均衡器列表失败'
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.page = 1
      this.loadLBs()
    },
    handleFilter() {
      this.page = 1
      this.loadLBs()
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.loadLBs()
    },
    openCreateDialog() {
      this.isEdit = false
      this.formError = ''
      this.errors = {}
      this.form = {
        name: '',
        vip_address: '',
        port: 80,
        algorithm: 'round_robin',
        status: 'active',
        description: ''
      }
      this.dialogVisible = true
    },
    openEditDialog(lb) {
      this.isEdit = true
      this.selectedLB = lb
      this.formError = ''
      this.errors = {}
      this.form = {
        name: lb.name,
        vip_address: lb.vip_address,
        port: lb.port,
        algorithm: lb.algorithm,
        status: lb.status,
        description: lb.description || ''
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
        this.errors.name = '请输入名称'
        return
      }
      if (!this.form.vip_address.trim()) {
        this.errors.vip_address = '请输入VIP地址'
        return
      }
      if (!this.form.port || this.form.port < 1 || this.form.port > 65535) {
        this.errors.port = '请输入有效端口(1-65535)'
        return
      }

      try {
        if (this.isEdit) {
          await updateLB(this.selectedLB.id, this.form)
        } else {
          await createLB(this.form)
        }
        this.closeDialog()
        this.loadLBs()
      } catch (e) {
        this.formError = e.message || '操作失败，请稍后重试'
      }
    },
    closeDeleteDialog() {
      this.deleteDialogVisible = false
    },
    confirmDelete(lb) {
      this.selectedLB = lb
      this.deleteDialogVisible = true
    },
    async handleDelete() {
      try {
        await deleteLB(this.selectedLB.id)
        this.closeDeleteDialog()
        this.loadLBs()
      } catch (e) {
        alert(e.message || '删除失败')
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString()
    },
    formatAlgorithm(algorithm) {
      const map = {
        round_robin: '轮询',
        least_conn: '最少连接',
        source: '源IP'
      }
      return map[algorithm] || algorithm
    },
    formatStatus(status) {
      const map = {
        active: '活跃',
        inactive: '未激活'
      }
      return map[status] || status
    },
    getStatusClass(status) {
      return status === 'active' ? 'status-active' : 'status-inactive'
    }
  }
}
</script>

<style scoped>
.lbs-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.lbs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.lbs-header h2 {
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

.lbs-table {
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

.status-active {
  color: #67c23a;
}

.status-inactive {
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
