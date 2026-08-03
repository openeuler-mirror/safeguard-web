import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import FileMonitorRules from '@/views/hosts/FileMonitorRules.vue'
import {
  getFileMonitorRules,
  createFileMonitorRule,
  updateFileMonitorRule,
  deleteFileMonitorRule
} from '@/api/safeguard/file-monitor'
import { getHost } from '@/api/host'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

vi.mock('@/api/safeguard/file-monitor')
vi.mock('@/api/host')

const mockPush = vi.fn()
const mockAlert = vi.fn()
window.alert = mockAlert

describe('FileMonitorRules 页面测试', () => {
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockRules = [
    { id: 1, path: '/etc/passwd', monitor_types: ['read', 'write'], enabled: true, created_at: '2024-01-01T00:00:00Z' },
    { id: 2, path: '/etc/hosts', monitor_types: ['create', 'delete'], enabled: false, created_at: '2024-01-02T00:00:00Z' }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockAlert.mockReset()

    getHost.mockResolvedValue(mockHost)
    getFileMonitorRules.mockResolvedValue({ results: mockRules })
    createFileMonitorRule.mockResolvedValue({ success: true })
    updateFileMonitorRule.mockResolvedValue({ success: true })
    deleteFileMonitorRule.mockResolvedValue({ success: true })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(FileMonitorRules, {
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
