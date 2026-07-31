import api from '../auth'

// 获取实时监控数据
export function getRealTimeMonitor(hostId) {
  return api.get('/safeguard/monitor/real-time/', { params: { host_id: hostId } })
}

// 获取历史监控数据
export function getMonitorHistory(hostId, params) {
  return api.get('/safeguard/monitor/history/', { params: { host_id: hostId, ...params } })
}

// 触发监控数据采集
export function collectMonitor(hostId) {
  return api.post('/safeguard/monitor/collect/', { host_id: hostId })
}
