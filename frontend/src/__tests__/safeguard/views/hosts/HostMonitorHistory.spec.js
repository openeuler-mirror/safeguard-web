import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostMonitorHistory from '@/views/hosts/HostMonitorHistory.vue'
import { getHost } from '@/api/host'
import { getMonitorHistory } from '@/api/safeguard/monitor'
import SimpleLineChart from '@/components/safeguard/SimpleLineChart.vue'

vi.mock('@/api/host')
vi.mock('@/api/safeguard/monitor')

const mockPush = vi.fn()

describe('HostMonitorHistory 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockHistoryData = [
    { timestamp: Date.now() - 3600000, cpu_percent: 45.5, mem_percent: 60.2, net_in: 1024, net_out: 2048, load_1: 1.25 },
    { timestamp: Date.now() - 3000000, cpu_percent: 50.1, mem_percent: 62.5, net_in: 1536, net_out: 2560, load_1: 1.45 },
    { timestamp: Date.now() - 2400000, cpu_percent: 42.3, mem_percent: 58.7, net_in: 768, net_out: 1792, load_1: 1.15 }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()

    getHost.mockResolvedValue(mockHost)
    getMonitorHistory.mockResolvedValue({ history: mockHistoryData })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostMonitorHistory, {
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

  describe('时间范围选择器正常工作', () => {
    it('时间范围选择器应存在', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const timeSelect = wrapper.findAll('.filter-select')[0]
      expect(timeSelect.exists()).toBe(true)
    })

    it('timeRange默认值应为1h', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.timeRange).toBe('1h')
    })

    it('时间范围选择器应有4个选项', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const timeSelect = wrapper.findAll('.filter-select')[0]
      const options = timeSelect.findAll('option')
      expect(options.length).toBe(4)
    })

    it('改变时间范围应重新加载数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      await wrapper.setData({ timeRange: '6h' })
      const timeSelect = wrapper.findAll('.filter-select')[0]
      await timeSelect.trigger('change')

      expect(getMonitorHistory).toHaveBeenCalledWith(mockHostId, { range: '6h' })
    })
  })

  describe('指标类型选择器正常工作', () => {
    it('指标类型选择器应存在', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const metricSelect = wrapper.findAll('.filter-select')[1]
      expect(metricSelect.exists()).toBe(true)
    })

    it('metricType默认值应为all', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.metricType).toBe('all')
    })

    it('指标类型选择器应有4个选项', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const metricSelect = wrapper.findAll('.filter-select')[1]
      const options = metricSelect.findAll('option')
      expect(options.length).toBe(4)
    })
  })

  describe('加载历史监控数据', () => {
    it('应调用getHost和getMonitorHistory API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHost).toHaveBeenCalledWith(mockHostId)
      expect(getMonitorHistory).toHaveBeenCalledWith(mockHostId, { range: '1h' })
    })

    it('应正确设置historyData数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.historyData).toEqual(mockHistoryData)
    })
  })

  describe('渲染历史数据图表', () => {
    it('metricType为all时应渲染所有3个图表', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const charts = wrapper.findAllComponents(SimpleLineChart)
      expect(charts.length).toBe(3)
    })

    it('metricType为cpu时应只渲染CPU图表', async () => {
      wrapper = createWrapper()
      await flushPromises()
      await wrapper.setData({ metricType: 'cpu' })

      expect(wrapper.vm.showCpuChart).toBe(true)
      expect(wrapper.vm.showMemChart).toBe(false)
      expect(wrapper.vm.showNetChart).toBe(false)
    })

    it('metricType为memory时应只渲染内存图表', async () => {
      wrapper = createWrapper()
      await flushPromises()
      await wrapper.setData({ metricType: 'memory' })

      expect(wrapper.vm.showCpuChart).toBe(false)
      expect(wrapper.vm.showMemChart).toBe(true)
      expect(wrapper.vm.showNetChart).toBe(false)
    })

    it('metricType为network时应只渲染网络图表', async () => {
      wrapper = createWrapper()
      await flushPromises()
      await wrapper.setData({ metricType: 'network' })

      expect(wrapper.vm.showCpuChart).toBe(false)
      expect(wrapper.vm.showMemChart).toBe(false)
      expect(wrapper.vm.showNetChart).toBe(true)
    })
  })

  describe('渲染历史数据表格', () => {
    it('应渲染数据表格', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.find('table').exists()).toBe(true)
    })

    it('表格应显示正确的列数', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const headers = wrapper.findAll('thead th')
      expect(headers.length).toBe(6)
    })

    it('表格应显示正确的行数', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(3)
    })
  })

  describe('分页功能正常工作', () => {
    it('表格应能显示多行数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.text()).toContain('45.5')
      expect(wrapper.text()).toContain('50.1')
      expect(wrapper.text()).toContain('42.3')
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

  describe('API 失败时显示错误信息', () => {
    it('getHost失败时应显示错误信息', async () => {
      const errorMessage = '获取主机信息失败'
      getHost.mockRejectedValue(new Error(errorMessage))

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.error').exists()).toBe(true)
      expect(wrapper.text()).toContain(errorMessage)
    })

    it('getMonitorHistory失败时应设置错误信息', async () => {
      const errorMessage = '获取历史监控数据失败'
      getMonitorHistory.mockRejectedValue(new Error(errorMessage))

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe(errorMessage)
    })
  })

  describe('刷新按钮功能', () => {
    it('刷新按钮存在且可点击', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const refreshButton = wrapper.find('.btn-refresh')
      expect(refreshButton.exists()).toBe(true)
    })

    it('点击刷新按钮应重新加载历史数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      const refreshButton = wrapper.find('.btn-refresh')
      await refreshButton.trigger('click')

      expect(getMonitorHistory).toHaveBeenCalledWith(mockHostId, { range: '1h' })
    })
  })

  describe('页面标题显示', () => {
    it('应显示包含主机名的标题', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.text()).toContain('test-host - 历史监控')
    })
  })

  describe('计算属性测试', () => {
    it('cpuChartData应正确格式化数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const cpuChartData = wrapper.vm.cpuChartData
      expect(cpuChartData.length).toBe(3)
      expect(cpuChartData[0].y).toBe(45.5)
      expect(cpuChartData[1].y).toBe(50.1)
    })

    it('memChartData应正确格式化数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const memChartData = wrapper.vm.memChartData
      expect(memChartData.length).toBe(3)
      expect(memChartData[0].y).toBe(60.2)
    })

    it('netInChartData应正确格式化数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const netInChartData = wrapper.vm.netInChartData
      expect(netInChartData.length).toBe(3)
      expect(netInChartData[0].y).toBe(1024)
    })

    it('netOutChartData应正确格式化数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const netOutChartData = wrapper.vm.netOutChartData
      expect(netOutChartData.length).toBe(3)
      expect(netOutChartData[0].y).toBe(2048)
    })

    it('maxNetValue应计算正确的最大值', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.maxNetValue).toBe(2600)
    })
  })

  describe('formatTime方法测试', () => {
    it('应正确格式化时间戳', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const result = wrapper.vm.formatTime(Date.now())
      expect(typeof result).toBe('string')
    })

    it('应处理null时间戳', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const result = wrapper.vm.formatTime(null)
      expect(result).toBe('-')
    })
  })

  describe('空数据处理', () => {
    it('没有数据时应显示空提示', async () => {
      getMonitorHistory.mockResolvedValue({ history: [] })

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无数据')
    })
  })

  describe('updateChartData方法', () => {
    it('updateChartData应能被调用', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(() => wrapper.vm.updateChartData()).not.toThrow()
    })
  })
})
