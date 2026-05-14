import api from './auth'

// 获取白名单列表
export function getWhiteList(params) {
  return api.get('/whitelist/', { params })
}

// 获取白名单详情
export function getWhiteListDetail(id) {
  return api.get(`/whitelist/${id}/`)
}

// 创建白名单
export function createWhiteList(data) {
  return api.post('/whitelist/', data)
}

// 更新白名单
export function updateWhiteList(id, data) {
  return api.put(`/whitelist/${id}/`, data)
}

// 删除白名单
export function deleteWhiteList(id) {
  return api.delete(`/whitelist/${id}/`)
}

// 批量导入白名单
export function importWhiteList(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/whitelist/import/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// 导出白名单
export function exportWhiteList(params) {
  return api.get('/whitelist/export/', { params })
}

export default {
  getWhiteList,
  getWhiteListDetail,
  createWhiteList,
  updateWhiteList,
  deleteWhiteList,
  importWhiteList,
  exportWhiteList,
}