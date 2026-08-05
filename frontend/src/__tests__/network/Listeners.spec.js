import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Listeners from '@/views/network/Listeners.vue'
import { getListeners, createListener, updateListener, deleteListener } from '@/api/network'

vi.mock('@/api/network')

describe('Listeners 页面测试', () => {
  let wrapper

  const mockListeners = [
    { id: 1, name: 'test-listener-1', loadbalancer_name: 'lb-1', protocol: 'http', port: 80, description: 'test', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-listener-2', loadbalancer_name: 'lb-2', protocol: 'https', port: 443, description: 'test', created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getListeners.mockResolvedValue({ results: mockListeners })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Listeners, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getListeners', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getListeners).toHaveBeenCalled()
    })

    it('应该显示监听器列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('test-listener-1')
      expect(wrapper.text()).toContain('lb-1')
      expect(wrapper.text()).toContain('test-listener-2')
      expect(wrapper.text()).toContain('lb-2')
    })

    it('应该显示协议类型', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('HTTP')
      expect(wrapper.text()).toContain('HTTPS')
    })
  })

  describe('创建监听器', () => {
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

      createListener.mockResolvedValue({})

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.loadbalancer = '1'
      wrapper.vm.form.protocol = 'tcp'
      wrapper.vm.form.port = 8080

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(createListener).toHaveBeenCalled()
      expect(getListeners).toHaveBeenCalledTimes(2)
    })
  })

  describe('编辑监听器', () => {
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

      updateListener.mockResolvedValue({})

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updateListener).toHaveBeenCalled()
      expect(getListeners).toHaveBeenCalledTimes(2)
    })
  })

  describe('删除监听器', () => {
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

      deleteListener.mockResolvedValue({})

      await wrapper.findAll('button.btn-danger')[0].trigger('click')
      await flushPromises()
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(deleteListener).toHaveBeenCalledWith(1)
      expect(getListeners).toHaveBeenCalledTimes(2)
    })
  })

  describe('搜索和过滤', () => {
    it('按回车搜索应该调用 loadListeners', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const searchInput = wrapper.find('input.search-input')
      await searchInput.setValue('test')
      await searchInput.trigger('keyup.enter')
      await flushPromises()

      expect(getListeners).toHaveBeenCalledTimes(2)
    })
  })

  describe('空数据', () => {
    it('没有数据时应该显示空提示', async () => {
      getListeners.mockResolvedValue({ results: [] })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无数据')
    })
  })

  describe('错误处理', () => {
    it('加载失败时应该显示错误信息', async () => {
      getListeners.mockRejectedValue(new Error('加载失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe('加载失败')
      expect(wrapper.find('.error').exists()).toBe(true)
    })
  })
})
