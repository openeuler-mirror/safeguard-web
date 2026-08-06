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

})
