import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Users from '@/views/Users.vue'
import { getUsers, getAuthorities } from '@/api/user'

vi.mock('@/api/user')
vi.mock('@/components/UserAuthorityDialog.vue', () => ({
  name: 'UserAuthorityDialog',
  template: '<div class="user-authority-dialog"></div>',
  props: ['visible', 'userInfo', 'allRoles'],
  emits: ['close', 'success']
}))

describe('Users 页面测试', () => {
  let wrapper

  const mockUsers = [
    { id: 1, user: 'admin', nickname: '管理员', email: 'admin@example.com', phone: '13800138000', enable: 1, created_at: '2024-01-01T00:00:00Z' },
    { id: 2, user: 'testuser', nickname: '测试用户', email: 'test@example.com', phone: '13800138001', enable: 0, created_at: '2024-01-02T00:00:00Z' }
  ]

  const mockRoles = [
    { id: 1, authority_id: 'admin', authority_name: '管理员' },
    { id: 2, authority_id: 'user', authority_name: '普通用户' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getUsers.mockResolvedValue(mockUsers)
    getAuthorities.mockResolvedValue({ results: mockRoles })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Users, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getUsers 和 getAuthorities', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getUsers).toHaveBeenCalled()
      expect(getAuthorities).toHaveBeenCalled()
    })

    it('应该显示用户列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('admin')
      expect(wrapper.text()).toContain('管理员')
      expect(wrapper.text()).toContain('testuser')
      expect(wrapper.text()).toContain('测试用户')
    })

    it('应该显示用户状态', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.status-active').exists()).toBe(true)
      expect(wrapper.find('.status-disabled').exists()).toBe(true)
    })

    it('应该显示加载状态', async () => {
      getUsers.mockImplementation(() => new Promise(() => { }))
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('加载中...')
    })
  })

  describe('授权管理', () => {
    it('点击授权按钮应该打开授权对话框', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.auth-btn')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.selectedUser).toEqual(mockUsers[0])
    })

    it('授权对话框成功回调应该刷新用户列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.auth-btn')[0].trigger('click')
      await flushPromises()

      getUsers.mockClear()
      await wrapper.vm.handleAuthSuccess()
      await flushPromises()

      expect(getUsers).toHaveBeenCalled()
    })
  })

  describe('刷新列表', () => {
    it('点击刷新按钮应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      getUsers.mockClear()
      await wrapper.find('button.refresh-btn').trigger('click')
      await flushPromises()

      expect(getUsers).toHaveBeenCalled()
    })
  })

  describe('错误处理', () => {
    it('加载用户列表失败时应该显示错误信息', async () => {
      getUsers.mockRejectedValue(new Error('加载用户列表失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe('加载用户列表失败')
      expect(wrapper.find('.error').exists()).toBe(true)
    })

    it('加载角色列表失败时应该在控制台打印错误', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { })
      getAuthorities.mockRejectedValue(new Error('加载角色列表失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })

  describe('工具函数', () => {
    it('formatDate 应该正确格式化日期', () => {
      wrapper = createWrapper()
      const dateStr = '2024-01-01T00:00:00Z'
      const result = wrapper.vm.formatDate(dateStr)
      expect(result).not.toBe('-')
    })

    it('formatDate 处理空值应该返回 "-"', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatDate('')).toBe('-')
      expect(wrapper.vm.formatDate(null)).toBe('-')
    })
  })
})
