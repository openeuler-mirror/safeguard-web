import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostAccounts from '@/views/hosts/HostAccounts.vue'
import { getHost } from '@/api/host'
import { getAccountsInfo } from '@/api/safeguard/host-info'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

vi.mock('@/api/host')
vi.mock('@/api/safeguard/host-info')

const mockPush = vi.fn()

describe('HostAccounts 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockAccounts = [
    { username: 'root', uid: 0, gid: 0, home: '/root', shell: '/bin/bash', locked: false },
    { username: 'www-data', uid: 33, gid: 33, home: '/var/www', shell: '/usr/sbin/nologin', locked: true },
    { username: 'admin', uid: 1000, gid: 1000, home: '/home/admin', shell: '/bin/bash', locked: false }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()

    getHost.mockResolvedValue(mockHost)
    getAccountsInfo.mockResolvedValue({ accounts: mockAccounts })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostAccounts, {
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
          StatusBadge
        }
      }
    })
  }

})
