import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  getFileMonitorRules,
  getFileMonitorRule,
  createFileMonitorRule,
  updateFileMonitorRule,
  deleteFileMonitorRule,
  getFileMonitorEvents,
  collectFileMonitorEvents
} from '@/api/safeguard/file-monitor'
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

describe('file-monitor API 测试', () => {
  const mockRuleId = 1
  const mockHostId = 1
  const mockResponse = { data: {} }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getFileMonitorRules 正确调用 API 路径', () => {
    it('应调用正确的URL', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getFileMonitorRules()

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/file-monitor/rules/',
        { params: undefined }
      )
    })
  })

  describe('getFileMonitorRules 正确传递主机过滤参数', () => {
    it('应调用正确的URL并传递主机过滤参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = { host_id: mockHostId, status: 'active' }

      await getFileMonitorRules(params)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/file-monitor/rules/',
        { params }
      )
    })
  })

  describe('getFileMonitorRule 正确传递规则ID', () => {
    it('应调用正确的URL并包含规则ID', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getFileMonitorRule(mockRuleId)

      expect(api.get).toHaveBeenCalledWith(
        `/safeguard/file-monitor/rules/${mockRuleId}/`
      )
    })
  })

  describe('createFileMonitorRule 正确传递规则数据', () => {
    it('应调用正确的URL并传递规则数据', async () => {
      api.post.mockResolvedValue(mockResponse)
      const ruleData = {
        host_id: mockHostId,
        path: '/etc',
        monitor_type: 'all',
        enabled: true
      }

      await createFileMonitorRule(ruleData)

      expect(api.post).toHaveBeenCalledWith(
        '/safeguard/file-monitor/rules/',
        ruleData
      )
    })
  })

  describe('updateFileMonitorRule 正确传递规则ID和数据', () => {
    it('应调用正确的URL并传递规则ID和数据', async () => {
      api.put.mockResolvedValue(mockResponse)
      const ruleData = { path: '/etc/updated', enabled: false }

      await updateFileMonitorRule(mockRuleId, ruleData)

      expect(api.put).toHaveBeenCalledWith(
        `/safeguard/file-monitor/rules/${mockRuleId}/`,
        ruleData
      )
    })
  })

  describe('deleteFileMonitorRule 正确传递规则ID', () => {
    it('应调用正确的URL并包含规则ID', async () => {
      api.delete.mockResolvedValue(mockResponse)

      await deleteFileMonitorRule(mockRuleId)

      expect(api.delete).toHaveBeenCalledWith(
        `/safeguard/file-monitor/rules/${mockRuleId}/`
      )
    })
  })

  describe('getFileMonitorEvents 正确调用 API 路径', () => {
    it('应调用正确的URL', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getFileMonitorEvents()

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/file-monitor/events/',
        { params: undefined }
      )
    })
  })

  describe('getFileMonitorEvents 正确传递时间范围参数', () => {
    it('应调用正确的URL并传递时间范围参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = {
        host_id: mockHostId,
        start_time: '2024-01-01',
        end_time: '2024-01-02',
        event_type: 'modify',
        page: 1
      }

      await getFileMonitorEvents(params)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/file-monitor/events/',
        { params }
      )
    })
  })
})
