import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostPorts from '@/views/hosts/HostPorts.vue'
import { getHost } from '@/api/host'
import { getPortsInfo } from '@/api/safeguard/host-info'
import PortList from '@/components/safeguard/PortList.vue'

vi.mock('@/api/host')
vi.mock('@/api/safeguard/host-info')

const mockPush = vi.fn()

describe('HostPorts 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockPorts = [
    { port: 22, protocol: 'tcp', process: 'sshd', state: 'LISTEN' },
    { port: 80, protocol: 'tcp', process: 'nginx', state: 'LISTEN' },
    { port: 443, protocol: 'tcp', process: 'nginx', state: 'LISTEN' }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()

    getHost.mockResolvedValue(mockHost)
    getPortsInfo.mockResolvedValue({ ports: mockPorts })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostPorts, {
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
          PortList
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

  describe('加载端口列表数据', () => {
    it('应调用getHost和getPortsInfo API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHost).toHaveBeenCalledWith(mockHostId)
      expect(getPortsInfo).toHaveBeenCalledWith(mockHostId)
    })

    it('应正确设置ports数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.ports).toEqual(mockPorts)
    })
  })

  describe('使用 PortList 组件渲染端口', () => {
    it('应渲染PortList组件', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.findComponent(PortList).exists()).toBe(true)
    })

    it('PortList组件应接收正确的props', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const portList = wrapper.findComponent(PortList)
      expect(portList.props('ports')).toEqual(mockPorts)
      expect(portList.props('loading')).toBe(false)
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

    it('getPortsInfo失败时应设置错误信息', async () => {
      const errorMessage = '获取端口信息失败'
      getPortsInfo.mockRejectedValue(new Error(errorMessage))

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe(errorMessage)
    })

    it('PortList组件应接收error prop', async () => {
      const errorMessage = '获取端口信息失败'
      getPortsInfo.mockRejectedValue(new Error(errorMessage))

      wrapper = createWrapper()
      await flushPromises()

      const portList = wrapper.findComponent(PortList)
      expect(portList.props('error')).toBe(errorMessage)
    })
  })

})
