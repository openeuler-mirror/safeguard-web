import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  getRealTimeMonitor,
  getMonitorHistory,
  collectMonitor
} from '@/api/safeguard/monitor'
import api from '@/api/auth'

// 模拟 api 模块
vi.mock('@/api/auth', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

describe('monitor API 测试', () => {
  const mockHostId = 1
  const mockResponse = { data: {} }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getRealTimeMonitor 正确调用 API 路径', () => {
    it('应调用正确的URL并传递host_id参数', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getRealTimeMonitor(mockHostId)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/monitor/real-time/',
        { params: { host_id: mockHostId } }
      )
    })
  })

  describe('getMonitorHistory 正确传递分页参数', () => {
    it('应调用正确的URL并传递分页参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = { page: 1, page_size: 20 }

      await getMonitorHistory(mockHostId, params)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/monitor/history/',
        { params: { host_id: mockHostId, ...params } }
      )
    })
  })

  describe('getMonitorHistory 正确传递时间范围参数', () => {
    it('应调用正确的URL并传递时间范围参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = { start_time: '2024-01-01', end_time: '2024-01-02' }

      await getMonitorHistory(mockHostId, params)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/monitor/history/',
        { params: { host_id: mockHostId, ...params } }
      )
    })

    it('应正确传递所有类型的参数组合', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = {
        page: 1,
        page_size: 20,
        start_time: '2024-01-01',
        end_time: '2024-01-02',
        metric: 'cpu'
      }

      await getMonitorHistory(mockHostId, params)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/monitor/history/',
        { params: { host_id: mockHostId, ...params } }
      )
    })
  })

  describe('collectMonitor 正确调用 API 路径', () => {
    it('应调用正确的URL并传递host_id参数', async () => {
      api.post.mockResolvedValue(mockResponse)

      await collectMonitor(mockHostId)

      expect(api.post).toHaveBeenCalledWith(
        '/safeguard/monitor/collect/',
        { host_id: mockHostId }
      )
    })
  })

  describe('正确处理 API 错误响应', () => {
    it('getRealTimeMonitor 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getRealTimeMonitor(mockHostId)).rejects.toThrow('API Error')
    })

    it('getMonitorHistory 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)
      const params = { page: 1 }

      await expect(getMonitorHistory(mockHostId, params)).rejects.toThrow('API Error')
    })

    it('collectMonitor 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.post.mockRejectedValue(mockError)

      await expect(collectMonitor(mockHostId)).rejects.toThrow('API Error')
    })
  })
})
