import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import SystemLogs from '@/views/hosts/SystemLogs.vue'
import { getSystemLogs } from '@/api/safeguard/host-info'
import { getHost } from '@/api/host'

vi.mock('@/api/safeguard/host-info')
vi.mock('@/api/host')

const mockPush = vi.fn()

describe('SystemLogs 页面测试', () => {
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockLogsData = { logs: 'Jan  1 10:00:00 test-host kernel: [0.000000] Linux version 5.4.0\nJan  1 10:00:01 test-host sshd[1234]: Accepted publickey' }

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()

    getHost.mockResolvedValue(mockHost)
    getSystemLogs.mockResolvedValue(mockLogsData)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(SystemLogs, {
      global: {
        mocks: {
          $router: {
            push: mockPush
          },
          $route: {
            params: { id: 1 }
          }
        }
      }
    })
  }

})
