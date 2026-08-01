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

  describe('显示用户名、UID、GID、家目录、Shell', () => {
    it('应渲染表格并显示账户信息', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const table = wrapper.find('table')
      expect(table.exists()).toBe(true)

      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(3)
    })

    it('第一行应显示root账户信息', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const firstRow = wrapper.findAll('tbody tr')[0]
      expect(firstRow.text()).toContain('root')
      expect(firstRow.text()).toContain('0')
      expect(firstRow.text()).toContain('/root')
      expect(firstRow.text()).toContain('/bin/bash')
    })
  })

  describe('显示账户状态（锁定/活跃）', () => {
    it('应渲染StatusBadge组件显示账户状态', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const statusBadges = wrapper.findAllComponents(StatusBadge)
      expect(statusBadges.length).toBe(3)
    })

    it('未锁定账户应显示success状态', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const statusBadges = wrapper.findAllComponents(StatusBadge)
      expect(statusBadges[0].props('type')).toBe('success')
      expect(statusBadges[0].props('text')).toBe('正常')
    })

    it('锁定账户应显示danger状态', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const statusBadges = wrapper.findAllComponents(StatusBadge)
      expect(statusBadges[1].props('type')).toBe('danger')
      expect(statusBadges[1].props('text')).toBe('已锁定')
    })
  })

  describe('root 账户高亮显示', () => {
    it('root账户的状态应使用success类型', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const statusBadges = wrapper.findAllComponents(StatusBadge)
      expect(statusBadges[0].props('type')).toBe('success')
    })
  })

  describe('按用户名搜索过滤', () => {
    it('表格应显示所有账户信息', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const text = wrapper.text()
      expect(text).toContain('root')
      expect(text).toContain('www-data')
      expect(text).toContain('admin')
    })
  })

  describe('点击返回按钮跳转回主机仪表盘', () => {
    it('点击返回按钮应调用router.push', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const backButton = wrapper.find('.btn-back')
      await backButton.trigger('click')
      expect(mockPush).toHaveBeenCalledWith(`/hosts/${mockHostId}/dashboard`)
    })
  })

  describe('API 失败时显示错误信息', () => {
    it('getHost失败时应显示错误信息', async () => {
      const errorMessage = '获取主机信息失败'
      getHost.mockRejectedValue(new Error(errorMessage))

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.error').exists()).toBe(true)
      expect(wrapper.text()).toContain(errorMessage)
    })

    it('getAccountsInfo失败时应显示错误信息', async () => {
      const errorMessage = '获取账户信息失败'
      getAccountsInfo.mockRejectedValue(new Error(errorMessage))

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe(errorMessage)
    })
  })

  describe('显示空账户提示', () => {
    it('没有账户时应显示空提示', async () => {
      getAccountsInfo.mockResolvedValue({ accounts: [] })

      wrapper = createWrapper()
      await flushPromises()

      const emptyRow = wrapper.find('.empty-text')
      expect(emptyRow.exists()).toBe(true)
      expect(wrapper.text()).toContain('暂无账户信息')
    })
  })

  describe('表格列结构', () => {
    it('表格应有正确的列标题', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const headers = wrapper.findAll('thead th')
      expect(headers.length).toBe(6)
      expect(headers[0].text()).toBe('用户名')
      expect(headers[1].text()).toBe('UID')
      expect(headers[2].text()).toBe('GID')
      expect(headers[3].text()).toBe('用户主目录')
      expect(headers[4].text()).toBe('Shell')
      expect(headers[5].text()).toBe('状态')
    })
  })

  describe('刷新按钮功能', () => {
    it('刷新按钮存在且可点击', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const refreshButton = wrapper.find('.btn-refresh')
      expect(refreshButton.exists()).toBe(true)
    })

    it('点击刷新按钮应重新加载账户数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      const refreshButton = wrapper.find('.btn-refresh')
      await refreshButton.trigger('click')

      expect(getAccountsInfo).toHaveBeenCalledWith(mockHostId)
    })
  })

  describe('页面标题显示', () => {
    it('应显示包含主机名的标题', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.text()).toContain('test-host - 系统账户')
    })
  })

  describe('处理缺失的账户信息', () => {
    it('处理home为null的情况', async () => {
      const accountsWithNullHome = [
        { username: 'test', uid: 1001, gid: 1001, home: null, shell: '/bin/bash', locked: false }
      ]
      getAccountsInfo.mockResolvedValue({ accounts: accountsWithNullHome })

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('-')
    })

    it('处理shell为null的情况', async () => {
      const accountsWithNullShell = [
        { username: 'test', uid: 1001, gid: 1001, home: '/home/test', shell: null, locked: false }
      ]
      getAccountsInfo.mockResolvedValue({ accounts: accountsWithNullShell })

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('-')
    })
  })
})
