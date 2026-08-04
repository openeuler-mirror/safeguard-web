import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Clusters from '@/views/Clusters.vue'
import { getClusters, createCluster, updateCluster, deleteCluster, getClusterHosts } from '@/api/host'

vi.mock('@/api/host')

describe('Clusters 页面测试', () => {
  let wrapper

  const mockClusters = [
    { id: 1, name: 'test-cluster-1', description: 'test description', host_count: 5, created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'test-cluster-2', description: '', host_count: 3, created_at: '2024-01-02T00:00:00Z' }
  ]

  const mockHosts = [
    { id: 1, hostname: 'test-host-1', ip_address: '192.168.1.1', port: 22, status: 'online', os_type: 'CentOS 7' },
    { id: 2, hostname: 'test-host-2', ip_address: '192.168.1.2', port: 22, status: 'offline', os_type: 'Ubuntu 20.04' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getClusters.mockResolvedValue({ results: mockClusters })
    getClusterHosts.mockResolvedValue(mockHosts)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Clusters, {
      global: {
        mocks: {},
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getClusters', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getClusters).toHaveBeenCalled()
    })

    it('应该显示集群列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('test-cluster-1')
      expect(wrapper.text()).toContain('test description')
      expect(wrapper.text()).toContain('test-cluster-2')
      expect(wrapper.text()).toContain('5')
      expect(wrapper.text()).toContain('3')
    })

    it('没有描述时应该显示-', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const emptyDescriptionCells = wrapper.findAll('td').filter(td => td.text() === '-')
      expect(emptyDescriptionCells.length).toBeGreaterThan(0)
    })
  })

  describe('创建集群', () => {
    it('点击创建集群按钮应该打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
    })

    it('表单初始值应该是空的', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openCreateDialog()

      expect(wrapper.vm.form.name).toBe('')
      expect(wrapper.vm.form.description).toBe('')
      expect(wrapper.vm.form.vcenter_id).toBe('')
    })

    it('创建集群成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createCluster.mockResolvedValue({})

      await wrapper.vm.openCreateDialog()
      wrapper.vm.form.name = 'new-cluster'
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(createCluster).toHaveBeenCalledWith({ name: 'new-cluster', description: '', vcenter_id: '' })
      expect(getClusters).toHaveBeenCalledTimes(2)
    })
  })

  describe('编辑集群', () => {
    it('点击编辑按钮应该打开弹窗并填充数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.form.name).toBe('test-cluster-1')
      expect(wrapper.vm.form.description).toBe('test description')
    })

    it('编辑集群成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      updateCluster.mockResolvedValue({})

      await wrapper.vm.openEditDialog(mockClusters[0])
      wrapper.vm.form.name = 'updated-cluster'
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updateCluster).toHaveBeenCalledWith(1, { name: 'updated-cluster', description: 'test description', vcenter_id: '' })
      expect(getClusters).toHaveBeenCalledTimes(2)
    })
  })

  describe('删除集群', () => {
    it('点击删除按钮应该打开确认弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-delete')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.deleteDialogVisible).toBe(true)
      expect(wrapper.vm.selectedCluster.name).toBe('test-cluster-1')
    })

    it('确认删除后应该调用 API 并刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      deleteCluster.mockResolvedValue({})
      vi.spyOn(window, 'alert').mockImplementation(() => { })

      await wrapper.vm.confirmDelete(mockClusters[0])
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(deleteCluster).toHaveBeenCalledWith(1)
      expect(getClusters).toHaveBeenCalledTimes(2)
    })

    it('点击取消应该关闭弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.confirmDelete(mockClusters[0])
      await wrapper.vm.closeDeleteDialog()

      expect(wrapper.vm.deleteDialogVisible).toBe(false)
    })
  })

  describe('查看主机列表', () => {
    it('点击主机按钮应该打开主机列表弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-info')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.hostDialogVisible).toBe(true)
      expect(wrapper.vm.selectedCluster.name).toBe('test-cluster-1')
    })

    it('打开主机列表弹窗应该调用 getClusterHosts', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openHostDialog(mockClusters[0])
      await flushPromises()

      expect(getClusterHosts).toHaveBeenCalledWith(1)
    })

    it('主机列表应该正确显示', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openHostDialog(mockClusters[0])
      await flushPromises()

      expect(wrapper.vm.clusterHosts).toEqual(mockHosts)
    })

    it('关闭主机列表弹窗应该清空数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openHostDialog(mockClusters[0])
      await wrapper.vm.closeHostDialog()

      expect(wrapper.vm.hostDialogVisible).toBe(false)
      expect(wrapper.vm.clusterHosts).toEqual([])
    })
  })

  describe('搜索功能', () => {
    it('按回车搜索应该调用 loadClusters', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const searchInput = wrapper.find('input.search-input')
      await searchInput.setValue('test')
      await searchInput.trigger('keyup.enter')
      await flushPromises()

      expect(getClusters).toHaveBeenCalledTimes(2)
    })
  })

  describe('表单验证', () => {
    it('集群名称不能为空', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openCreateDialog()
      wrapper.vm.form.name = ''
      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.name).toBe('请输入集群名称')
    })

    it('集群名称为空时不调用 API', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openCreateDialog()
      wrapper.vm.form.name = ''
      await wrapper.vm.submitForm()

      expect(createCluster).not.toHaveBeenCalled()
    })
  })

  describe('空数据', () => {
    it('没有集群数据时应该显示空提示', async () => {
      getClusters.mockResolvedValue({ results: [] })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无数据')
    })

    it('集群下没有主机时应该显示空提示', async () => {
      getClusterHosts.mockResolvedValue([])
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openHostDialog(mockClusters[0])
      await flushPromises()

      expect(wrapper.vm.clusterHosts).toEqual([])
    })
  })

  describe('错误处理', () => {
    it('加载失败时应该显示错误信息', async () => {
      getClusters.mockRejectedValue(new Error('加载失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe('加载失败')
      expect(wrapper.find('.error').exists()).toBe(true)
    })

    it('加载主机列表失败时应该显示 alert', async () => {
      getClusterHosts.mockRejectedValue(new Error('加载主机失败'))
      vi.spyOn(window, 'alert').mockImplementation(() => { })

      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openHostDialog(mockClusters[0])
      await flushPromises()

      expect(window.alert).toHaveBeenCalledWith('加载主机列表失败')
    })

    it('删除失败时应该显示 alert', async () => {
      deleteCluster.mockRejectedValue(new Error('删除失败'))
      vi.spyOn(window, 'alert').mockImplementation(() => { })

      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.confirmDelete(mockClusters[0])
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(window.alert).toHaveBeenCalledWith('删除失败')
    })
  })

  describe('日期格式化', () => {
    it('formatDate 应该正确格式化日期', async () => {
      wrapper = createWrapper()
      const dateStr = '2024-01-01T00:00:00Z'
      const formatted = wrapper.vm.formatDate(dateStr)

      expect(formatted).toBeTruthy()
      expect(typeof formatted).toBe('string')
    })

    it('formatDate 空值返回-', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatDate(null)).toBe('-')
      expect(wrapper.vm.formatDate('')).toBe('-')
    })
  })

  describe('弹窗关闭', () => {
    it('关闭创建/编辑弹窗应该清空错误', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.formError = 'test error'
      wrapper.vm.errors = { name: 'test' }
      await wrapper.vm.closeDialog()

      expect(wrapper.vm.formError).toBe('')
      expect(wrapper.vm.errors).toEqual({})
    })
  })
})
