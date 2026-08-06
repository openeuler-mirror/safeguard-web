import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Safeguards from '@/views/security/Safeguards.vue'
import {
  getSafeguards,
  createSafeguard,
  updateSafeguard,
  deleteSafeguard,
  deploySafeguard,
  rollbackSafeguard,
  getSafeguardStatus
} from '@/api/security'

vi.mock('@/api/security')

describe('Safeguards 页面测试', () => {
  let wrapper

  const mockSafeguards = [
    { id: 1, name: 'test-sg-1', safeguard_type: 'safeguardx86', arch: 'x86', host: '192.168.1.1', status: 'success', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-sg-2', safeguard_type: 'safeguardx86', arch: 'arm', host: '192.168.1.2', status: 'failed', created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getSafeguards.mockResolvedValue({ results: mockSafeguards, count: 2 })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Safeguards, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getSafeguards', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getSafeguards).toHaveBeenCalled()
    })

    it('应该显示安全防护列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('test-sg-1')
      expect(wrapper.text()).toContain('test-sg-2')
      expect(wrapper.text()).toContain('192.168.1.1')
    })

    it('应该显示状态标签', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.status-success').exists()).toBe(true)
      expect(wrapper.find('.status-failed').exists()).toBe(true)
    })

    it('应该显示加载状态', async () => {
      getSafeguards.mockImplementation(() => new Promise(() => { }))
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('加载中...')
    })
  })

})
