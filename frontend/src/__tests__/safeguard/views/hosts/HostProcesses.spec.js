import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostProcesses from '@/views/hosts/HostProcesses.vue'
import { getHost } from '@/api/host'
import { getProcessesInfo, killProcess } from '@/api/safeguard/host-info'
import ProcessList from '@/components/safeguard/ProcessList.vue'

vi.mock('@/api/host')
vi.mock('@/api/safeguard/host-info')

const mockPush = vi.fn()
const mockAlert = vi.fn()
window.alert = mockAlert

describe('HostProcesses 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockProcesses = [
    { pid: 1, name: 'systemd', cpu_percent: 0.5, mem_percent: 1.2 },
    { pid: 1234, name: 'nginx', cpu_percent: 2.5, mem_percent: 3.1 },
    { pid: 5678, name: 'node', cpu_percent: 10.5, mem_percent: 8.2 }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockAlert.mockReset()

    getHost.mockResolvedValue(mockHost)
    getProcessesInfo.mockResolvedValue({ processes: mockProcesses })
    killProcess.mockResolvedValue({ success: true })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostProcesses, {
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
          ProcessList
        }
      }
    })
  }

})
