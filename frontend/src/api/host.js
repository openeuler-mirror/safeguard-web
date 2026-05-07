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