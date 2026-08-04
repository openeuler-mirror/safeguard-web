import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Hosts from '@/views/Hosts.vue'
import { getHosts, createHost, updateHost, deleteHost, getClusterTree } from '@/api/host'

vi.mock('@/api/host')

const mockPush = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => ({})
}))

describe('Hosts 页面测试', () => {
  let wrapper

  const mockHosts = [
    { id: 1, hostname: 'test-host-1', ip_address: '192.168.1.1', port: 22, username: 'root', status: 'online', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, hostname: 'test-host-2', ip_address: '192.168.1.2', port: 22, username: 'root', status: 'offline', created_at: '2024-01-02T00:00:00Z' }
  ]

  const mockClusters = [
    { id: 1, name: 'test-cluster-1' },
    { id: 2, name: 'test-cluster-2' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    getHosts.mockResolvedValue({ results: mockHosts })
    getClusterTree.mockResolvedValue(mockClusters)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Hosts, {
      global: {
        mocks: {
          $router: {
            push: mockPush
          }
        },
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getHosts 和 getClusterTree', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getHosts).toHaveBeenCalled()
      expect(getClusterTree).toHaveBeenCalled()
    })

    it('应该显示主机列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('test-host-1')
      expect(wrapper.text()).toContain('192.168.1.1')
      expect(wrapper.text()).toContain('test-host-2')
      expect(wrapper.text()).toContain('192.168.1.2')
    })

    it('应该显示在线/离线状态', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.status-online').exists()).toBe(true)
      expect(wrapper.find('.status-offline').exists()).toBe(true)
    })
  })

})
