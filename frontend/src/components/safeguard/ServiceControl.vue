<template>
  <div class="service-control">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="service-table">
      <table>
        <thead>
          <tr>
            <th>服务名</th>
            <th>状态</th>
            <th>是否启用</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="service in services" :key="service.name">
            <td>{{ service.name }}</td>
            <td>
              <StatusBadge :type="service.active ? 'success' : 'offline'" :text="service.active ? '运行中' : '已停止'" />
            </td>
            <td>
              <StatusBadge :type="service.enabled ? 'success' : 'info'" :text="service.enabled ? '是' : '否'" />
            </td>
            <td>
              <div class="action-buttons">
                <button v-if="!service.active" class="btn-action btn-start" @click="handleAction(service, 'start')">启动</button>
                <button v-else class="btn-action btn-stop" @click="handleAction(service, 'stop')">停止</button>
                <button class="btn-action btn-restart" @click="handleAction(service, 'restart')">重启</button>
                <button v-if="service.active" class="btn-action btn-logs" @click="handleViewLogs(service)">日志</button>
              </div>
            </td>
          </tr>
          <tr v-if="services.length === 0">
            <td colspan="4" class="empty-text">暂无服务信息</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 操作确认弹窗 -->
    <div v-if="actionDialogVisible" class="dialog-overlay" @click.self="closeActionDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ actionTitle }}</h3>
          <button class="dialog-close" @click="closeActionDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <p>确定要{{ actionTitle }}服务 <strong>{{ selectedService?.name }}</strong> 吗？</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeActionDialog">取消</button>
          <button class="btn-primary" @click="confirmAction" :disabled="actioning">{{ actioning ? '操作中...' : '确认' }}</button>
        </div>
      </div>
    </div>

    <!-- 查看日志弹窗 -->
    <div v-if="logsDialogVisible" class="dialog-overlay dialog-large" @click.self="closeLogsDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>服务日志 - {{ selectedService?.name }}</h3>
          <button class="dialog-close" @click="closeLogsDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="logsLoading" class="loading">加载中...</div>
          <div v-else-if="logsError" class="error">{{ logsError }}</div>
          <pre v-else class="logs-content">{{ serviceLogs }}</pre>
        </div>
        <div class="dialog-footer">
          <button class="btn-primary" @click="refreshLogs" :disabled="logsLoading">刷新</button>
          <button class="btn-cancel" @click="closeLogsDialog">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StatusBadge from './StatusBadge.vue'

export default {
  name: 'ServiceControl',
  components: { StatusBadge },
  props: {
    services: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    error: { type: String, default: '' },
    onControl: { type: Function, default: null },
    onGetLogs: { type: Function, default: null }
  },
  data() {
    return {
      actionDialogVisible: false,
      selectedService: null,
      selectedAction: '',
      actioning: false,
      logsDialogVisible: false,
      serviceLogs: '',
      logsLoading: false,
      logsError: ''
    }
  },
  computed: {
    actionTitle() {
      const map = {
        start: '启动',
        stop: '停止',
        restart: '重启',
        reload: '重载',
        enable: '启用',
        disable: '禁用'
      }
      return map[this.selectedAction] || this.selectedAction
    }
  },
  methods: {
    handleAction(service, action) {
      this.selectedService = service
      this.selectedAction = action
      this.actioning = false
      this.actionDialogVisible = true
    },
    closeActionDialog() {
      this.actionDialogVisible = false
      this.selectedService = null
    },
    async confirmAction() {
      if (!this.selectedService || !this.selectedAction) return
      this.actioning = true
      try {
        if (this.onControl) {
          await this.onControl(this.selectedService.name, this.selectedAction)
        }
        this.closeActionDialog()
      } catch (e) {
        alert(e.message || '操作失败')
      } finally {
        this.actioning = false
      }
    },
    handleViewLogs(service) {
      this.selectedService = service
      this.logsDialogVisible = true
      this.serviceLogs = ''
      this.logsLoading = false
      this.logsError = ''
      this.refreshLogs()
    },
    closeLogsDialog() {
      this.logsDialogVisible = false
      this.selectedService = null
    },
    async refreshLogs() {
      if (!this.selectedService) return
      this.logsLoading = true
      this.logsError = ''
      try {
        let logs = '(暂无日志)'
        if (this.onGetLogs) {
          logs = await this.onGetLogs(this.selectedService.name)
        }
        this.serviceLogs = logs || '(暂无日志)'
      } catch (e) {
        this.logsError = e.message || '获取日志失败'
      } finally {
        this.logsLoading = false
      }
    }
  }
}
</script>

<style scoped>
.service-control {
  width: 100%;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #f56c6c;
}

.service-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
  white-space: nowrap;
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

.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.btn-action {
  padding: 4px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: white;
}

.btn-start {
  background: #67c23a;
}

.btn-start:hover {
  background: #85ce61;
}

.btn-stop {
  background: #f56c6c;
}

.btn-stop:hover {
  background: #f78989;
}

.btn-restart {
  background: #e6a23c;
}

.btn-restart:hover {
  background: #ebb563;
}

.btn-logs {
  background: #409eff;
}

.btn-logs:hover {
  background: #66b1ff;
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
  width: 450px;
  max-width: 90%;
}

.dialog-large .dialog {
  width: 700px;
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
  max-height: 400px;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
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

.btn-primary {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.logs-content {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 350px;
  overflow-y: auto;
  font-size: 12px;
  line-height: 1.5;
}
</style>