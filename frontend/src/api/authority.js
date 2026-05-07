import api from './auth'

const BASE_URL = '/authority'

// 获取角色列表
export function getAuthorities() {
  return api.get(`${BASE_URL}/authorities/`)
}

// 获取角色详情
export function getAuthority(id) {
  return api.get(`${BASE_URL}/authorities/${id}/`)
}

// 创建角色
export function createAuthority(data) {
  return api.post(`${BASE_URL}/authorities/`, data)
}

// 更新角色
export function updateAuthority(id, data) {
  return api.put(`${BASE_URL}/authorities/${id}/`, data)
}

// 删除角色
export function deleteAuthority(id) {
  return api.delete(`${BASE_URL}/authorities/${id}/`)
}

// 复制角色
export function copyAuthority(id) {
  return api.post(`${BASE_URL}/authorities/${id}/copy/`)
}

// 获取角色菜单
export function getAuthorityMenus(id) {
  return api.get(`${BASE_URL}/authorities/${id}/menus/`)
}

// 设置角色菜单
export function setAuthorityMenus(id, menuIds) {
  return api.put(`${BASE_URL}/authorities/${id}/menus/`, { menu_ids: menuIds })
}

// 获取角色按钮权限
export function getAuthorityBtns(id) {
  return api.get(`${BASE_URL}/authorities/${id}/btns/`)
}

// 设置角色按钮权限
export function setAuthorityBtns(id, buttons) {
  return api.put(`${BASE_URL}/authorities/${id}/btns/`, { buttons })
}

// 获取菜单列表
export function getMenus() {
  return api.get(`${BASE_URL}/menus/`)
}

// 获取菜单树
export function getMenuTree() {
  return api.get(`${BASE_URL}/menus/tree/`)
}

// 创建菜单
export function createMenu(data) {
  return api.post(`${BASE_URL}/menus/`, data)
}

// 更新菜单
export function updateMenu(id, data) {
  return api.put(`${BASE_URL}/menus/${id}/`, data)
}

// 删除菜单
export function deleteMenu(id) {
  return api.delete(`${BASE_URL}/menus/${id}/`)
}
