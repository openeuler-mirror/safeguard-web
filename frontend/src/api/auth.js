import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
})

// 请求拦截器：添加JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：处理token过期
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE}/auth/refresh/`, {
            refresh: refreshToken
          })
          const { access } = res.data
          localStorage.setItem('access_token', access)
          originalRequest.headers.Authorization = `Bearer ${access}`
          return api(originalRequest)
        } catch (refreshError) {
          // refresh token失效，清除登录状态
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      }
    }
    return Promise.reject(error)
  }
)

// 登录
export function login(username, password) {
  return api.post('/auth/login/', { username, password })
}

// 登出
export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

// 获取当前用户信息
export function getMe() {
  return api.get('/users/me/')
}

// 获取用户列表
export function getUsers() {
  return api.get('/users/')
}

// 创建用户
export function createUser(data) {
  return api.put('/auth/register/', data)
}

// 更新用户
export function updateUser(id, data) {
  return api.put(`/users/${id}/`, data)
}

// 删除用户
export function deleteUser(id) {
  return api.delete(`/users/${id}/`)
}

// 修改密码（自己）
export function changePassword(oldPassword, newPassword) {
  return api.put('/users/me/password/', { old_password: oldPassword, new_password: newPassword })
}

// 重置密码（管理员）
export function resetPassword(userId, newPassword) {
  return api.put(`/users/${userId}/password/`, { new_password: newPassword })
}

// 更新个人信息
export function updateMe(data) {
  return api.put('/users/me/', data)
}

export default api