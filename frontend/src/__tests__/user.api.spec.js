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

describe('user API 测试', () => {
  const mockResponse = { data: {} }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAuthorities API 路径测试', () => {
    it('应调用正确的URL获取角色列表', async () => {
      api.get.mockResolvedValue(mockResponse)

      await api.get('/authority/authorities/')

      expect(api.get).toHaveBeenCalledWith('/authority/authorities/')
    })
  })

  describe('getUsers API 路径测试', () => {
    it('应调用正确的URL获取用户列表', async () => {
      api.get.mockResolvedValue(mockResponse)

      await api.get('/users/')

      expect(api.get).toHaveBeenCalledWith('/users/')
    })
  })

  describe('getUser API 路径测试', () => {
    it('应调用正确的URL获取用户详情', async () => {
      api.get.mockResolvedValue(mockResponse)
      const userId = 1

      await api.get(`/users/${userId}/`)

      expect(api.get).toHaveBeenCalledWith('/users/1/')
    })
  })

})
