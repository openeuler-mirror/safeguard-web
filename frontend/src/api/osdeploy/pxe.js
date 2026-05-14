import api from './auth'

// 获取PXE服务器列表
export function getPXEServers(params) {
  return api.get('/pxe-servers/', { params })
}

// 获取PXE服务器详情
export function getPXEServerDetail(id) {
  return api.get(`/pxe-servers/${id}/`)
}

// 创建PXE服务器
export function createPXEServer(data) {
  return api.post('/pxe-servers/', data)
}

// 更新PXE服务器
export function updatePXEServer(id, data) {
  return api.put(`/pxe-servers/${id}/`, data)
}

// 删除PXE服务器
export function deletePXEServer(id) {
  return api.delete(`/pxe-servers/${id}/`)
}

export default {
  getPXEServers,
  getPXEServerDetail,
  createPXEServer,
  updatePXEServer,
  deletePXEServer,
}