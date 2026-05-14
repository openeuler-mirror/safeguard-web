import api from './auth'

// 获取仓库列表
export function getRepos(params) {
  return api.get('/repos/', { params })
}

// 获取仓库详情
export function getRepoDetail(id) {
  return api.get(`/repos/${id}/`)
}

// 创建仓库
export function createRepo(data) {
  return api.post('/repos/', data)
}

// 更新仓库
export function updateRepo(id, data) {
  return api.put(`/repos/${id}/`, data)
}

// 删除仓库
export function deleteRepo(id) {
  return api.delete(`/repos/${id}/`)
}

// 同步仓库
export function syncRepo(id) {
  return api.post(`/repos/${id}/sync/`)
}

export default {
  getRepos,
  getRepoDetail,
  createRepo,
  updateRepo,
  deleteRepo,
  syncRepo,
}