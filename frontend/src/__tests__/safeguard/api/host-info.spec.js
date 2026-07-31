import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  getSystemInfo,
  getPortsInfo,
  getProcessesInfo,
  getServicesInfo,
  getAccountsInfo,
  controlService,
  getServiceLogs,
  killProcess,
  getSystemLogs
} from '@/api/safeguard/host-info'
import api from '@/api/auth'

// 模拟 api 模块
vi.mock('@/api/auth', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

describe('host-info API 测试', () => {
  const mockHostId = 1
  const mockResponse = { data: {} }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getSystemInfo 正确调用 API 路径', () => {
    it('应调用正确的URL并传递host_id参数', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getSystemInfo(mockHostId)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/host-info/system-info/',
        { params: { host_id: mockHostId } }
      )
    })
  })

  describe('getPortsInfo 正确调用 API 路径', () => {
    it('应调用正确的URL并传递host_id参数', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getPortsInfo(mockHostId)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/host-info/ports-info/',
        { params: { host_id: mockHostId } }
      )
    })
  })

  describe('getProcessesInfo 正确调用 API 路径', () => {
    it('应调用正确的URL并传递host_id参数', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getProcessesInfo(mockHostId)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/host-info/processes-info/',
        { params: { host_id: mockHostId } }
      )
    })
  })

  describe('getServicesInfo 正确调用 API 路径', () => {
    it('应调用正确的URL并传递host_id参数', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getServicesInfo(mockHostId)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/host-info/services-info/',
        { params: { host_id: mockHostId } }
      )
    })
  })

  describe('getAccountsInfo 正确调用 API 路径', () => {
    it('应调用正确的URL并传递host_id参数', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getAccountsInfo(mockHostId)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/host-info/accounts-info/',
        { params: { host_id: mockHostId } }
      )
    })
  })

  describe('controlService 正确传递参数', () => {
    it('应调用正确的URL并传递完整的参数', async () => {
      api.post.mockResolvedValue(mockResponse)
      const controlData = { service_name: 'nginx', action: 'start' }

      await controlService(mockHostId, controlData)

      expect(api.post).toHaveBeenCalledWith(
        '/safeguard/host-info/service-control/',
        { host_id: mockHostId, ...controlData }
      )
    })
  })

  describe('getServiceLogs 正确传递参数', () => {
    it('应调用正确的URL并传递服务名称和行数参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const serviceName = 'nginx'
      const lines = 200

      await getServiceLogs(mockHostId, serviceName, lines)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/host-info/service-logs/',
        { params: { host_id: mockHostId, service_name: serviceName, lines } }
      )
    })

    it('应使用默认的lines参数值', async () => {
      api.get.mockResolvedValue(mockResponse)
      const serviceName = 'nginx'

      await getServiceLogs(mockHostId, serviceName)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/host-info/service-logs/',
        { params: { host_id: mockHostId, service_name: serviceName, lines: 100 } }
      )
    })
  })

  describe('killProcess 正确传递参数', () => {
    it('应调用正确的URL并传递pid参数', async () => {
      api.post.mockResolvedValue(mockResponse)
      const pid = 1234

      await killProcess(mockHostId, pid)

      expect(api.post).toHaveBeenCalledWith(
        '/safeguard/host-info/kill-process/',
        { host_id: mockHostId, pid, force: false }
      )
    })

    it('应正确传递force参数', async () => {
      api.post.mockResolvedValue(mockResponse)
      const pid = 1234

      await killProcess(mockHostId, pid, true)

      expect(api.post).toHaveBeenCalledWith(
        '/safeguard/host-info/kill-process/',
        { host_id: mockHostId, pid, force: true }
      )
    })
  })

  describe('正确处理 API 错误响应', () => {
    it('getSystemInfo 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getSystemInfo(mockHostId)).rejects.toThrow('API Error')
    })

    it('controlService 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.post.mockRejectedValue(mockError)
      const controlData = { service_name: 'nginx', action: 'start' }

      await expect(controlService(mockHostId, controlData)).rejects.toThrow('API Error')
    })
  })

  describe('getSystemLogs 正确调用 API 路径', () => {
    it('应调用正确的URL并传递host_id和额外参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const extraParams = { level: 'error', limit: 50 }

      await getSystemLogs(mockHostId, extraParams)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/host-info/system-logs/',
        { params: { host_id: mockHostId, ...extraParams } }
      )
    })

    it('应只传递host_id当没有额外参数时', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getSystemLogs(mockHostId)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/host-info/system-logs/',
        { params: { host_id: mockHostId } }
      )
    })
  })
})
