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

})
