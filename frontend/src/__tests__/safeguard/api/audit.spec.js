import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  getAuditLogs,
  getAuditLog,
  getAuditStats
} from '@/api/safeguard/audit'
import api from '@/api/auth'

// 模拟 api 模块
vi.mock('@/api/auth', () => ({
  default: {
    get: vi.fn()
  }
}))

describe('audit API 测试', () => {
  const mockLogId = 1
  const mockResponse = { data: {} }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAuditLogs 正确调用 API 路径', () => {
    it('应调用正确的URL', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getAuditLogs()

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/audit/logs/',
        { params: undefined }
      )
    })
  })

  describe('getAuditLogs 正确传递用户过滤参数', () => {
    it('应调用正确的URL并传递用户过滤参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = { user: 'admin', page: 1 }

      await getAuditLogs(params)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/audit/logs/',
        { params }
      )
    })
  })

  describe('getAuditLogs 正确传递操作类型过滤参数', () => {
    it('应调用正确的URL并传递操作类型过滤参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = { action_type: 'create', page: 1 }

      await getAuditLogs(params)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/audit/logs/',
        { params }
      )
    })
  })

  describe('getAuditLogs 正确传递时间范围参数', () => {
    it('应调用正确的URL并传递时间范围参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = {
        start_time: '2024-01-01',
        end_time: '2024-01-02',
        page: 1
      }

      await getAuditLogs(params)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/audit/logs/',
        { params }
      )
    })
  })

  describe('getAuditLogs 正确传递所有类型的参数组合', () => {
    it('应调用正确的URL并传递所有过滤参数组合', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = {
        user: 'admin',
        action_type: 'create',
        resource_type: 'policy',
        start_time: '2024-01-01',
        end_time: '2024-01-02',
        status: 'success',
        page: 1,
        page_size: 20
      }

      await getAuditLogs(params)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/audit/logs/',
        { params }
      )
    })
  })

  describe('getAuditLog 正确传递日志ID', () => {
    it('应调用正确的URL并包含日志ID', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getAuditLog(mockLogId)

      expect(api.get).toHaveBeenCalledWith(
        `/safeguard/audit/logs/${mockLogId}/`
      )
    })
  })

  describe('getAuditStats 正确调用统计接口', () => {
    it('应调用正确的统计URL', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getAuditStats()

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/audit/stats/',
        { params: undefined }
      )
    })
  })

  describe('getAuditStats 正确传递时间范围参数', () => {
    it('应调用正确的URL并传递时间范围参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = {
        start_time: '2024-01-01',
        end_time: '2024-01-02'
      }

      await getAuditStats(params)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/audit/stats/',
        { params }
      )
    })
  })

  describe('正确处理 API 错误响应', () => {
    it('getAuditLogs 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getAuditLogs()).rejects.toThrow('API Error')
    })

    it('getAuditLog 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getAuditLog(mockLogId)).rejects.toThrow('API Error')
    })

    it('getAuditStats 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getAuditStats()).rejects.toThrow('API Error')
    })
  })
})
