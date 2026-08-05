import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Members from '@/views/network/Members.vue'
import { getMembers, createMember, updateMember, deleteMember } from '@/api/network'

vi.mock('@/api/network')

describe('Members 页面测试', () => {
  let wrapper

  const mockMembers = [
    { id: 1, name: 'test-member-1', address: '192.168.1.10', port: 80, weight: 1, status: 'active', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-member-2', address: '192.168.1.11', port: 80, weight: 1, status: 'inactive', created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getMembers.mockResolvedValue({ results: mockMembers })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Members, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getMembers', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getMembers).toHaveBeenCalled()
    })

    it('应该显示成员列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('test-member-1')
      expect(wrapper.text()).toContain('192.168.1.10')
      expect(wrapper.text()).toContain('test-member-2')
      expect(wrapper.text()).toContain('192.168.1.11')
    })
  })

})
