import { describe, it, expect, vi, beforeEach, afterEach, fakeTimers } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostMonitor from '@/views/hosts/HostMonitor.vue'
import { getHost } from '@/api/host'
import { getRealTimeMonitor } from '@/api/safeguard/monitor'
import MetricCard from '@/components/safeguard/MetricCard.vue'
import SimpleLineChart from '@/components/safeguard/SimpleLineChart.vue'

vi.mock('@/api/host')
vi.mock('@/api/safeguard/monitor')

const mockPush = vi.fn()

describe('HostMonitor 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockMonitorData = {
    cpu_percent: 45.5,
    mem_percent: 60.2,
    net_in: 1024,
    net_out: 2048,
    load_1: 1.25
  }

  let wrapper
  let clock

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    clock = fakeTimers()

    getHost.mockResolvedValue(mockHost)
    getRealTimeMonitor.mockResolvedValue(mockMonitorData)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    clock.clear()
  })

  const createWrapper = () => {
    return mount(HostMonitor, {
      global: {
        mocks: {
          $route: {
            params: { id: mockHostId }
          },
          $router: {
            push: mockPush
          }
        },
        stubs: {
          MetricCard,
          SimpleLineChart
        }
      }
    })
  }

  describe('页面加载时显示 loading 状态', () => {
    it('初始应显示loading状态', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('.loading').exists()).toBe(true)
    })

    it('数据加载完成后应隐藏loading状态', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.find('.loading').exists()).toBe(false)
    })
  })

  describe('从路由参数获取 hostId', () => {
    it('应正确从路由参数获取hostId', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.hostId).toBe(mockHostId)
    })
  })

  describe('加载实时监控数据', () => {
    it('应调用getHost和getRealTimeMonitor API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHost).toHaveBeenCalledWith(mockHostId)
      expect(getRealTimeMonitor).toHaveBeenCalledWith(mockHostId)
    })

    it('应正确设置currentMetrics数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.currentMetrics).toEqual(mockMonitorData)
    })

    it('应将数据添加到monitorHistory', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.monitorHistory.length).toBe(1)
      expect(wrapper.vm.monitorHistory[0]).toEqual(mockMonitorData)
    })
  })

})
