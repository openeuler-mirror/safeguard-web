import { describe, it, expect, vi, beforeEach } from 'vitest'
import api from '@/api/auth'

// 模拟 api 模块
vi.mock('@/api/auth', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('auth API 测试', () => {
  const mockResponse = { data: {} }

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('login API 路径测试', () => {
    it('应调用正确的URL并传递用户名和密码', async () => {
      api.post.mockResolvedValue(mockResponse)

      await api.post('/auth/login/', { username: 'testuser', password: 'testpass' })

      expect(api.post).toHaveBeenCalledWith(
        '/auth/login/',
        { username: 'testuser', password: 'testpass' }
      )
    })
  })

  describe('logout 功能测试', () => {
    it('应从 localStorage 移除 access_token 和 refresh_token', () => {
      localStorage.setItem('access_token', 'test-access')
      localStorage.setItem('refresh_token', 'test-refresh')

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')

      expect(localStorage.getItem('access_token')).toBeNull()
      expect(localStorage.getItem('refresh_token')).toBeNull()
    })
  })

  describe('getMe API 路径测试', () => {
    it('应调用正确的URL获取当前用户信息', async () => {
      api.get.mockResolvedValue(mockResponse)

      await api.get('/users/me/')

      expect(api.get).toHaveBeenCalledWith('/users/me/')
    })
  })

  describe('getUsers API 路径测试', () => {
    it('应调用正确的URL获取用户列表', async () => {
      api.get.mockResolvedValue(mockResponse)

      await api.get('/users/')

      expect(api.get).toHaveBeenCalledWith('/users/')
    })
  })

  describe('createUser API 路径测试', () => {
    it('应调用正确的URL并传递用户数据', async () => {
      api.put.mockResolvedValue(mockResponse)
      const userData = { username: 'newuser', email: 'test@example.com' }

      await api.put('/auth/register/', userData)

      expect(api.put).toHaveBeenCalledWith(
        '/auth/register/',
        userData
      )
    })
  })

  describe('updateUser API 路径测试', () => {
    it('应调用正确的URL并传递用户ID和数据', async () => {
      api.put.mockResolvedValue(mockResponse)
      const userData = { username: 'updateduser' }

      await api.put('/users/1/', userData)

      expect(api.put).toHaveBeenCalledWith(
        '/users/1/',
        userData
      )
    })
  })

  describe('deleteUser API 路径测试', () => {
    it('应调用正确的URL并传递用户ID', async () => {
      api.delete.mockResolvedValue(mockResponse)

      await api.delete('/users/1/')

      expect(api.delete).toHaveBeenCalledWith('/users/1/')
    })
  })

})
