import api from './auth'

// 获取出口IP序列号列表
export function getOutIpSNs(params) {
  return api.get('/outipsn/', { params })
}

// 获取出口IP序列号详情
export function getOutIpSNDetail(id) {
  return api.get(`/outipsn/${id}/`)
}

// 创建出口IP序列号
export function createOutIpSN(data) {
  return api.post('/outipsn/', data)
}

// 更新出口IP序列号
export function updateOutIpSN(id, data) {
  return api.put(`/outipsn/${id}/`, data)
}

// 删除出口IP序列号
export function deleteOutIpSN(id) {
  return api.delete(`/outipsn/${id}/`)
}

export default {
  getOutIpSNs,
  getOutIpSNDetail,
  createOutIpSN,
  updateOutIpSN,
  deleteOutIpSN,
}