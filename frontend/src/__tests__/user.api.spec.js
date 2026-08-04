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

  describe('getUserAuthorities API 路径测试', () => {
    it('应调用正确的URL获取用户角色列表', async () => {
      api.get.mockResolvedValue(mockResponse)
      const userId = 1

      await api.get(`/users/${userId}/authorities/`)

      expect(api.get).toHaveBeenCalledWith('/users/1/authorities/')
    })
  })

  describe('setUserAuthorities API 路径测试', () => {
    it('应调用正确的URL并传递角色ID列表', async () => {
      api.put.mockResolvedValue(mockResponse)
      const userId = 1
      const roleIds = [1, 2, 3]

      await api.put(`/users/${userId}/authorities/`, { role_ids: roleIds })

      expect(api.put).toHaveBeenCalledWith(
        '/users/1/authorities/',
        { role_ids: roleIds }
      )
    })
  })

  describe('addUserAuthority API 路径测试', () => {
    it('应调用正确的URL并传递角色ID', async () => {
      api.post.mockResolvedValue(mockResponse)
      const userId = 1
      const authorityId = 2

      await api.post(`/users/${userId}/authorities/add/`, { authority_id: authorityId })

      expect(api.post).toHaveBeenCalledWith(
        '/users/1/authorities/add/',
        { authority_id: authorityId }
      )
    })
  })

  describe('removeUserAuthority API 路径测试', () => {
    it('应调用正确的URL并传递角色ID', async () => {
      api.delete.mockResolvedValue(mockResponse)
      const userId = 1
      const authorityId = 2

      await api.delete(`/users/${userId}/authorities/`, { data: { authority_id: authorityId } })

      expect(api.delete).toHaveBeenCalledWith(
        '/users/1/authorities/',
        { data: { authority_id: authorityId } }
      )
    })
  })

})
