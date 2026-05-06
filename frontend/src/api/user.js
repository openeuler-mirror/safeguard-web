import api from './auth'

// 获取所有角色列表
export function getAuthorities() {
  return api.get('/authorities/')
}

// 获取用户列表
export function getUsers() {
  return api.get('/users/')
}

// 获取用户详情
export function getUser(id) {
  return api.get(`/users/${id}/`)
}

// 获取用户角色列表
export function getUserAuthorities(userId) {
  return api.get(`/users/${userId}/authorities/`)
}

// 设置用户角色（覆盖式）
export function setUserAuthorities(userId, roleIds) {
  return api.put(`/users/${userId}/authorities/`, { role_ids: roleIds })
}

// 添加用户角色
export function addUserAuthority(userId, authorityId) {
  return api.post(`/users/${userId}/authorities/add/`, { authority_id: authorityId })
}

// 移除用户角色
export function removeUserAuthority(userId, authorityId) {
  return api.delete(`/users/${userId}/authorities/`, { data: { authority_id: authorityId } })
}
