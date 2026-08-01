import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostServices from '@/views/hosts/HostServices.vue'
import { getHost } from '@/api/host'
import { getServicesInfo, controlService, getServiceLogs } from '@/api/safeguard/host-info'
import ServiceControl from '@/components/safeguard/ServiceControl.vue'

vi.mock('@/api/host')
vi.mock('@/api/safeguard/host-info')

const mockPush = vi.fn()
const mockAlert = vi.fn()
window.alert = mockAlert

describe('HostServices 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockServices = [
    { name: 'nginx', status: 'running', active: true },
    { name: 'ssh', status: 'running', active: true },
    { name: 'cron', status: 'stopped', active: false }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockAlert.mockReset()

    getHost.mockResolvedValue(mockHost)
    getServicesInfo.mockResolvedValue({ services: mockServices })
    controlService.mockResolvedValue({ success: true })
    getServiceLogs.mockResolvedValue({ logs: 'sample log content' })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostServices, {
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
          ServiceControl
        }
      }
    })
  }

})
