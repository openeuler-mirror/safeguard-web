import api from './auth'

// ========== Cluster ==========

// 获取集群列表
export function getClusters(params) {
  return api.get('/clusters/', { params })
}

// 获取集群详情
export function getCluster(id) {
  return api.get(`/clusters/${id}/`)
}

// 创建集群
export function createCluster(data) {
  return api.post('/clusters/', data)
}

// 更新集群
export function updateCluster(id, data) {
  return api.put(`/clusters/${id}/`, data)
}

// 删除集群
export function deleteCluster(id) {
  return api.delete(`/clusters/${id}/`)
}

// 获取集群树下拉（用于下拉选择）
export function getClusterTree() {
  return api.get('/clusters/tree/')
}

// 获取集群拓扑
export function getClusterTopology(id) {
  return api.get(`/clusters/${id}/topology/`)
}

// ========== Host ==========

// 获取主机列表
export function getHosts(params) {
  return api.get('/hosts/', { params })
}

// 获取主机详情
export function getHost(id) {
  return api.get(`/hosts/${id}/`)
}

// 创建主机
export function createHost(data) {
  return api.post('/hosts/', data)
}

// 更新主机
export function updateHost(id, data) {
  return api.put(`/hosts/${id}/`, data)
}

// 删除主机
export function deleteHost(id) {
  return api.delete(`/hosts/${id}/`)
}

// 采集主机硬件信息
export function collectHardware(id) {
  return api.post(`/hosts/${id}/collect_hardware/`)
}