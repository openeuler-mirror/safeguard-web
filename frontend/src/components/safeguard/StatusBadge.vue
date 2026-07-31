<template>
  <span :class="['status-badge', typeClass]">
    {{ label }}
  </span>
</template>

<script>
export default {
  name: 'StatusBadge',
  props: {
    type: {
      type: String,
      default: 'default',
      validator: v => ['success', 'warning', 'danger', 'info', 'online', 'offline', 'default'].includes(v)
    },
    text: {
      type: String,
      default: ''
    }
  },
  computed: {
    typeClass() {
      const map = {
        success: 'status-success',
        warning: 'status-warning',
        danger: 'status-danger',
        info: 'status-info',
        online: 'status-online',
        offline: 'status-offline'
      }
      return map[this.type] || 'status-default'
    },
    label() {
      const map = {
        success: '成功',
        warning: '警告',
        danger: '失败',
        info: '信息',
        online: '在线',
        offline: '离线'
      }
      return this.text || map[this.type] || this.type
    }
  }
}
</script>

<style scoped>
.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
.status-success { background: #e1f3d8; color: #67c23a; }
.status-warning { background: #faecd8; color: #e6a23c; }
.status-danger { background: #fde2e2; color: #f56c6c; }
.status-info { background: #e9e9eb; color: #909399; }
.status-online { background: #e1f3d8; color: #67c23a; }
.status-offline { background: #e9e9eb; color: #909399; }
</style>
