import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Safeguards from '@/views/security/Safeguards.vue'
import {
  getSafeguards,
  createSafeguard,
  updateSafeguard,
  deleteSafeguard,
  deploySafeguard,
  rollbackSafeguard,
  getSafeguardStatus
} from '@/api/security'

vi.mock('@/api/security')

describe('Safeguards 页面测试', () => {
  let wrapper

  const mockSafeguards = [
    { id: 1, name: 'test-sg-1', safeguard_type: 'safeguardx86', arch: 'x86', host: '192.168.1.1', status: 'success', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-sg-2', safeguard_type: 'safeguardx86', arch: 'arm', host: '192.168.1.2', status: 'failed', created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getSafeguards.mockResolvedValue({ results: mockSafeguards, count: 2 })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Safeguards, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getSafeguards', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getSafeguards).toHaveBeenCalled()
    })

    it('应该显示安全防护列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('test-sg-1')
      expect(wrapper.text()).toContain('test-sg-2')
      expect(wrapper.text()).toContain('192.168.1.1')
    })

    it('应该显示状态标签', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.status-success').exists()).toBe(true)
      expect(wrapper.find('.status-failed').exists()).toBe(true)
    })

    it('应该显示加载状态', async () => {
      getSafeguards.mockImplementation(() => new Promise(() => { }))
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('加载中...')
    })
  })

  describe('创建安全防护', () => {
    it('点击创建部署按钮应该打开弹窗', async () => {
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

      createSafeguard.mockResolvedValue({})

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.name = 'new-sg'
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(createSafeguard).toHaveBeenCalled()
      expect(getSafeguards).toHaveBeenCalledTimes(2)
    })

    it('名称为空时应该显示验证错误', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.name = ''
      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.name).toBe('请输入名称')
      expect(createSafeguard).not.toHaveBeenCalled()
    })

    it('创建失败时应该显示错误信息', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createSafeguard.mockRejectedValue(new Error('创建失败'))

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.name = 'new-sg'
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(wrapper.vm.formError).toBe('创建失败')
    })
  })

  describe('编辑安全防护', () => {
    it('点击编辑按钮应该打开弹窗并填充数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.form.name).toBe('test-sg-1')
    })

    it('编辑成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      updateSafeguard.mockResolvedValue({})

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updateSafeguard).toHaveBeenCalled()
      expect(getSafeguards).toHaveBeenCalledTimes(2)
    })
  })

  describe('删除安全防护', () => {
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

      deleteSafeguard.mockResolvedValue({})

      await wrapper.findAll('button.btn-danger')[0].trigger('click')
      await flushPromises()
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(deleteSafeguard).toHaveBeenCalledWith(1)
      expect(getSafeguards).toHaveBeenCalledTimes(2)
    })

    it('删除失败时应该显示 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      deleteSafeguard.mockRejectedValue(new Error('删除失败'))

      await wrapper.findAll('button.btn-danger')[0].trigger('click')
      await flushPromises()
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(window.alert).toHaveBeenCalledWith('删除失败')
    })
  })

})
