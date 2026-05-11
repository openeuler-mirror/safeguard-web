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
      <p class="drag-tip">提示：拖拽可调整同级菜单顺序</p>
      <div
        v-for="(menu, index) in menuTree"
        :key="menu.id"
        class="menu-item-wrapper"
        draggable="true"
        @dragstart="onDragStart($event, menu, 'top', index)"
        @dragover="onDragOver($event, 'top')"
        @dragleave="onDragLeave"
        @drop="onDrop($event, menu, 'top', index)"
        @dragend="onDragEnd"
      >
        <div class="menu-row" :class="{ 'drag-over-top': dragOverIndex === 'top-' + index }">
          <div class="drag-handle">⋮⋮</div>
          <div class="menu-info">
            <span class="menu-icon">{{ isEmoji(menu.meta?.icon) ? menu.meta.icon : '📁' }}</span>
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
          <div
            v-for="(child, childIndex) in menu.children"
            :key="child.id"
            class="menu-row child"
            draggable="true"
            @dragstart="onDragStart($event, child, menu.id, childIndex)"
            @dragover="onDragOver($event, menu.id)"
            @dragleave="onDragLeave"
            @drop="onDrop($event, child, menu.id, childIndex)"
            @dragend="onDragEnd"
          >
            <div class="drag-handle">⋮⋮</div>
            <div class="menu-info">
              <span class="menu-icon">{{ isEmoji(child.meta?.icon) ? child.meta.icon : '📄' }}</span>
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
            <select id="parentMenu" v-model="formData.parent">
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
import { getMenuTree, createMenu, updateMenu, deleteMenu, reorderMenus } from '@/api/authority'

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
      },
      // 拖拽相关
      draggingMenu: null,
      dragParentId: null,
      dragIndex: null,
      dragOverIndex: null
    }
  },
  computed: {
    parentMenuOptions() {
      // 显示所有可作为父菜单的选项，排除自身
      // 循环引用问题由后端验证
      if (!this.isEdit) {
        return this.allMenus.filter(m => !m.parent)
      }
      return this.allMenus.filter(m => {
        if (m.id === this.selectedMenu?.id) return false
        // 排除直接子菜单（防止循环引用）
        if (m.parent === this.selectedMenu?.id) return false
        return true
      })
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
        this.menuTree = res
        // 扁平化所有菜单用于父菜单选择
        this.allMenus = this.flattenMenus(res)
      } catch (e) {
        this.error = e.message || '加载菜单列表失败'
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
          parent: this.formData.parent,
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
          await createMenu(data)
          this.formSuccess = '创建成功'
        }
        setTimeout(() => {
          this.dialogVisible = false
          this.loadMenus()
        }, 1000)
      } catch (e) {
        this.formError = e.message || (this.isEdit ? '更新失败' : '创建失败')
      } finally {
        this.saving = false
      }
    },
    isEmoji(str) {
      if (!str) return false
      // 检查是否是emoji（Unicode范围）或单个字符
      const emojiRegex = /(\p{Emoji_Presentation}|\p{Emoji}\uFE0F)/u
      return emojiRegex.test(str) || (str.length <= 2 && !/^[a-zA-Z]/.test(str))
    },
    // 拖拽方法
    onDragStart(event, menu, parentId, index) {
      this.draggingMenu = menu
      this.dragParentId = parentId
      this.dragIndex = index
      event.dataTransfer.effectAllowed = 'move'
      event.target.closest('.menu-item-wrapper, .menu-row').classList.add('dragging')
    },
    onDragOver(event, parentId) {
      event.preventDefault()
      event.dataTransfer.dropEffect = 'move'
    },
    onDragLeave(event) {
      this.dragOverIndex = null
    },
    async onDrop(event, targetMenu, parentId, targetIndex) {
      event.preventDefault()
      if (!this.draggingMenu) return

      // 只有同级拖拽才有效
      if (this.dragParentId !== parentId) {
        alert('只能在同级菜单中拖拽')
        return
      }

      const menuList = parentId === 'top'
        ? [...this.menuTree]
        : [...(this.menuTree.find(m => m.id === parentId)?.children || [])]

      const fromIndex = menuList.findIndex(m => m.id === this.draggingMenu.id)
      const toIndex = menuList.findIndex(m => m.id === targetMenu.id)

      if (fromIndex === -1 || toIndex === -1 || fromIndex === toIndex) return

      // 移动元素
      menuList.splice(fromIndex, 1)
      menuList.splice(toIndex, 0, this.draggingMenu)

      // 更新本地 sort 值
      const orders = menuList.map((menu, index) => ({
        id: menu.id,
        sort: index * 10
      }))

      // 更新菜单树
      if (parentId === 'top') {
        this.menuTree = menuList
      } else {
        const parentMenu = this.menuTree.find(m => m.id === parentId)
        if (parentMenu) {
          parentMenu.children = menuList
        }
      }

      // 调用 API 保存
      try {
        await reorderMenus(orders)
        // 更新 store 中的菜单数据
        this.$store.dispatch('auth/fetchMenus')
      } catch (e) {
        alert('保存排序失败')
        this.loadMenus()
      }

      this.onDragEnd()
    },
    onDragEnd() {
      this.draggingMenu = null
      this.dragParentId = null
      this.dragIndex = null
      this.dragOverIndex = null
      document.querySelectorAll('.dragging').forEach(el => el.classList.remove('dragging'))
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
        alert(e.message || '删除失败')
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

.drag-tip {
  padding: 8px 16px;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  border-bottom: 1px solid #eee;
  margin: 0;
}

.drag-handle {
  cursor: move;
  color: #c0c4cc;
  padding: 0 8px;
  font-size: 14px;
  user-select: none;
}

.drag-handle:hover {
  color: #409eff;
}

.menu-item-wrapper {
  transition: opacity 0.3s;
}

.menu-item-wrapper.dragging {
  opacity: 0.5;
}

.menu-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.menu-row.drag-over-top {
  border-top: 2px solid #409eff;
}

.menu-row.drag-over-bottom {
  border-bottom: 2px solid #409eff;
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
  min-width: 0;
  overflow: hidden;
}

.menu-title {
  font-weight: 500;
  color: #333;
  min-width: 80px;
  flex-shrink: 0;
}

.menu-path {
  color: #409eff;
  font-size: 13px;
  font-family: monospace;
  background: #ecf5ff;
  padding: 2px 8px;
  border-radius: 3px;
  white-space: nowrap;
  flex-shrink: 0;
}

.menu-component {
  color: #909399;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
  flex-shrink: 0;
}

.menu-icon {
  font-size: 18px;
  width: 32px;
  min-width: 32px;
  text-align: center;
  flex-shrink: 0;
  margin-right: 4px;
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
