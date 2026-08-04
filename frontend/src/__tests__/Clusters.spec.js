import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Clusters from '@/views/Clusters.vue'
import { getClusters, createCluster, updateCluster, deleteCluster, getClusterHosts } from '@/api/host'

vi.mock('@/api/host')

describe('Clusters 页面测试', () => {
  let wrapper

  const mockClusters = [
    { id: 1, name: 'test-cluster-1', description: 'test description', host_count: 5, created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-cluster-2', description: '', host_count: 3, created_at: '2024-01-02T00:00:00Z' }
  ]

  const mockHosts = [
    { id: 1, hostname: 'test-host-1', ip_address: '192.168.1.1', port: 22, status: 'online', os_type: 'CentOS 7' },
    { id: 2, hostname: 'test-host-2', ip_address: '192.168.1.2', port: 22, status: 'offline', os_type: 'Ubuntu 20.04' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getClusters.mockResolvedValue({ results: mockClusters })
    getClusterHosts.mockResolvedValue(mockHosts)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Clusters, {
      global: {
        mocks: {},
        stubs: {}
      }
    })
  }

})
