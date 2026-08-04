import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Hosts from '@/views/Hosts.vue'
import { getHosts, createHost, updateHost, deleteHost, getClusterTree } from '@/api/host'

vi.mock('@/api/host')

const mockPush = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => ({})
}))

describe('Hosts 页面测试', () => {
  let wrapper

  const mockHosts = [
    { id: 1, hostname: 'test-host-1', ip_address: '192.168.1.1', port: 22, username: 'root', status: 'online', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, hostname: 'test-host-2', ip_address: '192.168.1.2', port: 22, username: 'root', status: 'offline', created_at: '2024-01-02T00:00:00Z' }
  ]

  const mockClusters = [
    { id: 1, name: 'test-cluster-1' },
    { id: 2, name: 'test-cluster-2' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    getHosts.mockResolvedValue({ results: mockHosts })
    getClusterTree.mockResolvedValue(mockClusters)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Hosts, {
      global: {
        mocks: {
          $router: {
            push: mockPush
          }
        },
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getHosts 和 getClusterTree', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getHosts).toHaveBeenCalled()
      expect(getClusterTree).toHaveBeenCalled()
    })

    it('应该显示主机列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('test-host-1')
      expect(wrapper.text()).toContain('192.168.1.1')
      expect(wrapper.text()).toContain('test-host-2')
      expect(wrapper.text()).toContain('192.168.1.2')
    })

    it('应该显示在线/离线状态', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.status-online').exists()).toBe(true)
      expect(wrapper.find('.status-offline').exists()).toBe(true)
    })
  })

  describe('创建主机', () => {
    it('点击创建主机按钮应该打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
    })

    it('创建主机成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createHost.mockResolvedValue({})

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.hostname = 'new-host'
      wrapper.vm.form.ip_address = '192.168.1.3'
      wrapper.vm.form.username = 'root'

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(createHost).toHaveBeenCalled()
      expect(getHosts).toHaveBeenCalledTimes(2)
    })
  })

  describe('编辑主机', () => {
    it('点击编辑按钮应该打开弹窗并填充数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.form.hostname).toBe('test-host-1')
    })

    it('编辑主机成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      updateHost.mockResolvedValue({})

      await wrapper.findAll('button.btn-edit')[0].trigger('click')
      await flushPromises()

      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updateHost).toHaveBeenCalled()
      expect(getHosts).toHaveBeenCalledTimes(2)
    })
  })

  describe('删除主机', () => {
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

      deleteHost.mockResolvedValue({})
      vi.spyOn(window, 'alert').mockImplementation(() => { })

      await wrapper.findAll('button.btn-danger')[0].trigger('click')
      await flushPromises()
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(deleteHost).toHaveBeenCalledWith(1)
      expect(getHosts).toHaveBeenCalledTimes(2)
    })
  })

  describe('搜索和过滤', () => {
    it('按回车搜索应该调用 loadHosts', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.searchName = 'test'
      const searchInput = wrapper.find('input.search-input')
      await searchInput.setValue('test')
      await searchInput.trigger('keyup.enter')
      await flushPromises()

      expect(getHosts).toHaveBeenCalledWith({ search: 'test' })
    })

    it('改变过滤条件应该调用 loadHosts', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.filterStatus = 'online'
      await wrapper.vm.handleFilter()
      await flushPromises()

      expect(getHosts).toHaveBeenCalledWith({ status: 'online' })
    })
  })

  describe('导航到主机详情', () => {
    it('点击详情按钮应该跳转到主机详情页', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.goToHostDetail(mockHosts[0])

      expect(mockPush).toHaveBeenCalledWith('/hosts/1/dashboard')
    })
  })

  describe('表单验证', () => {
    it('主机名不能为空', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.hostname = ''
      wrapper.vm.form.ip_address = '192.168.1.1'
      wrapper.vm.form.username = 'root'

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.hostname).toBe('请输入主机名')
    })

    it('IP地址不能为空', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.hostname = 'test'
      wrapper.vm.form.ip_address = ''
      wrapper.vm.form.username = 'root'

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.ip_address).toBe('请输入IP地址')
    })

    it('用户名不能为空', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-primary').trigger('click')
      await flushPromises()

      wrapper.vm.form.hostname = 'test'
      wrapper.vm.form.ip_address = '192.168.1.1'
      wrapper.vm.form.username = ''

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.username).toBe('请输入用户名')
    })
  })

  describe('空数据', () => {
    it('没有数据时应该显示空提示', async () => {
      getHosts.mockResolvedValue({ results: [] })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无数据')
    })
  })

  describe('错误处理', () => {
    it('加载失败时应该显示错误信息', async () => {
      getHosts.mockRejectedValue(new Error('加载失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe('加载失败')
      expect(wrapper.find('.error').exists()).toBe(true)
    })
  })
})
