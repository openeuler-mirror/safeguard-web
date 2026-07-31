<template>
  <div class="host-processes">
    <div class="page-header">
      <button class="btn-back" @click="goBack">← 返回</button>
      <h2>{{ host?.hostname || '主机' }} - 进程管理</h2>
      <button class="btn-refresh" @click="loadProcessesInfo" :disabled="loading">刷新</button>
    </div>

    <ProcessList
      :processes="processes"
      :loading="loading"
      :error="error"
      @kill="handleKillProcess"
    />
  </div>
</template>

<script>
import { getHost } from '@/api/host'
import { getProcessesInfo, killProcess } from '@/api/safeguard/host-info'
import ProcessList from '@/components/safeguard/ProcessList.vue'

export default {
  name: 'HostProcesses',
  components: { ProcessList },
  data() {
    return {
      hostId: null,
      host: null,
      processes: [],
      loading: false,
      error: ''
    }
  },
  mounted() {
    this.hostId = this.$route.params.id
    if (this.hostId) {
      this.loadData()
    }
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = ''
      try {
        const hostRes = await getHost(this.hostId)
        this.host = hostRes
        await this.loadProcessesInfo()
      } catch (e) {
        this.error = e.message || '加载数据失败'
      } finally {
        this.loading = false
      }
    },
    async loadProcessesInfo() {
      try {
        const res = await getProcessesInfo(this.hostId)
        this.processes = res?.processes || []
      } catch (e) {
        this.error = e.message || '获取进程信息失败'
      }
    },
    async handleKillProcess(pid, force) {
      await killProcess(this.hostId, pid, force)
      alert('进程已终止')
      await this.loadProcessesInfo()
    },
    goBack() {
      this.$router.push(`/hosts/${this.hostId}/dashboard`)
    }
  }
}
</script>

<style scoped>
.host-processes {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.btn-back {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.btn-back:hover {
  background: #eee;
}

.btn-refresh {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-refresh:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>