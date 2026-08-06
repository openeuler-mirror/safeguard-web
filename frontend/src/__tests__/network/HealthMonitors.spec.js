import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HealthMonitors from '@/views/network/HealthMonitors.vue'
import { getHealthMonitors, createHealthMonitor, updateHealthMonitor, deleteHealthMonitor, getPools } from '@/api/network'

vi.mock('@/api/network')

describe('HealthMonitors 页面测试', () => {
  let wrapper

  const mockHealthMonitors = [
    { id: 1, pool_name: 'pool-1', monitor_type: 'http', interval: 5, timeout: 3, retry: 3, description: 'test', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, pool_name: 'pool-2', monitor_type: 'tcp', interval: 10, timeout: 5, retry: 5, description: 'test', created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getHealthMonitors.mockResolvedValue({ results: mockHealthMonitors })
    getPools.mockResolvedValue({ results: [] })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HealthMonitors, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getHealthMonitors 和 getPools', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getHealthMonitors).toHaveBeenCalled()
      expect(getPools).toHaveBeenCalled()
    })
  })

  describe('创建健康检查', () => {
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

      createHealthMonitor.mockResolvedValue({})

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.pool = '1'

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(createHealthMonitor).toHaveBeenCalled()
      expect(getHealthMonitors).toHaveBeenCalledTimes(2)
    })
  })

  describe('编辑健康检查', () => {
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

      updateHealthMonitor.mockResolvedValue({})

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      wrapper.vm.form.pool = '1'

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updateHealthMonitor).toHaveBeenCalled()
      expect(getHealthMonitors).toHaveBeenCalledTimes(2)
    })
  })

  describe('删除健康检查', () => {
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

      deleteHealthMonitor.mockResolvedValue({})

      await wrapper.findAll('button.btn-danger')[0].trigger('click')
      await flushPromises()
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(deleteHealthMonitor).toHaveBeenCalledWith(1)
      expect(getHealthMonitors).toHaveBeenCalledTimes(2)
    })
  })

  describe('空数据', () => {
    it('没有数据时应该显示空提示', async () => {
      getHealthMonitors.mockResolvedValue({ results: [] })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无数据')
    })
  })

  describe('错误处理', () => {
    it('加载失败时应该显示错误信息', async () => {
      getHealthMonitors.mockRejectedValue(new Error('加载失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBeTruthy()
      expect(wrapper.find('.error').exists()).toBe(true)
    })
  })
})
