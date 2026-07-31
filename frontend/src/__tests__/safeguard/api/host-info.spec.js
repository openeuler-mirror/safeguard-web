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
})
