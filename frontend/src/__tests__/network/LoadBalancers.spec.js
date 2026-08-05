import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import LoadBalancers from '@/views/network/LoadBalancers.vue'
import { getLBs, createLB, updateLB, deleteLB, getLBsByProject, getLBsByK8s, getLBAzNames } from '@/api/network'

vi.mock('@/api/network')

describe('LoadBalancers 页面测试', () => {
  let wrapper

  const mockLBs = [
    { id: 1, name: 'test-lb-1', vip_address: '192.168.1.100', port: 80, algorithm: 'round_robin', status: 'active', description: 'test', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-lb-2', vip_address: '192.168.1.101', port: 443, algorithm: 'least_conn', status: 'inactive', description: 'test', created_at: '2024-01-02T00:00:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getLBs.mockResolvedValue({ results: mockLBs })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(LoadBalancers, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getLBs', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getLBs).toHaveBeenCalled()
    })

    it('应该显示负载均衡器列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('test-lb-1')
      expect(wrapper.text()).toContain('192.168.1.100')
      expect(wrapper.text()).toContain('test-lb-2')
      expect(wrapper.text()).toContain('192.168.1.101')
    })

    it('应该显示活跃/未激活状态', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.status-active').exists()).toBe(true)
      expect(wrapper.find('.status-inactive').exists()).toBe(true)
    })
  })

  describe('创建负载均衡器', () => {
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

      createLB.mockResolvedValue({})

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.name = 'new-lb'
      wrapper.vm.form.vip_address = '192.168.1.102'
      wrapper.vm.form.port = 8080

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(createLB).toHaveBeenCalled()
      expect(getLBs).toHaveBeenCalledTimes(2)
    })
  })

  describe('编辑负载均衡器', () => {
    it('点击编辑按钮应该打开弹窗并填充数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.form.name).toBe('test-lb-1')
    })

    it('编辑成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      updateLB.mockResolvedValue({})

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updateLB).toHaveBeenCalled()
      expect(getLBs).toHaveBeenCalledTimes(2)
    })
  })

  describe('删除负载均衡器', () => {
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

      deleteLB.mockResolvedValue({})

      await wrapper.findAll('button.btn-danger')[0].trigger('click')
      await flushPromises()
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(deleteLB).toHaveBeenCalledWith(1)
      expect(getLBs).toHaveBeenCalledTimes(2)
    })
  })

  describe('搜索和过滤', () => {
    it('按回车搜索应该调用 loadLBs', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const searchInput = wrapper.find('input.search-input')
      await searchInput.setValue('test')
      await searchInput.trigger('keyup.enter')
      await flushPromises()

      expect(getLBs).toHaveBeenCalledTimes(2)
    })

    it('改变过滤条件应该调用 loadLBs', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.filterStatus = 'active'
      await wrapper.vm.handleFilter()
      await flushPromises()

      expect(getLBs).toHaveBeenCalledTimes(2)
    })
  })

  describe('扩展功能', () => {
    it('点击扩展视图应该显示扩展面板', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-info')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.showExtension).toBe(true)
    })

    it('按项目查询应该调用 getLBsByProject', async () => {
      wrapper = createWrapper()
      await flushPromises()

      getLBsByProject.mockResolvedValue({ data: [] })

      wrapper.vm.extProjectId = '123'
      await wrapper.vm.handleByProject()
      await flushPromises()

      expect(getLBsByProject).toHaveBeenCalledWith('123')
    })

    it('按K8s查询应该调用 getLBsByK8s', async () => {
      wrapper = createWrapper()
      await flushPromises()

      getLBsByK8s.mockResolvedValue({ data: [] })

      wrapper.vm.extK8sCluster = 'k8s-cluster-1'
      await wrapper.vm.handleByK8s()
      await flushPromises()

      expect(getLBsByK8s).toHaveBeenCalledWith('k8s-cluster-1')
    })

    it('加载AZ列表应该调用 getLBAzNames', async () => {
      wrapper = createWrapper()
      await flushPromises()

      getLBAzNames.mockResolvedValue(['az1', 'az2'])

      await wrapper.vm.handleLoadAzNames()
      await flushPromises()

      expect(getLBAzNames).toHaveBeenCalled()
      expect(wrapper.vm.azNames).toEqual(['az1', 'az2'])
    })
  })

  describe('表单验证', () => {
    it('名称不能为空', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.name = ''
      wrapper.vm.form.vip_address = '192.168.1.1'
      wrapper.vm.form.port = 80

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.name).toBe('请输入名称')
    })

    it('VIP地址不能为空', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.name = 'test'
      wrapper.vm.form.vip_address = ''
      wrapper.vm.form.port = 80

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.vip_address).toBe('请输入VIP地址')
    })

    it('端口必须在有效范围内', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.name = 'test'
      wrapper.vm.form.vip_address = '192.168.1.1'
      wrapper.vm.form.port = 0

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.port).toBe('请输入有效端口(1-65535)')
    })
  })

  describe('空数据', () => {
    it('没有数据时应该显示空提示', async () => {
      getLBs.mockResolvedValue({ results: [] })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无数据')
    })
  })

  describe('错误处理', () => {
    it('加载失败时应该显示错误信息', async () => {
      getLBs.mockRejectedValue(new Error('加载失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe('加载失败')
      expect(wrapper.find('.error').exists()).toBe(true)
    })
  })
})
