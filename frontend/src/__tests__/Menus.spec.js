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
      await wrapper.vm.$nextTick()
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

  describe('添加子菜单', () => {
    it('点击添加子菜单按钮应该打开弹窗并设置父菜单', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.add-child-btn')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
      expect(wrapper.vm.formData.parent).toBe(1)
    })
  })

  describe('刷新列表', () => {
    it('点击刷新按钮应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      getMenuTree.mockClear()
      await wrapper.find('button.refresh-btn').trigger('click')
      await flushPromises()

      expect(getMenuTree).toHaveBeenCalledTimes(1)
    })
  })

  describe('错误处理', () => {
    it('加载菜单列表失败时应该显示错误信息', async () => {
      getMenuTree.mockRejectedValue(new Error('加载菜单列表失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe('加载菜单列表失败')
      expect(wrapper.find('.error').exists()).toBe(true)
    })
  })

  describe('工具函数', () => {
    it('isEmoji 应该正确识别 emoji', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.isEmoji('🏠')).toBe(true)
      expect(wrapper.vm.isEmoji('👤')).toBe(true)
      expect(wrapper.vm.isEmoji('Home')).toBe(false)
      expect(wrapper.vm.isEmoji('')).toBe(false)
    })

    it('flattenMenus 应该正确扁平化菜单树', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.flattenMenus(mockMenus)
      expect(result.length).toBe(3)
      expect(result[0].id).toBe(1)
      expect(result[1].id).toBe(2)
      expect(result[2].id).toBe(3)
    })
  })

  describe('拖拽排序', () => {
    it('拖拽开始应该设置拖拽状态', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const mockEvent = {
        dataTransfer: {
          effectAllowed: '',
          dropEffect: ''
        },
        target: {
          closest: () => ({ classList: { add: vi.fn() } })
        }
      }

      await wrapper.vm.onDragStart(mockEvent, mockMenus[0], 'top', 0)

      expect(wrapper.vm.draggingMenu).toEqual(mockMenus[0])
      expect(wrapper.vm.dragParentId).toBe('top')
      expect(wrapper.vm.dragIndex).toBe(0)
    })

    it('拖拽结束应该清除拖拽状态', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.draggingMenu = mockMenus[0]
      wrapper.vm.dragParentId = 'top'
      wrapper.vm.dragIndex = 0

      await wrapper.vm.onDragEnd()

      expect(wrapper.vm.draggingMenu).toBeNull()
      expect(wrapper.vm.dragParentId).toBeNull()
      expect(wrapper.vm.dragIndex).toBeNull()
    })
  })
})
