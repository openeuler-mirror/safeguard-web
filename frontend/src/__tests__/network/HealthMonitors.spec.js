import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HealthMonitors from '@/views/network/HealthMonitors.vue'
import { getHealthMonitors, createHealthMonitor, updateHealthMonitor, deleteHealthMonitor } from '@/api/network'

vi.mock('@/api/network')

describe('HealthMonitors 页面测试', () => {
  let wrapper

  const mockHealthMonitors = [
    { id: 1, name: 'test-hm-1', type: 'http', delay: 30, timeout: 5, max_retries: 3, created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-hm-2', type: 'tcp', delay: 60, timeout: 10, max_retries: 5, created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getHealthMonitors.mockResolvedValue({ results: mockHealthMonitors })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HealthMonitors, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getHealthMonitors', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getHealthMonitors).toHaveBeenCalled()
    })

    it('应该显示健康检查列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('test-hm-1')
      expect(wrapper.text()).toContain('test-hm-2')
    })
  })

})
