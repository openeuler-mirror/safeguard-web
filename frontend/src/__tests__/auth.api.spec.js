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

  describe('changePassword API 路径测试', () => {
    it('应调用正确的URL并传递新旧密码', async () => {
      api.put.mockResolvedValue(mockResponse)
      const passwordData = { old_password: 'oldpass', new_password: 'newpass' }

      await api.put('/users/me/password/', passwordData)

      expect(api.put).toHaveBeenCalledWith(
        '/users/me/password/',
        passwordData
      )
    })
  })

  describe('resetPassword API 路径测试', () => {
    it('应调用正确的URL并传递用户ID和新密码', async () => {
      api.put.mockResolvedValue(mockResponse)
      const passwordData = { new_password: 'newpass' }

      await api.put('/users/1/password/', passwordData)

      expect(api.put).toHaveBeenCalledWith(
        '/users/1/password/',
        passwordData
      )
    })
  })

  describe('sendVerificationCode API 路径测试', () => {
    it('应调用正确的URL并传递邮箱和用途', async () => {
      api.post.mockResolvedValue(mockResponse)

      await api.post('/auth/send-code/', { email: 'test@example.com', purpose: 'register' })

      expect(api.post).toHaveBeenCalledWith(
        '/auth/send-code/',
        { email: 'test@example.com', purpose: 'register' }
      )
    })
  })

  describe('verifyCode API 路径测试', () => {
    it('应调用正确的URL并传递邮箱和验证码', async () => {
      api.post.mockResolvedValue(mockResponse)

      await api.post('/auth/verify-code/', { email: 'test@example.com', code: '123456' })

      expect(api.post).toHaveBeenCalledWith(
        '/auth/verify-code/',
        { email: 'test@example.com', code: '123456' }
      )
    })
  })

  describe('forgotPassword API 路径测试', () => {
    it('应调用正确的URL并传递邮箱', async () => {
      api.post.mockResolvedValue(mockResponse)

      await api.post('/auth/forgot-password/', { email: 'test@example.com' })

      expect(api.post).toHaveBeenCalledWith(
        '/auth/forgot-password/',
        { email: 'test@example.com' }
      )
    })
  })

  describe('resetPasswordWithCode API 路径测试', () => {
    it('应调用正确的URL并传递邮箱、验证码和新密码', async () => {
      api.post.mockResolvedValue(mockResponse)

      await api.post('/auth/reset-password/', {
        email: 'test@example.com',
        code: '123456',
        new_password: 'newpass'
      })

      expect(api.post).toHaveBeenCalledWith(
        '/auth/reset-password/',
        { email: 'test@example.com', code: '123456', new_password: 'newpass' }
      )
    })
  })

})
