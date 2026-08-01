import { describe, it, expect, vi, beforeEach, afterEach, fakeTimers } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostMonitor from '@/views/hosts/HostMonitor.vue'
import { getHost } from '@/api/host'
import { getRealTimeMonitor } from '@/api/safeguard/monitor'
import MetricCard from '@/components/safeguard/MetricCard.vue'
import SimpleLineChart from '@/components/safeguard/SimpleLineChart.vue'

vi.mock('@/api/host')
vi.mock('@/api/safeguard/monitor')

const mockPush = vi.fn()

describe('HostMonitor 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockMonitorData = {
    cpu_percent: 45.5,
    mem_percent: 60.2,
    net_in: 1024,
    net_out: 2048,
    load_1: 1.25
  }

  let wrapper
  let clock

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    clock = fakeTimers()

    getHost.mockResolvedValue(mockHost)
    getRealTimeMonitor.mockResolvedValue(mockMonitorData)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    clock.clear()
  })

  const createWrapper = () => {
    return mount(HostMonitor, {
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
          MetricCard,
          SimpleLineChart
        }
      }
    })
  }

})
