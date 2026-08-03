import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostDashboard from '@/views/hosts/HostDashboard.vue'
import { getHost } from '@/api/host'
import { getSystemInfo } from '@/api/safeguard/host-info'
import { getRealTimeMonitor } from '@/api/safeguard/monitor'
import MetricCard from '@/components/safeguard/MetricCard.vue'

// 模拟模块
vi.mock('@/api/host')
vi.mock('@/api/safeguard/host-info')
vi.mock('@/api/safeguard/monitor')

const mockPush = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => ({
    params: { id: 1 }
  })
}))

describe('HostDashboard 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockSystemInfo = {
    hostname: 'test-host',
    os: 'Ubuntu 20.04',
    kernel: '5.4.0-90-generic',
    cpu_cores: 4,
    mem_total: 8589934592,
    uptime: '10 days'
  }
  const mockMonitorData = {
    cpu_percent: 45.5,
    mem_percent: 60.2,
    disk_percent: 70.1,
    load_1: 1.25
  }

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()

    // 默认模拟成功返回
    getHost.mockResolvedValue(mockHost)
    getSystemInfo.mockResolvedValue(mockSystemInfo)
    getRealTimeMonitor.mockResolvedValue(mockMonitorData)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostDashboard, {
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
          MetricCard
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

  describe('加载主机基本信息', () => {
    it('应调用getHost API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHost).toHaveBeenCalledWith(mockHostId)
    })

    it('应正确设置host数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.host).toEqual(mockHost)
    })
  })

  describe('加载系统信息', () => {
    it('应调用getSystemInfo API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getSystemInfo).toHaveBeenCalledWith(mockHostId)
    })

    it('应正确设置systemInfo数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.systemInfo).toEqual(mockSystemInfo)
    })
  })

  describe('加载实时监控数据', () => {
    it('应调用getRealTimeMonitor API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getRealTimeMonitor).toHaveBeenCalledWith(mockHostId)
    })

    it('应正确设置monitorData数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.monitorData).toEqual(mockMonitorData)
    })
  })

  describe('渲染 4 个指标卡片', () => {
    it('应渲染4个MetricCard组件', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const metricCards = wrapper.findAllComponents(MetricCard)
      expect(metricCards.length).toBe(4)
    })

    it('指标卡片应包含正确的props', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const metricCards = wrapper.findAllComponents(MetricCard)
      expect(metricCards[0].props('label')).toBe('CPU 使用率')
      expect(metricCards[0].props('value')).toBe(45.5)
      expect(metricCards[0].props('unit')).toBe('%')
    })
  })

  describe('渲染快速导航按钮', () => {
    it('应渲染9个快速导航按钮', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const navButtons = wrapper.findAll('.nav-btn')
      expect(navButtons.length).toBe(9)
    })

    it('导航按钮应包含正确的文本', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.text()).toContain('端口信息')
      expect(wrapper.text()).toContain('进程管理')
      expect(wrapper.text()).toContain('服务控制')
      expect(wrapper.text()).toContain('实时监控')
    })
  })

  describe('渲染系统信息网格', () => {
    it('应渲染系统信息网格', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.find('.system-info').exists()).toBe(true)
    })

    it('系统信息应显示正确的内容', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.text()).toContain('主机名')
      expect(wrapper.text()).toContain('操作系统')
      expect(wrapper.text()).toContain('内核版本')
      expect(wrapper.text()).toContain('Ubuntu 20.04')
    })
  })

  describe('点击快速导航按钮正确跳转路由', () => {
    it('点击端口信息按钮应跳转到正确路由', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const portsButton = wrapper.findAll('.nav-btn')[0]
      await portsButton.trigger('click')
      expect(mockPush).toHaveBeenCalledWith(`/hosts/${mockHostId}/ports`)
    })

    it('点击进程管理按钮应跳转到正确路由', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const processesButton = wrapper.findAll('.nav-btn')[1]
      await processesButton.trigger('click')
      expect(mockPush).toHaveBeenCalledWith(`/hosts/${mockHostId}/processes`)
    })

    it('点击服务控制按钮应跳转到正确路由', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const servicesButton = wrapper.findAll('.nav-btn')[2]
      await servicesButton.trigger('click')
      expect(mockPush).toHaveBeenCalledWith(`/hosts/${mockHostId}/services`)
    })

    it('点击实时监控按钮应跳转到正确路由', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const monitorButton = wrapper.findAll('.nav-btn')[3]
      await monitorButton.trigger('click')
      expect(mockPush).toHaveBeenCalledWith(`/hosts/${mockHostId}/monitor`)
    })
  })

  describe('点击返回按钮跳转回主机列表', () => {
    it('点击返回按钮应调用router.push', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const backButton = wrapper.find('.btn-back')
      await backButton.trigger('click')
      expect(mockPush).toHaveBeenCalledWith('/hosts')
    })
  })

  describe('API 失败处理', () => {
    it('getSystemInfo失败时不应阻止其他数据加载', async () => {
      getSystemInfo.mockRejectedValue(new Error('获取系统信息失败'))

      wrapper = createWrapper()
      await flushPromises()

      expect(getHost).toHaveBeenCalled()
      expect(getRealTimeMonitor).toHaveBeenCalled()
    })
  })

  describe('formatBytes 正确格式化字节数', () => {
    it('应正确格式化字节为合适的单位', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.formatBytes(1024)).toBe('1.00 KB')
      expect(wrapper.vm.formatBytes(1048576)).toBe('1.00 MB')
      expect(wrapper.vm.formatBytes(1073741824)).toBe('1.00 GB')
    })

    it('处理空值应返回"-"', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.formatBytes(null)).toBe('-')
      expect(wrapper.vm.formatBytes(0)).toBe('-')
    })
  })

  describe('Promise.allSettled 正确处理部分失败', () => {
    it('一个API失败不应影响其他API的数据', async () => {
      getSystemInfo.mockRejectedValue(new Error('系统信息失败'))

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.host).toEqual(mockHost)
      expect(wrapper.vm.monitorData).toEqual(mockMonitorData)
    })
  })
})
