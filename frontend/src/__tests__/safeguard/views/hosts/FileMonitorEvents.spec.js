import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import FileMonitorEvents from '@/views/hosts/FileMonitorEvents.vue'
import { getFileMonitorEvents, collectFileMonitorEvents } from '@/api/safeguard/file-monitor'
import { getHost } from '@/api/host'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

vi.mock('@/api/safeguard/file-monitor')
vi.mock('@/api/host')

const mockPush = vi.fn()
const mockAlert = vi.fn()
window.alert = mockAlert

describe('FileMonitorEvents 页面测试', () => {
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockEvents = [
    { id: 1, path: '/etc/passwd', event_type: 'read', process_name: 'cat', user: 'root', timestamp: '2024-01-01T10:00:00Z' },
    { id: 2, path: '/etc/hosts', event_type: 'write', process_name: 'vi', user: 'admin', timestamp: '2024-01-01T11:00:00Z' }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockAlert.mockReset()

    getHost.mockResolvedValue(mockHost)
    getFileMonitorEvents.mockResolvedValue({ results: mockEvents })
    collectFileMonitorEvents.mockResolvedValue({ success: true })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(FileMonitorEvents, {
      global: {
        mocks: {
          $router: {
            push: mockPush
          },
          $route: {
            params: { id: 1 }
          }
        },
        stubs: {
          StatusBadge
        }
      }
    })
  }

})
