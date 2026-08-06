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

})
