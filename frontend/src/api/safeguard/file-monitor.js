import api from '../auth'

// ========== 文件监控规则 ==========

// 获取监控规则列表
export function getFileMonitorRules(params) {
  return api.get('/safeguard/file-monitor/rules/', { params })
}

// 获取监控规则详情
export function getFileMonitorRule(id) {
  return api.get(`/safeguard/file-monitor/rules/${id}/`)
}

// 创建监控规则
export function createFileMonitorRule(data) {
  return api.post('/safeguard/file-monitor/rules/', data)
}

// 更新监控规则
export function updateFileMonitorRule(id, data) {
  return api.put(`/safeguard/file-monitor/rules/${id}/`, data)
}

// 删除监控规则
export function deleteFileMonitorRule(id) {
  return api.delete(`/safeguard/file-monitor/rules/${id}/`)
}

// ========== 文件监控事件 ==========

// 获取监控事件列表
export function getFileMonitorEvents(params) {
  return api.get('/safeguard/file-monitor/events/', { params })
}

// 触发事件采集
export function collectFileMonitorEvents(hostId) {
  return api.post('/safeguard/file-monitor/collect-events/', { host_id: hostId })
}
