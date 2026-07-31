import api from '../auth'

// ========== 审计日志 ==========

// 获取审计日志列表
export function getAuditLogs(params) {
  return api.get('/safeguard/audit/logs/', { params })
}

// 获取审计日志详情
export function getAuditLog(id) {
  return api.get(`/safeguard/audit/logs/${id}/`)
}

// 获取审计统计数据
export function getAuditStats(params) {
  return api.get('/safeguard/audit/stats/', { params })
}
