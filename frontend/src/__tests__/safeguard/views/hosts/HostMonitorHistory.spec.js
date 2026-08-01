import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostMonitorHistory from '@/views/hosts/HostMonitorHistory.vue'
import { getHost } from '@/api/host'
import { getMonitorHistory } from '@/api/safeguard/monitor'
import SimpleLineChart from '@/components/safeguard/SimpleLineChart.vue'

vi.mock('@/api/host')
vi.mock('@/api/safeguard/monitor')

const mockPush = vi.fn()

describe('HostMonitorHistory 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockHistoryData = [
    { timestamp: Date.now() - 3600000, cpu_percent: 45.5, mem_percent: 60.2, net_in: 1024, net_out: 2048, load_1: 1.25 },
    { timestamp: Date.now() - 3000000, cpu_percent: 50.1, mem_percent: 62.5, net_in: 1536, net_out: 2560, load_1: 1.45 },
    { timestamp: Date.now() - 2400000, cpu_percent: 42.3, mem_percent: 58.7, net_in: 768, net_out: 1792, load_1: 1.15 }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()

    getHost.mockResolvedValue(mockHost)
    getMonitorHistory.mockResolvedValue({ history: mockHistoryData })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostMonitorHistory, {
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
          SimpleLineChart
        }
      }
    })
  }

})
