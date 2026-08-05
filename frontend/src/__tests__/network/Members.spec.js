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

  describe('创建成员', () => {
    it('点击创建按钮应该打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
    })

    it('创建成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createMember.mockResolvedValue({})

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.name = 'new-member'
      wrapper.vm.form.address = '192.168.1.12'
      wrapper.vm.form.port = 80

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(createMember).toHaveBeenCalled()
      expect(getMembers).toHaveBeenCalledTimes(2)
    })
  })

  describe('编辑成员', () => {
    it('点击编辑按钮应该打开弹窗并填充数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(true)
    })

    it('编辑成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      updateMember.mockResolvedValue({})

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updateMember).toHaveBeenCalled()
      expect(getMembers).toHaveBeenCalledTimes(2)
    })
  })

  describe('删除成员', () => {
    it('点击删除按钮应该打开确认弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-danger')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.deleteDialogVisible).toBe(true)
    })

    it('确认删除后应该调用 API 并刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      deleteMember.mockResolvedValue({})

      await wrapper.findAll('button.btn-danger')[0].trigger('click')
      await flushPromises()
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(deleteMember).toHaveBeenCalledWith(1)
      expect(getMembers).toHaveBeenCalledTimes(2)
    })
  })

  describe('空数据', () => {
    it('没有数据时应该显示空提示', async () => {
      getMembers.mockResolvedValue({ results: [] })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无数据')
    })
  })

  describe('错误处理', () => {
    it('加载失败时应该显示错误信息', async () => {
      getMembers.mockRejectedValue(new Error('加载失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe('加载失败')
      expect(wrapper.find('.error').exists()).toBe(true)
    })
  })
})
