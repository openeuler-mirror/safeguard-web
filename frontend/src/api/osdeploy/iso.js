import api from './auth'

// 获取ISO文件列表
export function getISOFiles(params) {
  return api.get('/isos/', { params })
}

// 获取ISO文件详情
export function getISOFileDetail(id) {
  return api.get(`/isos/${id}/`)
}

// 创建ISO文件记录
export function createISOFile(data) {
  return api.post('/isos/', data)
}

// 更新ISO文件
export function updateISOFile(id, data) {
  return api.put(`/isos/${id}/`, data)
}

// 删除ISO文件
export function deleteISOFile(id) {
  return api.delete(`/isos/${id}/`)
}

// 上传ISO文件
export function uploadISOFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/isos/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export default {
  getISOFiles,
  getISOFileDetail,
  createISOFile,
  updateISOFile,
  deleteISOFile,
  uploadISOFile,
}