import api from './auth'

// ========== LoadBalancer ==========

// 获取负载均衡器列表
export function getLBs(params) {
  return api.get('/lbs/', { params })
}

// 获取负载均衡器详情
export function getLB(id) {
  return api.get(`/lbs/${id}/`)
}

// 创建负载均衡器
export function createLB(data) {
  return api.post('/lbs/', data)
}

// 更新负载均衡器
export function updateLB(id, data) {
  return api.put(`/lbs/${id}/`, data)
}

// 删除负载均衡器
export function deleteLB(id) {
  return api.delete(`/lbs/${id}/`)
}

// ========== Listener ==========

// 获取监听器列表
export function getListeners(params) {
  return api.get('/listeners/', { params })
}

// 获取监听器详情
export function getListener(id) {
  return api.get(`/listeners/${id}/`)
}

// 创建监听器
export function createListener(data) {
  return api.post('/listeners/', data)
}

// 更新监听器
export function updateListener(id, data) {
  return api.put(`/listeners/${id}/`, data)
}

// 删除监听器
export function deleteListener(id) {
  return api.delete(`/listeners/${id}/`)
}

// ========== Pool ==========

// 获取后端池列表
export function getPools(params) {
  return api.get('/pools/', { params })
}

// 获取后端池详情
export function getPool(id) {
  return api.get(`/pools/${id}/`)
}

// 创建后端池
export function createPool(data) {
  return api.post('/pools/', data)
}

// 更新后端池
export function updatePool(id, data) {
  return api.put(`/pools/${id}/`, data)
}

// 删除后端池
export function deletePool(id) {
  return api.delete(`/pools/${id}/`)
}

// ========== Member ==========

// 获取池成员列表
export function getMembers(params) {
  return api.get('/members/', { params })
}

// 获取池成员详情
export function getMember(id) {
  return api.get(`/members/${id}/`)
}

// 创建池成员
export function createMember(data) {
  return api.post('/members/', data)
}

// 更新池成员
export function updateMember(id, data) {
  return api.put(`/members/${id}/`, data)
}

// 删除池成员
export function deleteMember(id) {
  return api.delete(`/members/${id}/`)
}

// ========== HealthMonitor ==========

// 获取健康检查列表
export function getHealthMonitors(params) {
  return api.get('/health-monitors/', { params })
}

// 获取健康检查详情
export function getHealthMonitor(id) {
  return api.get(`/health-monitors/${id}/`)
}

// 创建健康检查
export function createHealthMonitor(data) {
  return api.post('/health-monitors/', data)
}

// 更新健康检查
export function updateHealthMonitor(id, data) {
  return api.put(`/health-monitors/${id}/`, data)
}

// 删除健康检查
export function deleteHealthMonitor(id) {
  return api.delete(`/health-monitors/${id}/`)
}

export default {
  // LoadBalancer
  getLBs,
  getLB,
  createLB,
  updateLB,
  deleteLB,
  // Listener
  getListeners,
  getListener,
  createListener,
  updateListener,
  deleteListener,
  // Pool
  getPools,
  getPool,
  createPool,
  updatePool,
  deletePool,
  // Member
  getMembers,
  getMember,
  createMember,
  updateMember,
  deleteMember,
  // HealthMonitor
  getHealthMonitors,
  getHealthMonitor,
  createHealthMonitor,
  updateHealthMonitor,
  deleteHealthMonitor,
}
