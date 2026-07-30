import api from '../auth'

// ========== 策略模板 ==========

// 获取策略模板列表
export function getPolicyTemplates(params) {
  return api.get('/safeguard/policy/templates/', { params })
}

// 获取策略模板详情
export function getPolicyTemplate(id) {
  return api.get(`/safeguard/policy/templates/${id}/`)
}

// 创建策略模板
export function createPolicyTemplate(data) {
  return api.post('/safeguard/policy/templates/', data)
}

// 更新策略模板
export function updatePolicyTemplate(id, data) {
  return api.put(`/safeguard/policy/templates/${id}/`, data)
}

// 删除策略模板
export function deletePolicyTemplate(id) {
  return api.delete(`/safeguard/policy/templates/${id}/`)
}

// 克隆策略模板
export function clonePolicyTemplate(id) {
  return api.post(`/safeguard/policy/templates/${id}/clone/`)
}

// ========== 主机策略 ==========

// 获取主机策略
export function getHostPolicy(hostId) {
  return api.get(`/safeguard/policy/host/${hostId}/`)
}

// 绑定主机策略
export function bindHostPolicy(hostId, data) {
  return api.post(`/safeguard/policy/host/${hostId}/bind/`, data)
}

// ========== 策略下发 ==========

// 下发策略
export function applyPolicy(templateId, hostIds) {
  return api.post(`/safeguard/policy/templates/${templateId}/apply/`, { host_ids: hostIds })
}

// 获取任务状态
export function getPolicyTask(taskId) {
  return api.get(`/safeguard/policy/tasks/${taskId}/`)
}

// 获取任务列表
export function getPolicyTasks(params) {
  return api.get('/safeguard/policy/tasks/', { params })
}
