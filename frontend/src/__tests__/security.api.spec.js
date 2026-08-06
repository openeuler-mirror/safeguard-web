import { describe, it, expect, vi, beforeEach } from 'vitest'
import api from '@/api/auth'
import {
  getSafeguards,
  getSafeguard,
  createSafeguard,
  updateSafeguard,
  deleteSafeguard,
  deploySafeguard,
  rollbackSafeguard,
  getSafeguardStatus
} from '@/api/security'

// 模拟 api 模块
vi.mock('@/api/auth', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('security API 测试', () => {
  const mockResponse = { data: {} }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getSafeguards API 路径测试', () => {
    it('应调用正确的URL获取安全防护列表', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getSafeguards()

      expect(api.get).toHaveBeenCalledWith('/safeguards/', { params: undefined })
    })

    it('应支持传递查询参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = { page: 1, status: 'active' }

      await getSafeguards(params)

      expect(api.get).toHaveBeenCalledWith('/safeguards/', { params })
    })
  })

  describe('getSafeguard API 路径测试', () => {
    it('应调用正确的URL获取安全防护详情', async () => {
      api.get.mockResolvedValue(mockResponse)
      const safeguardId = 1

      await getSafeguard(safeguardId)

      expect(api.get).toHaveBeenCalledWith('/safeguards/1/')
    })
  })

  describe('createSafeguard API 路径测试', () => {
    it('应调用正确的URL并传递数据创建安全防护', async () => {
      api.post.mockResolvedValue(mockResponse)
      const data = { name: 'test-safeguard', type: 'firewall' }

      await createSafeguard(data)

      expect(api.post).toHaveBeenCalledWith('/safeguards/', data)
    })
  })

  describe('updateSafeguard API 路径测试', () => {
    it('应调用正确的URL并传递数据更新安全防护', async () => {
      api.put.mockResolvedValue(mockResponse)
      const safeguardId = 1
      const data = { name: 'updated-safeguard' }

      await updateSafeguard(safeguardId, data)

      expect(api.put).toHaveBeenCalledWith('/safeguards/1/', data)
    })
  })

  describe('deleteSafeguard API 路径测试', () => {
    it('应调用正确的URL删除安全防护', async () => {
      api.delete.mockResolvedValue(mockResponse)
      const safeguardId = 1

      await deleteSafeguard(safeguardId)

      expect(api.delete).toHaveBeenCalledWith('/safeguards/1/')
    })
  })

})
