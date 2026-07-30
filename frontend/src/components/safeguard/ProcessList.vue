<template>
  <div class="process-list">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="process-table">
      <table>
        <thead>
          <tr>
            <th>PID</th>
            <th>进程名</th>
            <th>用户</th>
            <th>CPU%</th>
            <th>内存%</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="proc in processes" :key="proc.pid">
            <td>{{ proc.pid }}</td>
            <td>{{ proc.name }}</td>
            <td>{{ proc.user || '-' }}</td>
            <td :class="{ 'high-resource': proc.cpu_percent > 50 }">{{ proc.cpu_percent }}%</td>
            <td :class="{ 'high-resource': proc.mem_percent > 50 }">{{ proc.mem_percent }}%</td>
            <td>
              <StatusBadge :type="proc.status === 'running' ? 'success' : 'info'" :text="proc.status" />
            </td>
            <td>
              <button v-if="proc.pid !== 1" class="btn-kill" @click="handleKill(proc)">终止</button>
            </td>
          </tr>
          <tr v-if="processes.length === 0">
            <td colspan="7" class="empty-text">暂无进程信息</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 终止确认弹窗 -->
    <div v-if="killDialogVisible" class="dialog-overlay" @click.self="closeKillDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>确认终止进程</h3>
          <button class="dialog-close" @click="closeKillDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <p>确定要终止进程 <strong>{{ selectedProcess?.name }}</strong> (PID: {{ selectedProcess?.pid }}) 吗？</p>
          <p class="warning-text">此操作可能导致相关服务异常</p>
          <div class="checkbox-item">
            <label>
              <input type="checkbox" v-model="forceKill"> 强制终止 (SIGKILL)
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeKillDialog">取消</button>
          <button class="btn-danger" @click="confirmKill" :disabled="killing">{{ killing ? '终止中...' : '确认终止' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StatusBadge from './StatusBadge.vue'

export default {
  name: 'ProcessList',
  components: { StatusBadge },
  props: {
    processes: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    error: { type: String, default: '' }
  },
  data() {
    return {
      killDialogVisible: false,
      selectedProcess: null,
      forceKill: false,
      killing: false
    }
  },
  methods: {
    handleKill(proc) {
      this.selectedProcess = proc
      this.forceKill = false
      this.killing = false
      this.killDialogVisible = true
    },
    closeKillDialog() {
      this.killDialogVisible = false
      this.selectedProcess = null
    },
    async confirmKill() {
      if (!this.selectedProcess) return
      this.killing = true
      try {
        await this.$emit('kill', this.selectedProcess.pid, this.forceKill)
        this.closeKillDialog()
      } catch (e) {
        alert(e.message || '终止进程失败')
      } finally {
        this.killing = false
      }
    }
  }
}
</script>

<style scoped>
.process-list {
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

.process-table {
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

.high-resource {
  color: #f56c6c;
  font-weight: 600;
}

.empty-text {
  text-align: center;
  color: #999;
}

.btn-kill {
  padding: 4px 10px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-kill:hover {
  background: #f78989;
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
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
}

.warning-text {
  color: #f56c6c;
  font-size: 14px;
}

.checkbox-item {
  margin-top: 12px;
}

.checkbox-item label {
  cursor: pointer;
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

.btn-danger:hover:not(:disabled) {
  background: #f78989;
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
