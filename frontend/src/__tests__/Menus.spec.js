import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Menus from '@/views/Menus.vue'
import { getMenuTree, createMenu, updateMenu, deleteMenu, reorderMenus } from '@/api/authority'

vi.mock('@/api/authority')

describe('Menus 页面测试', () => {
  let wrapper

  const mockMenus = [
    { id: 1, parent: null, path: '/dashboard', name: 'Dashboard', component: '@/views/Dashboard.vue', sort: 0, meta: { title: '首页', icon: '🏠' } },
    {
      id: 2, parent: null, path: '/users', name: 'Users', component: '@/views/Users.vue', sort: 1, meta: { title: '用户管理', icon: '👤' }, children: [
        { id: 3, parent: 2, path: '/users/list', name: 'UserList', component: '@/views/Users.vue', sort: 0, meta: { title: '用户列表', icon: '📄' } }
      ]
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getMenuTree.mockResolvedValue(mockMenus)
    vi.spyOn(window, 'confirm').mockImplementation(() => true)
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Menus, {
      global: {
        mocks: {
          $store: {
            dispatch: vi.fn()
          }
        },
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getMenuTree', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getMenuTree).toHaveBeenCalled()
    })

    it('应该显示菜单树', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('首页')
      expect(wrapper.text()).toContain('Dashboard')
      expect(wrapper.text()).toContain('/dashboard')
    })

    it('应该显示加载状态', async () => {
      getMenuTree.mockImplementation(() => new Promise(() => { }))
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('加载中...')
    })
  })

  describe('创建菜单', () => {
    it('点击新增菜单按钮应该打开弹窗', async () => {
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

      createMenu.mockResolvedValue({})

      await wrapper.find('button.add-btn').trigger('click')
      await flushPromises()

      wrapper.vm.formData.path = '/test'
      wrapper.vm.formData.name = 'Test'
      await wrapper.vm.handleSave()
      await flushPromises()

      expect(createMenu).toHaveBeenCalled()
    })

    it('路由路径为空时应该显示验证错误', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.add-btn').trigger('click')
      await flushPromises()

      wrapper.vm.formData.path = ''
      wrapper.vm.formData.name = 'Test'
      await wrapper.vm.handleSave()

      expect(wrapper.vm.formError).toBe('请输入路由路径')
      expect(createMenu).not.toHaveBeenCalled()
    })

    it('路由名称为空时应该显示验证错误', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.add-btn').trigger('click')
      await flushPromises()

      wrapper.vm.formData.path = '/test'
      wrapper.vm.formData.name = ''
      await wrapper.vm.handleSave()

      expect(wrapper.vm.formError).toBe('请输入路由名称')
      expect(createMenu).not.toHaveBeenCalled()
    })

    it('创建失败时应该显示错误信息', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createMenu.mockRejectedValue(new Error('创建失败'))

      await wrapper.find('button.add-btn').trigger('click')
      await flushPromises()

      wrapper.vm.formData.path = '/test'
      wrapper.vm.formData.name = 'Test'
      await wrapper.vm.handleSave()
      await flushPromises()

      expect(wrapper.vm.formError).toBe('创建失败')
    })
  })

  describe('编辑菜单', () => {
    it('点击编辑按钮应该打开弹窗并填充数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.edit-btn')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.formData.path).toBe('/dashboard')
    })

    it('编辑成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      updateMenu.mockResolvedValue({})

      await wrapper.findAll('button.edit-btn')[0].trigger('click')
      await flushPromises()

      wrapper.vm.formData.path = '/dashboard'
      wrapper.vm.formData.name = 'Dashboard'
      await wrapper.vm.handleSave()
      await flushPromises()

      expect(updateMenu).toHaveBeenCalled()
    })
  })

  describe('删除菜单', () => {
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

      deleteMenu.mockResolvedValue({})

      await wrapper.findAll('button.delete-btn')[0].trigger('click')
      await flushPromises()

      expect(deleteMenu).toHaveBeenCalledWith(1)
    })

    it('删除失败时应该显示 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      deleteMenu.mockRejectedValue(new Error('删除失败'))

      await wrapper.findAll('button.delete-btn')[0].trigger('click')
      await flushPromises()

      expect(window.alert).toHaveBeenCalledWith('删除失败')
    })
  })

})
