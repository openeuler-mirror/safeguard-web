import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Listeners from '@/views/network/Listeners.vue'
import { getListeners, createListener, updateListener, deleteListener } from '@/api/network'

vi.mock('@/api/network')

describe('Listeners 页面测试', () => {
  let wrapper

  const mockListeners = [
    { id: 1, name: 'test-listener-1', loadbalancer_name: 'lb-1', protocol: 'http', port: 80, description: 'test', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-listener-2', loadbalancer_name: 'lb-2', protocol: 'https', port: 443, description: 'test', created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getListeners.mockResolvedValue({ results: mockListeners })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Listeners, {
      global: {
        stubs: {}
      }
    })
  }

})
