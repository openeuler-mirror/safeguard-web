<template>
  <div v-if="visible" class="dialog-overlay" @click.self="handleClose">
    <div class="dialog-content">
      <div class="dialog-header">
        <h3>为「{{ authorityInfo.authority_name }}」分配菜单</h3>
        <button class="close-btn" @click="handleClose">&times;</button>
      </div>

      <div class="dialog-body">
        <div class="info-bar">
          <span class="info-item">角色ID: {{ authorityInfo.authority_id }}</span>
          <span class="info-item">角色名称: {{ authorityInfo.authority_name }}</span>
        </div>

        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else class="menu-tree">
          <div v-for="menu in menuTree" :key="menu.id" class="menu-item">
            <label class="menu-label">
              <input
                type="checkbox"
                :value="menu.id"
                v-model="selectedMenuIds"
                @change="handleMenuChange(menu)"
              />
              <span class="menu-name">{{ menu.meta?.title || menu.name }}</span>
              <span class="menu-path">{{ menu.path }}</span>
            </label>
            <!-- 子菜单 -->
            <div v-if="menu.children && menu.children.length" class="children-menus">
              <div v-for="child in menu.children" :key="child.id" class="menu-item child">
                <label class="menu-label">
                  <input
                    type="checkbox"
                    :value="child.id"
                    v-model="selectedMenuIds"
                    :disabled="!isParentSelected(menu.id)"
                    @change="handleMenuChange(child)"
                  />
                  <span class="menu-name">{{ child.meta?.title || child.name }}</span>
                  <span class="menu-path">{{ child.path }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="dialog-footer">
        <div v-if="message" :class="['message', messageType]">{{ message }}</div>
        <button class="cancel-btn" @click="handleClose">取消</button>
        <button class="save-btn" @click="handleSave" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { getAuthorityMenus, setAuthorityMenus, getMenuTree } from '@/api/authority'

export default {
  name: 'AuthorityMenuDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    authorityInfo: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'success'],
  data() {
    return {
      menuTree: [],
      selectedMenuIds: [],
      loading: false,
      saving: false,
      message: '',
      messageType: '',
      error: ''
    }
  },
  watch: {
    visible: {
      handler(newVal) {
        if (newVal) {
          this.loadData()
        } else {
          this.reset()
        }
      }
    }
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = ''
      try {
        // 并行加载菜单树和角色已有的菜单
        const [treeRes, menuRes] = await Promise.all([
          getMenuTree(),
          getAuthorityMenus(this.authorityInfo.id)
        ])
        this.menuTree = treeRes.data
        // 从响应中提取已选中的菜单ID
        this.selectedMenuIds = menuRes.data.map(item => item.id)
      } catch (e) {
        this.error = e.response?.data?.error || '加载菜单数据失败'
      } finally {
        this.loading = false
      }
    },
    handleMenuChange(menu) {
      // 如果选中了父菜单，自动选中所有子菜单
      // 如果取消了父菜单，自动取消所有子菜单（但这个通过子菜单的disabled状态和手动取消来处理）
      this.$forceUpdate()
    },
    isParentSelected(parentId) {
      return this.selectedMenuIds.includes(parentId)
    },
    async handleSave() {
      this.saving = true
      this.message = ''
      try {
        await setAuthorityMenus(this.authorityInfo.id, this.selectedMenuIds)
        this.message = '保存成功'
        this.messageType = 'success'
        setTimeout(() => {
          this.$emit('success')
          this.$emit('close')
        }, 1000)
      } catch (e) {
        this.message = e.response?.data?.error || '保存失败'
        this.messageType = 'error'
      } finally {
        this.saving = false
      }
    },
    handleClose() {
      this.$emit('close')
    },
    reset() {
      this.menuTree = []
      this.selectedMenuIds = []
      this.loading = false
      this.saving = false
      this.message = ''
      this.messageType = ''
      this.error = ''
    }
  }
}
</script>

<style scoped>
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
  width: 550px;
  max-width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
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
  overflow-y: auto;
  flex: 1;
}

.info-bar {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  display: flex;
  gap: 20px;
}

.info-item {
  color: #666;
  font-size: 14px;
}

.loading, .error {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: #f56c6c;
}

.menu-tree {
  max-height: 400px;
  overflow-y: auto;
}

.menu-item {
  padding: 8px 0;
}

.menu-item.child {
  padding-left: 24px;
}

.menu-label {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
}

.menu-label:hover {
  background: #f5f5f5;
}

.menu-label input {
  margin-right: 10px;
}

.menu-name {
  flex: 1;
  color: #333;
}

.menu-path {
  color: #999;
  font-size: 12px;
  margin-left: 10px;
}

.children-menus {
  margin-left: 12px;
  border-left: 2px solid #eee;
}

.dialog-footer {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

.message {
  margin-right: auto;
  font-size: 14px;
}

.message.success {
  color: #67c23a;
}

.message.error {
  color: #f56c6c;
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
