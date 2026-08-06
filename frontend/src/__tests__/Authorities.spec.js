import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Authorities from '@/views/Authorities.vue'
import {
  getAuthorities,
  createAuthority,
  updateAuthority,
  deleteAuthority,
  copyAuthority
} from '@/api/authority'

vi.mock('@/api/authority')
vi.mock('@/components/AuthorityMenuDialog.vue', () => ({
  name: 'AuthorityMenuDialog',
  template: '<div class="authority-menu-dialog"></div>',
  props: ['visible', 'authorityInfo'],
  emits: ['close', 'success']
}))

describe('Authorities 页面测试', () => {
  let wrapper

  const mockAuthorities = [
    { id: 1, authority_id: 'admin', authority_name: '管理员', parent: null, default_router: 'dashboard', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, authority_id: 'user', authority_name: '普通用户', parent: null, default_router: 'dashboard', created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getAuthorities.mockResolvedValue({ results: mockAuthorities })
    vi.spyOn(window, 'confirm').mockImplementation(() => true)
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Authorities, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getAuthorities', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getAuthorities).toHaveBeenCalled()
    })

    it('应该显示角色列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('admin')
      expect(wrapper.text()).toContain('管理员')
      expect(wrapper.text()).toContain('普通用户')
    })

    it('应该显示加载状态', async () => {
      getAuthorities.mockImplementation(() => new Promise(() => { }))
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('加载中...')
    })
  })

  describe('创建角色', () => {
    it('点击新增角色按钮应该打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.add-btn').trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
    })

    it('创建成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createAuthority.mockResolvedValue({})

      await wrapper.find('button.add-btn').trigger('click')
      await flushPromises()

      wrapper.vm.formData.authority_id = 'test'
      wrapper.vm.formData.authority_name = '测试角色'
      await wrapper.vm.handleSave()
      await flushPromises()

      expect(createAuthority).toHaveBeenCalled()
      expect(getAuthorities).toHaveBeenCalledTimes(2)
    })

    it('角色ID为空时应该显示验证错误', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.add-btn').trigger('click')
      await flushPromises()

      wrapper.vm.formData.authority_id = ''
      await wrapper.vm.handleSave()

      expect(wrapper.vm.formError).toBe('请输入角色ID')
      expect(createAuthority).not.toHaveBeenCalled()
    })

    it('角色名称为空时应该显示验证错误', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.add-btn').trigger('click')
      await flushPromises()

      wrapper.vm.formData.authority_id = 'test'
      wrapper.vm.formData.authority_name = ''
      await wrapper.vm.handleSave()

      expect(wrapper.vm.formError).toBe('请输入角色名称')
      expect(createAuthority).not.toHaveBeenCalled()
    })

    it('创建失败时应该显示错误信息', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createAuthority.mockRejectedValue(new Error('创建失败'))

      await wrapper.find('button.add-btn').trigger('click')
      await flushPromises()

      wrapper.vm.formData.authority_id = 'test'
      wrapper.vm.formData.authority_name = '测试角色'
      await wrapper.vm.handleSave()
      await flushPromises()

      expect(wrapper.vm.formError).toBe('创建失败')
    })
  })

  describe('编辑角色', () => {
    it('点击编辑按钮应该打开弹窗并填充数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.edit-btn')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.formData.authority_id).toBe('admin')
      expect(wrapper.vm.formData.authority_name).toBe('管理员')
    })

    it('编辑成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      updateAuthority.mockResolvedValue({})

      await wrapper.findAll('button.edit-btn')[0].trigger('click')
      await flushPromises()

      await wrapper.vm.handleSave()
      await flushPromises()

      expect(updateAuthority).toHaveBeenCalled()
      expect(getAuthorities).toHaveBeenCalledTimes(2)
    })
  })

  describe('删除角色', () => {
    it('点击删除按钮应该显示确认对话框', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.delete-btn')[0].trigger('click')
      await flushPromises()

      expect(window.confirm).toHaveBeenCalled()
    })

    it('确认删除后应该调用 API 并刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      deleteAuthority.mockResolvedValue({})

      await wrapper.findAll('button.delete-btn')[0].trigger('click')
      await flushPromises()

      expect(deleteAuthority).toHaveBeenCalledWith(1)
      expect(getAuthorities).toHaveBeenCalledTimes(2)
    })

    it('删除失败时应该显示 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      deleteAuthority.mockRejectedValue(new Error('删除失败'))

      await wrapper.findAll('button.delete-btn')[0].trigger('click')
      await flushPromises()

      expect(window.alert).toHaveBeenCalledWith('删除失败')
    })
  })

  describe('复制角色', () => {
    it('点击复制按钮应该调用 copyAuthority 并刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      copyAuthority.mockResolvedValue({})

      await wrapper.findAll('button.copy-btn')[0].trigger('click')
      await flushPromises()

      expect(copyAuthority).toHaveBeenCalledWith(1)
      expect(getAuthorities).toHaveBeenCalledTimes(2)
    })

    it('复制失败时应该显示 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      copyAuthority.mockRejectedValue(new Error('复制失败'))

      await wrapper.findAll('button.copy-btn')[0].trigger('click')
      await flushPromises()

      expect(window.alert).toHaveBeenCalledWith('复制失败')
    })
  })

  describe('菜单管理', () => {
    it('点击菜单按钮应该打开菜单对话框', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.menu-btn')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.menuDialogVisible).toBe(true)
      expect(wrapper.vm.selectedAuthority).toEqual(mockAuthorities[0])
    })

    it('菜单对话框成功回调应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.menu-btn')[0].trigger('click')
      await flushPromises()

      await wrapper.vm.handleMenuSuccess()
      await flushPromises()

      expect(getAuthorities).toHaveBeenCalledTimes(2)
    })
  })

  describe('刷新列表', () => {
    it('点击刷新按钮应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.refresh-btn').trigger('click')
      await flushPromises()

      expect(getAuthorities).toHaveBeenCalledTimes(2)
    })
  })

})
