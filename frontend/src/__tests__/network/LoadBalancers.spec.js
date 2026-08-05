import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import LoadBalancers from '@/views/network/LoadBalancers.vue'
import { getLBs, createLB, updateLB, deleteLB, getLBsByProject, getLBsByK8s, getLBAzNames } from '@/api/network'

vi.mock('@/api/network')

describe('LoadBalancers 页面测试', () => {
  let wrapper

  const mockLBs = [
    { id: 1, name: 'test-lb-1', vip_address: '192.168.1.100', port: 80, algorithm: 'round_robin', status: 'active', description: 'test', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-lb-2', vip_address: '192.168.1.101', port: 443, algorithm: 'least_conn', status: 'inactive', description: 'test', created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getLBs.mockResolvedValue({ results: mockLBs })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(LoadBalancers, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getLBs', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getLBs).toHaveBeenCalled()
    })

    it('应该显示负载均衡器列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('test-lb-1')
      expect(wrapper.text()).toContain('192.168.1.100')
      expect(wrapper.text()).toContain('test-lb-2')
      expect(wrapper.text()).toContain('192.168.1.101')
    })

    it('应该显示活跃/未激活状态', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.status-active').exists()).toBe(true)
      expect(wrapper.find('.status-inactive').exists()).toBe(true)
    })
  })

})
