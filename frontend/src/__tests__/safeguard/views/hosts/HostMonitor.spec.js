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

  describe('渲染 CPU 使用率折线图', () => {
    it('应渲染SimpleLineChart组件', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const charts = wrapper.findAllComponents(SimpleLineChart)
      expect(charts.length).toBe(4)
    })

    it('第一个图表应为CPU使用率图表', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const chartCards = wrapper.findAll('.chart-card')
      expect(chartCards[0].text()).toContain('CPU 使用率')
    })
  })

  describe('渲染内存使用率折线图', () => {
    it('第二个图表应为内存使用率图表', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const chartCards = wrapper.findAll('.chart-card')
      expect(chartCards[1].text()).toContain('内存使用率')
    })
  })

  describe('渲染网络流量图表', () => {
    it('第三个图表应为网络流量图表', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const chartCards = wrapper.findAll('.chart-card')
      expect(chartCards[2].text()).toContain('网络流量')
    })
  })

  describe('渲染系统负载图表', () => {
    it('第四个图表应为系统负载图表', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const chartCards = wrapper.findAll('.chart-card')
      expect(chartCards[3].text()).toContain('系统负载')
    })
  })

  describe('显示系统负载数值', () => {
    it('应渲染4个MetricCard组件', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const metricCards = wrapper.findAllComponents(MetricCard)
      expect(metricCards.length).toBe(4)
    })

    it('MetricCard应包含正确的CPU数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const metricCards = wrapper.findAllComponents(MetricCard)
      expect(metricCards[0].props('label')).toBe('CPU 使用率')
      expect(metricCards[0].props('value')).toBe(45.5)
      expect(metricCards[0].props('unit')).toBe('%')
    })

    it('MetricCard应包含正确的内存数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const metricCards = wrapper.findAllComponents(MetricCard)
      expect(metricCards[1].props('label')).toBe('内存使用率')
      expect(metricCards[1].props('value')).toBe(60.2)
      expect(metricCards[1].props('unit')).toBe('%')
    })

    it('MetricCard应包含正确的网络入流量数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const metricCards = wrapper.findAllComponents(MetricCard)
      expect(metricCards[2].props('label')).toBe('网络入流量')
      expect(metricCards[2].props('value')).toBe(1024)
      expect(metricCards[2].props('unit')).toBe('KB/s')
    })

    it('MetricCard应包含正确的网络出流量数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const metricCards = wrapper.findAllComponents(MetricCard)
      expect(metricCards[3].props('label')).toBe('网络出流量')
      expect(metricCards[3].props('value')).toBe(2048)
      expect(metricCards[3].props('unit')).toBe('KB/s')
    })
  })

})
