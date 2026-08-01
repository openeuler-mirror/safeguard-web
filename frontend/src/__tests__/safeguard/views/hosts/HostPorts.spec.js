import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostPorts from '@/views/hosts/HostPorts.vue'
import { getHost } from '@/api/host'
import { getPortsInfo } from '@/api/safeguard/host-info'
import PortList from '@/components/safeguard/PortList.vue'

vi.mock('@/api/host')
vi.mock('@/api/safeguard/host-info')

const mockPush = vi.fn()

describe('HostPorts 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockPorts = [
    { port: 22, protocol: 'tcp', process: 'sshd', state: 'LISTEN' },
    { port: 80, protocol: 'tcp', process: 'nginx', state: 'LISTEN' },
    { port: 443, protocol: 'tcp', process: 'nginx', state: 'LISTEN' }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()

    getHost.mockResolvedValue(mockHost)
    getPortsInfo.mockResolvedValue({ ports: mockPorts })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostPorts, {
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
          PortList
        }
      }
    })
  }

})
