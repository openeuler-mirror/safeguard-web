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
    })
  })

  describe('处理服务控制操作', () => {
    it('handleControlService应调用controlService API', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.handleControlService('nginx', 'start')

      expect(controlService).toHaveBeenCalledWith(mockHostId, { name: 'nginx', action: 'start' })
    })

    it('start操作成功后应刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      await wrapper.vm.handleControlService('nginx', 'start')

      expect(getServicesInfo).toHaveBeenCalledTimes(1)
    })

    it('stop操作成功后应刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      await wrapper.vm.handleControlService('nginx', 'stop')

      expect(getServicesInfo).toHaveBeenCalledTimes(1)
    })

    it('restart操作成功后应刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      await wrapper.vm.handleControlService('nginx', 'restart')

      expect(getServicesInfo).toHaveBeenCalledTimes(1)
    })

    it('reload操作成功后应刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      await wrapper.vm.handleControlService('nginx', 'reload')

      expect(getServicesInfo).toHaveBeenCalledTimes(1)
    })

    it('服务操作成功后应显示成功提示', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.handleControlService('nginx', 'start')

      expect(mockAlert).toHaveBeenCalledWith('操作成功')
    })
  })

  describe('处理获取服务日志操作', () => {
    it('handleGetServiceLogs应调用getServiceLogs API', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const result = await wrapper.vm.handleGetServiceLogs('nginx')

      expect(getServiceLogs).toHaveBeenCalledWith(mockHostId, 'nginx')
      expect(result).toBe('sample log content')
    })

    it('获取日志失败时应显示错误提示', async () => {
      const errorMessage = '获取日志失败'
      getServiceLogs.mockRejectedValue(new Error(errorMessage))

      wrapper = createWrapper()
      await flushPromises()

      const result = await wrapper.vm.handleGetServiceLogs('nginx')

      expect(mockAlert).toHaveBeenCalledWith(errorMessage)
      expect(result).toBe('')
    })
  })

  describe('服务操作失败显示错误提示', () => {
    it('controlService失败时应显示错误', async () => {
      const errorMessage = '操作失败'
      controlService.mockRejectedValue(new Error(errorMessage))

      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.handleControlService('nginx', 'start')

      expect(mockAlert).toHaveBeenCalledWith(errorMessage)
    })
  })

  describe('服务日志弹窗正确显示', () => {
    it('handleGetServiceLogs函数应存在', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(typeof wrapper.vm.handleGetServiceLogs).toBe('function')
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
    it('getHost失败时应设置错误信息', async () => {
      const errorMessage = '获取主机信息失败'
      getHost.mockRejectedValue(new Error(errorMessage))

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe(errorMessage)
    })

    it('getServicesInfo失败时应设置错误信息', async () => {
      const errorMessage = '获取服务信息失败'
      getServicesInfo.mockRejectedValue(new Error(errorMessage))

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

    it('点击刷新按钮应重新加载服务数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      const refreshButton = wrapper.find('.btn-refresh')
      await refreshButton.trigger('click')

      expect(getServicesInfo).toHaveBeenCalledWith(mockHostId)
    })
  })

  describe('页面标题显示', () => {
    it('应显示包含主机名的标题', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.text()).toContain('test-host - 服务控制')
    })
  })
})
