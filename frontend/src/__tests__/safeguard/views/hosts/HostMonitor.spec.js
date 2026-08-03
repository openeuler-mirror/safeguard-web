import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
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

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    vi.useFakeTimers()

    getHost.mockResolvedValue(mockHost)
    getRealTimeMonitor.mockResolvedValue(mockMonitorData)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.useRealTimers()
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
    it('初始loading应为true', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(true)
    })

    it('数据加载完成后应隐藏loading状态', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.loading).toBe(false)
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

  describe('自动刷新功能（默认 10 秒）', () => {
    it('autoRefresh默认应为true', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.autoRefresh).toBe(true)
    })

    it('应设置自动刷新定时器', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.refreshInterval).not.toBeNull()
    })

    it('10秒后应自动刷新数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      vi.advanceTimersByTime(10000)

      expect(getRealTimeMonitor).toHaveBeenCalledTimes(1)
    })
  })

  describe('暂停/继续自动刷新', () => {
    it('点击切换按钮应改变autoRefresh状态', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const toggleButton = wrapper.find('.btn-toggle')
      expect(wrapper.vm.autoRefresh).toBe(true)

      await toggleButton.trigger('click')
      expect(wrapper.vm.autoRefresh).toBe(false)

      await toggleButton.trigger('click')
      expect(wrapper.vm.autoRefresh).toBe(true)
    })

    it('暂停后应清除定时器', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const toggleButton = wrapper.find('.btn-toggle')
      await toggleButton.trigger('click')

      expect(wrapper.vm.refreshInterval).toBeNull()
    })

    it('继续后应重新设置定时器', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const toggleButton = wrapper.find('.btn-toggle')
      await toggleButton.trigger('click')
      await toggleButton.trigger('click')

      expect(wrapper.vm.refreshInterval).not.toBeNull()
    })
  })

  describe('手动刷新按钮触发数据采集', () => {
    it('手动刷新按钮应存在', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const toggleButton = wrapper.find('.btn-toggle')
      await toggleButton.trigger('click')

      const refreshButton = wrapper.find('.btn-refresh')
      expect(refreshButton.exists()).toBe(true)
    })

    it('点击手动刷新按钮应调用API', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const toggleButton = wrapper.find('.btn-toggle')
      await toggleButton.trigger('click')

      vi.clearAllMocks()
      const refreshButton = wrapper.find('.btn-refresh')
      await refreshButton.trigger('click')

      expect(getRealTimeMonitor).toHaveBeenCalledWith(mockHostId)
    })
  })

  describe('组件卸载时清除定时器', () => {
    it('stopAutoRefresh函数应存在且能调用', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(typeof wrapper.vm.stopAutoRefresh).toBe('function')
      // 调用一下确保不会出错
      expect(() => wrapper.vm.stopAutoRefresh()).not.toThrow()
    })
  })

  describe('点击返回按钮跳转回主机仪表盘', () => {
    it('点击返回按钮应调用router.push', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const backButton = wrapper.find('.btn-back')
      await backButton.trigger('click')
      expect(mockPush).toHaveBeenCalledWith(`/hosts/${mockHostId}/dashboard`)
    })
  })

  describe('API 失败处理', () => {
    it('轮询失败时应显示pollError', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      const errorMessage = '获取监控数据失败'
      getRealTimeMonitor.mockRejectedValue(new Error(errorMessage))

      await wrapper.vm.loadMonitorData()
      await flushPromises()

      expect(wrapper.vm.pollError).toBe(errorMessage)
    })
  })

  describe('计算属性测试', () => {
    it('cpuData应正确格式化数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const cpuData = wrapper.vm.cpuData
      expect(cpuData.length).toBe(1)
      expect(cpuData[0].x).toBe(0)
      expect(cpuData[0].y).toBe(45.5)
    })

    it('memData应正确格式化数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const memData = wrapper.vm.memData
      expect(memData.length).toBe(1)
      expect(memData[0].x).toBe(0)
      expect(memData[0].y).toBe(60.2)
    })

    it('loadChartData应正确格式化数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const loadChartData = wrapper.vm.loadChartData
      expect(loadChartData.length).toBe(1)
      expect(loadChartData[0].x).toBe(0)
      expect(loadChartData[0].y).toBe(1.25)
    })

    it('maxNetValue应计算正确的最大值', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.maxNetValue).toBe(2100)
    })

    it('maxLoadValue应计算正确的最大值', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.maxLoadValue).toBe(2)
    })
  })

  describe('历史数据点限制', () => {
    it('超过maxDataPoints时应移除最旧的数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      // 添加足够多的数据点
      for (let i = 0; i < 25; i++) {
        await wrapper.vm.loadMonitorData()
      }

      expect(wrapper.vm.monitorHistory.length).toBe(20)
    })
  })

  describe('页面标题显示', () => {
    it('应显示包含主机名的标题', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.text()).toContain('test-host - 实时监控')
    })
  })

  describe('切换按钮文本', () => {
    it('autoRefresh为true时显示"暂停自动刷新"', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const toggleButton = wrapper.find('.btn-toggle')
      expect(toggleButton.text()).toBe('暂停自动刷新')
    })

    it('autoRefresh为false时显示"开启自动刷新"', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const toggleButton = wrapper.find('.btn-toggle')
      await toggleButton.trigger('click')

      expect(toggleButton.text()).toBe('开启自动刷新')
    })
  })
})
