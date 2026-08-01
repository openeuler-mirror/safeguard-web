import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostDashboard from '@/views/hosts/HostDashboard.vue'
import { getHost } from '@/api/host'
import { getSystemInfo } from '@/api/safeguard/host-info'
import { getRealTimeMonitor } from '@/api/safeguard/monitor'
import MetricCard from '@/components/safeguard/MetricCard.vue'

// 模拟模块
vi.mock('@/api/host')
vi.mock('@/api/safeguard/host-info')
vi.mock('@/api/safeguard/monitor')

const mockPush = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => ({
    params: { id: 1 }
  })
}))

describe('HostDashboard 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockSystemInfo = {
    hostname: 'test-host',
    os: 'Ubuntu 20.04',
    kernel: '5.4.0-90-generic',
    cpu_cores: 4,
    mem_total: 8589934592,
    uptime: '10 days'
  }
  const mockMonitorData = {
    cpu_percent: 45.5,
    mem_percent: 60.2,
    disk_percent: 70.1,
    load_1: 1.25
  }

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()

    // 默认模拟成功返回
    getHost.mockResolvedValue(mockHost)
    getSystemInfo.mockResolvedValue(mockSystemInfo)
    getRealTimeMonitor.mockResolvedValue(mockMonitorData)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostDashboard, {
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
          MetricCard
        }
      }
    })
  }

})
