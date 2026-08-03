import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import SystemLogs from '@/views/hosts/SystemLogs.vue'
import { getSystemLogs } from '@/api/safeguard/host-info'
import { getHost } from '@/api/host'

vi.mock('@/api/safeguard/host-info')
vi.mock('@/api/host')

const mockPush = vi.fn()

describe('SystemLogs 页面测试', () => {
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockLogsData = { logs: 'Jan  1 10:00:00 test-host kernel: [0.000000] Linux version 5.4.0\nJan  1 10:00:01 test-host sshd[1234]: Accepted publickey' }

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()

    getHost.mockResolvedValue(mockHost)
    getSystemLogs.mockResolvedValue(mockLogsData)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(SystemLogs, {
      global: {
        mocks: {
          $router: {
            push: mockPush
          },
          $route: {
            params: { id: 1 }
          }
        }
      }
    })
  }

  describe('页面加载时显示 loading 状态', () => {
    it('初始 loading 应为 true', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(true)
    })

    it('数据加载完成后应隐藏 loading 状态', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('加载主机和系统日志', () => {
    it('应调用 getHost 和 getSystemLogs API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHost).toHaveBeenCalledWith(1)
      expect(getSystemLogs).toHaveBeenCalledWith(1, {})
    })

    it('应正确设置 host 和 logs 数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.host).toEqual(mockHost)
      expect(wrapper.vm.logs).toEqual(mockLogsData.logs)
    })

    it('没有日志数据时应显示默认值', async () => {
      getSystemLogs.mockResolvedValue({})

      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.logs).toEqual('(暂无日志)')
    })
  })

  describe('日志级别筛选', () => {
    it('改变 logLevel 时应重新加载日志', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.setData({ logLevel: 'error' })
      await wrapper.vm.loadLogs()

      expect(getSystemLogs).toHaveBeenCalledWith(1, { level: 'error' })
    })

    it('logLevel 为空时不传该参数', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.setData({ logLevel: '' })
      await wrapper.vm.loadLogs()

      expect(getSystemLogs).toHaveBeenCalledWith(1, {})
    })
  })

  describe('API 失败时显示错误信息', () => {
    it('getHost 失败时应显示错误', async () => {
      getHost.mockRejectedValue(new Error('加载数据失败'))

      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.error).toBe('加载数据失败')
    })

    it('getSystemLogs 失败时应显示错误', async () => {
      getSystemLogs.mockRejectedValue(new Error('获取日志失败'))

      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.error).toBe('获取日志失败')
    })
  })

})
