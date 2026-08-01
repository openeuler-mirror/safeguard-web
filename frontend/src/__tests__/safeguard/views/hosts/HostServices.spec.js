import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostServices from '@/views/hosts/HostServices.vue'
import { getHost } from '@/api/host'
import { getServicesInfo, controlService, getServiceLogs } from '@/api/safeguard/host-info'
import ServiceControl from '@/components/safeguard/ServiceControl.vue'

vi.mock('@/api/host')
vi.mock('@/api/safeguard/host-info')

const mockPush = vi.fn()
const mockAlert = vi.fn()
window.alert = mockAlert

describe('HostServices 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockServices = [
    { name: 'nginx', status: 'running', active: true },
    { name: 'ssh', status: 'running', active: true },
    { name: 'cron', status: 'stopped', active: false }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockAlert.mockReset()

    getHost.mockResolvedValue(mockHost)
    getServicesInfo.mockResolvedValue({ services: mockServices })
    controlService.mockResolvedValue({ success: true })
    getServiceLogs.mockResolvedValue({ logs: 'sample log content' })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostServices, {
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
          ServiceControl
        }
      }
    })
  }

  describe('页面加载时显示 loading 状态', () => {
    it('初始应显示loading状态', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(true)
    })

    it('数据加载完成后应停止loading', async () => {
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

  describe('加载服务列表数据', () => {
    it('应调用getHost和getServicesInfo API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHost).toHaveBeenCalledWith(mockHostId)
      expect(getServicesInfo).toHaveBeenCalledWith(mockHostId)
    })

    it('应正确设置services数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.services).toEqual(mockServices)
    })
  })

  describe('使用 ServiceControl 组件渲染服务', () => {
    it('应渲染ServiceControl组件', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.findComponent(ServiceControl).exists()).toBe(true)
    })

    it('ServiceControl组件应接收正确的props', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const serviceControl = wrapper.findComponent(ServiceControl)
      expect(serviceControl.props('services')).toEqual(mockServices)
      expect(serviceControl.props('loading')).toBe(false)
      expect(serviceControl.props('on-control')).toBeDefined()
      expect(serviceControl.props('on-get-logs')).toBeDefined()
    })
  })

})
