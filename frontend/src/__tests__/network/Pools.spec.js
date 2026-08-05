import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Pools from '@/views/network/Pools.vue'
import { getPools, createPool, updatePool, deletePool } from '@/api/network'

vi.mock('@/api/network')

describe('Pools 页面测试', () => {
  let wrapper

  const mockPools = [
    { id: 1, name: 'test-pool-1', protocol: 'http', algorithm: 'round_robin', description: 'test', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-pool-2', protocol: 'tcp', algorithm: 'least_conn', description: 'test', created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getPools.mockResolvedValue({ results: mockPools })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Pools, {
      global: {
        stubs: {}
      }
    })
  }

})
