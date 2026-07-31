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
})
