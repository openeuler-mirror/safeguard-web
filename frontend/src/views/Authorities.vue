<template>
  <div class="authorities-container">
    <div class="authorities-header">
      <h2>角色管理</h2>
      <div class="header-actions">
        <button class="refresh-btn" @click="loadAuthorities">刷新</button>
        <button class="add-btn" @click="openCreateDialog">新增角色</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="authorities-table">
      <table>
        <thead>
          <tr>
            <th>角色ID</th>
            <th>角色名称</th>
            <th>父角色</th>
            <th>默认路由</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="auth in authorities" :key="auth.id">
            <td>{{ auth.authority_id }}</td>
            <td>{{ auth.authority_name }}</td>
            <td>{{ auth.parent_name || '-' }}</td>
            <td>{{ auth.default_router }}</td>
            <td>{{ formatDate(auth.created_at) }}</td>
            <td>
              <button class="action-btn edit-btn" @click="openEditDialog(auth)">编辑</button>
              <button class="action-btn menu-btn" @click="openMenuDialog(auth)">菜单</button>
              <button class="action-btn copy-btn" @click="handleCopy(auth)">复制</button>
              <button class="action-btn delete-btn" @click="handleDelete(auth)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建/编辑角色弹窗 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="dialogVisible = false">
      <div class="dialog-content">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑角色' : '新增角色' }}</h3>
          <button class="close-btn" @click="dialogVisible = false">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label for="authorityId">角色ID</label>
            <input
              id="authorityId"
              v-model="formData.authority_id"
              type="number"
              placeholder="请输入角色ID"
              :disabled="isEdit"
            />
          </div>
          <div class="form-group">
            <label for="authorityName">角色名称</label>
            <input
              id="authorityName"
              v-model="formData.authority_name"
              type="text"
              placeholder="请输入角色名称"
            />
          </div>
          <div class="form-group">
            <label for="parent">父角色</label>
            <select id="parent" v-model="formData.parent">
              <option :value="null">无</option>
              <option v-for="auth in parentOptions" :key="auth.id" :value="auth.id">
                {{ auth.authority_name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="defaultRouter">默认路由</label>
            <input
              id="defaultRouter"
              v-model="formData.default_router"
              type="text"
              placeholder="如: dashboard"
            />
          </div>
          <div v-if="formError" class="form-error">{{ formError }}</div>
          <div v-if="formSuccess" class="form-success">{{ formSuccess }}</div>
        </div>
        <div class="dialog-footer">
          <button class="cancel-btn" @click="dialogVisible = false">取消</button>
          <button class="save-btn" @click="handleSave" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 菜单绑定弹窗 -->
    <AuthorityMenuDialog
      :visible="menuDialogVisible"
      :authority-info="selectedAuthority"
      @close="menuDialogVisible = false"
      @success="handleMenuSuccess"
    />
  </div>
</template>

<script>
import {
  getAuthorities,
  createAuthority,
  updateAuthority,
  deleteAuthority,
  copyAuthority
} from '@/api/authority'
import AuthorityMenuDialog from '@/components/AuthorityMenuDialog.vue'

export default {
  name: 'Authorities',
  components: {
    AuthorityMenuDialog
  },
  data() {
    return {
      authorities: [],
      loading: false,
      error: '',
      dialogVisible: false,
      menuDialogVisible: false,
      isEdit: false,
      selectedAuthority: {},
      saving: false,
      formError: '',
      formSuccess: '',
      formData: {
        authority_id: '',
        authority_name: '',
        parent: null,
        default_router: 'dashboard'
      }
    }
  },
  computed: {
    parentOptions() {
      // 排除自身，防止循环引用
      return this.authorities.filter(a => !this.isEdit || a.id !== this.selectedAuthority.id)
    }
  },
  mounted() {
    this.loadAuthorities()
  },
  methods: {
    async loadAuthorities() {
      this.loading = true
      this.error = ''
      try {
        const res = await getAuthorities()
        this.authorities = res.data.results || res.data
      } catch (e) {
        this.error = e.response?.data?.error || '加载角色列表失败'
      } finally {
        this.loading = false
      }
    },
    openCreateDialog() {
      this.isEdit = false
      this.formData = {
        authority_id: '',
        authority_name: '',
        parent: null,
        default_router: 'dashboard'
      }
      this.formError = ''
      this.formSuccess = ''
      this.dialogVisible = true
    },
    openEditDialog(auth) {
      this.isEdit = true
      this.selectedAuthority = auth
      this.formData = {
        authority_id: auth.authority_id,
        authority_name: auth.authority_name,
        parent: auth.parent,
        default_router: auth.default_router
      }
      this.formError = ''
      this.formSuccess = ''
      this.dialogVisible = true
    },
    openMenuDialog(auth) {
      this.selectedAuthority = auth
      this.menuDialogVisible = true
    },
    async handleSave() {
      if (!this.formData.authority_id) {
        this.formError = '请输入角色ID'
        return
      }
      if (!this.formData.authority_name) {
        this.formError = '请输入角色名称'
        return
      }
      this.saving = true
      this.formError = ''
      this.formSuccess = ''
      try {
        const data = {
          authority_name: this.formData.authority_name,
          parent: this.formData.parent,
          default_router: this.formData.default_router
        }
        if (this.isEdit) {
          await updateAuthority(this.selectedAuthority.id, data)
          this.formSuccess = '更新成功'
        } else {
          data.authority_id = this.formData.authority_id
          await createAuthority(data)
          this.formSuccess = '创建成功'
        }
        setTimeout(() => {
          this.dialogVisible = false
          this.loadAuthorities()
        }, 1000)
      } catch (e) {
        this.formError = e.response?.data?.error || (this.isEdit ? '更新失败' : '创建失败')
      } finally {
        this.saving = false
      }
    },
    async handleCopy(auth) {
      try {
        await copyAuthority(auth.id)
        this.loadAuthorities()
      } catch (e) {
        alert(e.response?.data?.error || '复制失败')
      }
    },
    async handleDelete(auth) {
      if (!confirm(`确定要删除角色「${auth.authority_name}」吗？`)) {
        return
      }
      try {
        await deleteAuthority(auth.id)
        this.loadAuthorities()
      } catch (e) {
        alert(e.response?.data?.error || '删除失败')
      }
    },
    handleMenuSuccess() {
      this.loadAuthorities()
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
.authorities-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.authorities-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.authorities-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.refresh-btn, .add-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn {
  background: #f0f0f0;
  color: #666;
}

.refresh-btn:hover {
  background: #e0e0e0;
}

.add-btn {
  background: #67c23a;
  color: white;
}

.add-btn:hover {
  background: #85ce61;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #f56c6c;
}

.authorities-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
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

.action-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 6px;
}

.edit-btn {
  background: #409eff;
  color: white;
}

.edit-btn:hover {
  background: #66b1ff;
}

.menu-btn {
  background: #e6a23c;
  color: white;
}

.menu-btn:hover {
  background: #ebb563;
}

.copy-btn {
  background: #909399;
  color: white;
}

.copy-btn:hover {
  background: #a6a9ab;
}

.delete-btn {
  background: #f56c6c;
  color: white;
}

.delete-btn:hover {
  background: #f78989;
}

/* 弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  border-radius: 8px;
  width: 450px;
  max-width: 90%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
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
  font-size: 16px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #666;
}

.dialog-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #666;
  font-size: 14px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #409eff;
}

.form-group input:disabled {
  background: #f5f5f5;
  color: #999;
}

.form-error {
  color: #f56c6c;
  font-size: 14px;
  margin-top: 8px;
}

.form-success {
  color: #67c23a;
  font-size: 14px;
  margin-top: 8px;
}

.dialog-footer {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn, .save-btn {
  padding: 8px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn {
  background: #f0f0f0;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.save-btn {
  background: #409eff;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.save-btn:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}
</style>
