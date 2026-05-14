import api from './auth'

// 获取Kickstart模板列表
export function getKickstarts(params) {
  return api.get('/kickstarts/', { params })
}

// 获取Kickstart模板详情
export function getKickstartDetail(id) {
  return api.get(`/kickstarts/${id}/`)
}

// 创建Kickstart模板
export function createKickstart(data) {
  return api.post('/kickstarts/', data)
}

// 更新Kickstart模板
export function updateKickstart(id, data) {
  return api.put(`/kickstarts/${id}/`, data)
}

// 删除Kickstart模板
export function deleteKickstart(id) {
  return api.delete(`/kickstarts/${id}/`)
}

// 验证Kickstart模板语法
export function validateKickstart(id) {
  return api.post(`/kickstarts/${id}/validate/`)
}

// 预览生成的Kickstart文件内容
export function previewKickstart(id, vars) {
  return api.post(`/kickstarts/${id}/preview/`, { vars })
}

export default {
  getKickstarts,
  getKickstartDetail,
  createKickstart,
  updateKickstart,
  deleteKickstart,
  validateKickstart,
  previewKickstart,
}