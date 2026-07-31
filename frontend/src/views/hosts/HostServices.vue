<template>
  <div class="host-services">
    <div class="page-header">
      <button class="btn-back" @click="goBack">← 返回</button>
      <h2>{{ host?.hostname || '主机' }} - 服务控制</h2>
      <button class="btn-refresh" @click="loadServicesInfo" :disabled="loading">刷新</button>
    </div>

    <ServiceControl
      :services="services"
      :loading="loading"
      :error="error"
      @control="handleControlService"
      @get-logs="handleGetServiceLogs"
    />
  </div>
</template>

<script>
import { getHost } from '@/api/host'
import { getServicesInfo, controlService, getServiceLogs } from '@/api/safeguard/host-info'
import ServiceControl from '@/components/safeguard/ServiceControl.vue'

export default {
  name: 'HostServices',
  components: { ServiceControl },
  data() {
    return {
      hostId: null,
      host: null,
      services: [],
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
        await this.loadServicesInfo()
      } catch (e) {
        this.error = e.message || '加载数据失败'
      } finally {
        this.loading = false
      }
    },
    async loadServicesInfo() {
      try {
        const res = await getServicesInfo(this.hostId)
        this.services = res?.services || []
      } catch (e) {
        this.error = e.message || '获取服务信息失败'
      }
    },
    async handleControlService(serviceName, action) {
      await controlService(this.hostId, { name: serviceName, action })
      alert('操作成功')
      await this.loadServicesInfo()
    },
    async handleGetServiceLogs(serviceName) {
      const res = await getServiceLogs(this.hostId, serviceName)
      return res?.logs || ''
    },
    goBack() {
      this.$router.push(`/hosts/${this.hostId}/dashboard`)
    }
  }
}
</script>

<style scoped>
.host-services {
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