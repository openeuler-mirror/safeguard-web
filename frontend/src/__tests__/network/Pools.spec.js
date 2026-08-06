import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Pools from '@/views/network/Pools.vue'
import { getPools, createPool, updatePool, deletePool } from '@/api/network'

vi.mock('@/api/network')

describe('Pools 页面测试', () => {
  let wrapper

  const mockPools = [
    { id: 1, name: 'test-pool-1', protocol: 'http', algorithm: 'round_robin', description: 'test', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-pool-2', protocol: 'tcp', algorithm: 'least_conn', description: 'test', created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getPools.mockResolvedValue({ results: mockPools })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Pools, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getPools', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getPools).toHaveBeenCalled()
    })

    it('应该显示后端池列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('test-pool-1')
      expect(wrapper.text()).toContain('test-pool-2')
    })
  })

  describe('创建后端池', () => {
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

      createPool.mockResolvedValue({})

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.name = 'new-pool'
      wrapper.vm.form.protocol = 'http'

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(createPool).toHaveBeenCalled()
      expect(getPools).toHaveBeenCalledTimes(2)
    })
  })

  describe('编辑后端池', () => {
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

      updatePool.mockResolvedValue({})

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updatePool).toHaveBeenCalled()
      expect(getPools).toHaveBeenCalledTimes(2)
    })
  })

  describe('删除后端池', () => {
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

      deletePool.mockResolvedValue({})

      await wrapper.findAll('button.btn-danger')[0].trigger('click')
      await flushPromises()
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(deletePool).toHaveBeenCalledWith(1)
      expect(getPools).toHaveBeenCalledTimes(2)
    })
  })

})
