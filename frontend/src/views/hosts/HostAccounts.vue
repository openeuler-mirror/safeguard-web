<template>
  <div class="host-accounts">
    <div class="page-header">
      <button class="btn-back" @click="goBack">← 返回</button>
      <h2>{{ host?.hostname || '主机' }} - 系统账户</h2>
      <button class="btn-refresh" @click="loadAccountsInfo" :disabled="loading">刷新</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="accounts-table">
      <table>
        <thead>
          <tr>
            <th>用户名</th>
            <th>UID</th>
            <th>GID</th>
            <th>用户主目录</th>
            <th>Shell</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="account in accounts" :key="account.username">
            <td>{{ account.username }}</td>
            <td>{{ account.uid }}</td>
            <td>{{ account.gid }}</td>
            <td>{{ account.home || '-' }}</td>
            <td>{{ account.shell || '-' }}</td>
            <td>
              <StatusBadge :type="account.locked ? 'danger' : 'success'" :text="account.locked ? '已锁定' : '正常'" />
            </td>
          </tr>
          <tr v-if="accounts.length === 0">
            <td colspan="6" class="empty-text">暂无账户信息</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { getHost } from '@/api/host'
import { getAccountsInfo } from '@/api/safeguard/host-info'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

export default {
  name: 'HostAccounts',
  components: { StatusBadge },
  data() {
    return {
      hostId: null,
      host: null,
      accounts: [],
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
        await this.loadAccountsInfo()
      } catch (e) {
        this.error = e.message || '加载数据失败'
      } finally {
        this.loading = false
      }
    },
    async loadAccountsInfo() {
      try {
        this.error = ''
        const res = await getAccountsInfo(this.hostId)
        this.accounts = res?.accounts || []
      } catch (e) {
        this.error = e.message || '获取账户信息失败'
      }
    },
    goBack() {
      this.$router.push(`/hosts/${this.hostId}/dashboard`)
    }
  }
}
</script>

<style scoped>
.host-accounts {
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

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #f56c6c;
}

.accounts-table {
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
</style>