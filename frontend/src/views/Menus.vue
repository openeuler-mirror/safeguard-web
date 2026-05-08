<template>
  <div class="menus-container">
    <div class="menus-header">
      <h2>菜单管理</h2>
      <div class="header-actions">
        <button class="refresh-btn" @click="loadMenus">刷新</button>
        <button class="add-btn" @click="openCreateDialog(null)">新增菜单</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="menus-tree">
      <div v-for="menu in menuTree" :key="menu.id" class="menu-item-wrapper">
        <div class="menu-row">
          <div class="menu-info">
            <span class="menu-icon">{{ menu.meta?.icon || '📁' }}</span>
            <span class="menu-title">{{ menu.meta?.title || menu.name }}</span>
            <span class="menu-path">{{ menu.path }}</span>
            <span class="menu-component">{{ menu.component || '-' }}</span>
          </div>
          <div class="menu-actions">
            <button class="action-btn add-child-btn" @click="openCreateDialog(menu)" title="添加子菜单">+子</button>
            <button class="action-btn edit-btn" @click="openEditDialog(menu)">编辑</button>
            <button class="action-btn delete-btn" @click="handleDelete(menu)">删除</button>
          </div>
        </div>
        <!-- 子菜单 -->
        <div v-if="menu.children && menu.children.length" class="children-menus">
          <div v-for="child in menu.children" :key="child.id" class="menu-row child">
            <div class="menu-info">
              <span class="menu-icon">{{ child.meta?.icon || '📄' }}</span>
              <span class="menu-title">{{ child.meta?.title || child.name }}</span>
              <span class="menu-path">{{ child.path }}</span>
              <span class="menu-component">{{ child.component || '-' }}</span>
            </div>
            <div class="menu-actions">
              <button class="action-btn edit-btn" @click="openEditDialog(child)">编辑</button>
              <button class="action-btn delete-btn" @click="handleDelete(child)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑菜单弹窗 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="dialogVisible = false">
      <div class="dialog-content">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑菜单' : '新增菜单' }}</h3>
          <button class="close-btn" @click="dialogVisible = false">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label for="parentMenu">父菜单</label>
            <select id="parentMenu" v-model="formData.parent" :disabled="isEdit">
              <option :value="null">无（顶级菜单）</option>
              <option v-for="m in parentMenuOptions" :key="m.id" :value="m.id">
                {{ m.meta?.title || m.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="path">路由路径</label>
            <input
              id="path"
              v-model="formData.path"
              type="text"
              placeholder="如: /users"
            />
          </div>
          <div class="form-group">
            <label for="name">路由名称</label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              placeholder="如: Users"
            />
          </div>
          <div class="form-group">
            <label for="component">前端组件</label>
            <input
              id="component"
              v-model="formData.component"
              type="text"
              placeholder="如: @/views/Users.vue"
            />
          </div>
          <div class="form-group">
            <label for="sort">排序</label>
            <input
              id="sort"
              v-model.number="formData.sort"
              type="number"
              placeholder="数字越小越靠前"
            />
          </div>
          <div class="form-group">
            <label for="title">菜单标题</label>
            <input
              id="title"
              v-model="formData.meta.title"
              type="text"
              placeholder="显示在导航栏的名称"
            />
          </div>
          <div class="form-group">
            <label for="icon">图标</label>
            <input
              id="icon"
              v-model="formData.meta.icon"
              type="text"
              placeholder="如: 👤 或 element 图标名"
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
  </div>
</template>

<script>
import { getMenuTree, createMenu, updateMenu, deleteMenu } from '@/api/authority'

export default {
  name: 'Menus',
  data() {
    return {
      menuTree: [],
      allMenus: [],
      loading: false,
      error: '',
      dialogVisible: false,
      isEdit: false,
      selectedMenu: null,
      saving: false,
      formError: '',
      formSuccess: '',
      formData: {
        parent: null,
        path: '',
        name: '',
        component: '',
        sort: 0,
        meta: {
          title: '',
          icon: ''
        }
      }
    }
  },
  computed: {
    parentMenuOptions() {
      // 只显示顶级菜单作为父菜单选项，排除自身
      return this.allMenus.filter(m => !m.parent && (!this.isEdit || m.id !== this.selectedMenu?.id))
    }
  },
  mounted() {
    this.loadMenus()
  },
  methods: {
    async loadMenus() {
      this.loading = true
      this.error = ''
      try {
        const res = await getMenuTree()
        this.menuTree = res.data
        // 扁平化所有菜单用于父菜单选择
        this.allMenus = this.flattenMenus(res.data)
      } catch (e) {
        this.error = e.response?.data?.error || '加载菜单列表失败'
      } finally {
        this.loading = false
      }
    },
    flattenMenus(menus, result = []) {
      for (const menu of menus) {
        result.push(menu)
        if (menu.children && menu.children.length) {
          this.flattenMenus(menu.children, result)
        }
      }
      return result
    },
    openCreateDialog(parentMenu) {
      this.isEdit = false
      this.selectedMenu = null
      this.formData = {
        parent: parentMenu ? parentMenu.id : null,
        path: '',
        name: '',
        component: '',
        sort: 0,
        meta: {
          title: '',
          icon: ''
        }
      }
      this.formError = ''
      this.formSuccess = ''
      this.dialogVisible = true
    },
    openEditDialog(menu) {
      this.isEdit = true
      this.selectedMenu = menu
      this.formData = {
        parent: menu.parent,
        path: menu.path,
        name: menu.name,
        component: menu.component || '',
        sort: menu.sort || 0,
        meta: {
          title: menu.meta?.title || '',
          icon: menu.meta?.icon || ''
        }
      }
      this.formError = ''
      this.formSuccess = ''
      this.dialogVisible = true
    },
    async handleSave() {
      if (!this.formData.path) {
        this.formError = '请输入路由路径'
        return
      }
      if (!this.formData.name) {
        this.formError = '请输入路由名称'
        return
      }
      this.saving = true
      this.formError = ''
      this.formSuccess = ''
      try {
        const data = {
          path: this.formData.path,
          name: this.formData.name,
          component: this.formData.component,
          sort: this.formData.sort,
          meta: this.formData.meta
        }
        if (this.isEdit) {
          await updateMenu(this.selectedMenu.id, data)
          this.formSuccess = '更新成功'
        } else {
          data.parent = this.formData.parent
          await createMenu(data)
          this.formSuccess = '创建成功'
        }
        setTimeout(() => {
          this.dialogVisible = false
          this.loadMenus()
        }, 1000)
      } catch (e) {
        this.formError = e.response?.data?.error || (this.isEdit ? '更新失败' : '创建失败')
      } finally {
        this.saving = false
      }
    },
    async handleDelete(menu) {
      const childCount = menu.children?.length || 0
      const message = childCount > 0
        ? `确定要删除菜单「${menu.meta?.title || menu.name}」及其${childCount}个子菜单吗？`
        : `确定要删除菜单「${menu.meta?.title || menu.name}」吗？`

      if (!confirm(message)) {
        return
      }
      try {
        await deleteMenu(menu.id)
        this.loadMenus()
      } catch (e) {
        alert(e.response?.data?.error || '删除失败')
      }
    }
  }
}
</script>

<style scoped>
.menus-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.menus-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.menus-header h2 {
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

.menus-tree {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.menu-item-wrapper {
  border-bottom: 1px solid #eee;
}

.menu-item-wrapper:last-child {
  border-bottom: none;
}

.menu-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px 16px;
  gap: 12px;
}

.menu-row:hover {
  background: #fafafa;
}

.menu-row.child {
  background: #f9f9f9;
  padding-left: 48px;
}

.menu-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  flex-wrap: wrap;
  min-width: 0;
}

.menu-title {
  font-weight: 500;
  color: #333;
  min-width: 80px;
}

.menu-path {
  color: #409eff;
  font-size: 13px;
  font-family: monospace;
  background: #ecf5ff;
  padding: 2px 8px;
  border-radius: 3px;
  white-space: nowrap;
}

.menu-component {
  color: #909399;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.menu-icon {
  font-size: 16px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.menu-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 4px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.action-btn:hover {
  opacity: 0.8;
}

.add-child-btn {
  background: #e6a23c;
  color: white;
}

.edit-btn {
  background: #409eff;
  color: white;
}

.delete-btn {
  background: #f56c6c;
  color: white;
}

.children-menus {
  border-top: 1px solid #eee;
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
  width: 500px;
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
  max-height: 60vh;
  overflow-y: auto;
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
