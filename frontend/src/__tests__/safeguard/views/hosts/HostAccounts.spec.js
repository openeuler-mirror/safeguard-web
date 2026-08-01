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

  describe('页面加载时显示 loading 状态', () => {
    it('初始应显示loading状态', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('.loading').exists()).toBe(true)
    })

    it('数据加载完成后应隐藏loading状态', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.find('.loading').exists()).toBe(false)
    })
  })

  describe('从路由参数获取 hostId', () => {
    it('应正确从路由参数获取hostId', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.hostId).toBe(mockHostId)
    })
  })

  describe('加载系统账户列表', () => {
    it('应调用getHost和getAccountsInfo API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHost).toHaveBeenCalledWith(mockHostId)
      expect(getAccountsInfo).toHaveBeenCalledWith(mockHostId)
    })

    it('应正确设置accounts数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.accounts).toEqual(mockAccounts)
    })
  })

})
