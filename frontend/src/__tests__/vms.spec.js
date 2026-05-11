import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import VMs from '@/views/VMs.vue'

// Mock API
vi.mock('@/api/host', () => ({
  getVMs: vi.fn(),
  createVM: vi.fn(),
  updateVM: vi.fn(),
  deleteVM: vi.fn(),
  startVM: vi.fn(),
  stopVM: vi.fn(),
  rebootVM: vi.fn(),
  getClusterTree: vi.fn(),
  getHosts: vi.fn()
}))

import { getVMs, createVM, updateVM, deleteVM, startVM, stopVM, rebootVM, getClusterTree, getHosts } from '@/api/host'

const createWrapper = () => {
  return mount(VMs, {
    global: {
      stubs: {
        'router-link': true,
        router: { push: vi.fn() }
      }
    }
  })
}

describe('VMs.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('UI 渲染', () => {
    it('渲染标题', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('虚拟机管理')
    })

    it('渲染创建按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.btn-primary').text()).toBe('创建虚拟机')
    })

    it('渲染集群筛选下拉框', () => {
      const wrapper = createWrapper()
      expect(wrapper.findAll('.filter-select').length).toBeGreaterThan(0)
    })

    it('渲染搜索输入框', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.search-input').exists()).toBe(true)
    })
  })

  describe('数据加载', () => {
    it('加载时显示 loading', async () => {
      getVMs.mockImplementation(() => new Promise(() => {}))
      getClusterTree.mockResolvedValue([])
      getHosts.mockResolvedValue([])

      const wrapper = createWrapper()
      wrapper.vm.loading = true

      expect(wrapper.find('.loading').exists()).toBe(true)
    })

    it('加载失败时显示错误信息', async () => {
      const wrapper = createWrapper()
      wrapper.vm.error = '加载失败'
      wrapper.vm.loading = false

      expect(wrapper.find('.error').text()).toBe('加载失败')
    })

    it('无数据时显示暂无数据', async () => {
      getVMs.mockResolvedValue([])
      getClusterTree.mockResolvedValue([])
      getHosts.mockResolvedValue([])

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.empty-text').exists()).toBe(true)
    })
  })

  describe('表格渲染', () => {
    it('正确显示VM数据', async () => {
      const mockVMs = [{
        id: 1,
        name: 'test-vm',
        uuid: '123-456-789',
        host: 1,
        host_name: 'host1',
        cluster: 1,
        cluster_name: 'cluster1',
        status: 'running',
        vcpu: 4,
        memory: 8589934592,
        disk: 107374182400,
        ip_address: '192.168.1.100',
        mac_address: '00:0c:29:ab:cd:ef',
        os_type: 'CentOS 7.9',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getVMs.mockResolvedValue({ results: mockVMs })
      getClusterTree.mockResolvedValue([])
      getHosts.mockResolvedValue([])

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(1)
      expect(rows[0].find('td:nth-child(2)').text()).toBe('test-vm')
    })

    it('UUID使用等宽字体显示', async () => {
      const mockVMs = [{
        id: 1,
        name: 'test-vm',
        uuid: '123-456-789',
        host: 1,
        host_name: 'host1',
        cluster: null,
        cluster_name: null,
        status: 'stopped',
        vcpu: 2,
        memory: 4294967296,
        disk: 53687091200,
        ip_address: null,
        mac_address: null,
        os_type: null,
        created_at: '2026-01-01T00:00:00Z'
      }]

      getVMs.mockResolvedValue({ results: mockVMs })
      getClusterTree.mockResolvedValue([])
      getHosts.mockResolvedValue([])

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const uuidCell = wrapper.find('.uuid-text')
      expect(uuidCell.exists()).toBe(true)
    })
  })

  describe('状态显示', () => {
    it('运行中状态显示绿色', async () => {
      const mockVMs = [{
        id: 1,
        name: 'vm1',
        uuid: 'uuid1',
        host: 1,
        host_name: 'host1',
        cluster: null,
        cluster_name: null,
        status: 'running',
        vcpu: 1,
        memory: 0,
        disk: 0,
        created_at: '2026-01-01T00:00:00Z'
      }]

      getVMs.mockResolvedValue({ results: mockVMs })
      getClusterTree.mockResolvedValue([])
      getHosts.mockResolvedValue([])

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const statusSpan = wrapper.find('.status-running')
      expect(statusSpan.exists()).toBe(true)
      expect(statusSpan.text()).toBe('运行中')
    })

    it('已停止状态显示灰色', async () => {
      const mockVMs = [{
        id: 1,
        name: 'vm1',
        uuid: 'uuid1',
        host: 1,
        host_name: 'host1',
        cluster: null,
        cluster_name: null,
        status: 'stopped',
        vcpu: 1,
        memory: 0,
        disk: 0,
        created_at: '2026-01-01T00:00:00Z'
      }]

      getVMs.mockResolvedValue({ results: mockVMs })
      getClusterTree.mockResolvedValue([])
      getHosts.mockResolvedValue([])

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const statusSpan = wrapper.find('.status-stopped')
      expect(statusSpan.exists()).toBe(true)
      expect(statusSpan.text()).toBe('已停止')
    })

    it('暂停状态显示橙色', async () => {
      const mockVMs = [{
        id: 1,
        name: 'vm1',
        uuid: 'uuid1',
        host: 1,
        host_name: 'host1',
        cluster: null,
        cluster_name: null,
        status: 'paused',
        vcpu: 1,
        memory: 0,
        disk: 0,
        created_at: '2026-01-01T00:00:00Z'
      }]

      getVMs.mockResolvedValue({ results: mockVMs })
      getClusterTree.mockResolvedValue([])
      getHosts.mockResolvedValue([])

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const statusSpan = wrapper.find('.status-paused')
      expect(statusSpan.exists()).toBe(true)
      expect(statusSpan.text()).toBe('暂停')
    })

    it('挂起状态显示红色', async () => {
      const mockVMs = [{
        id: 1,
        name: 'vm1',
        uuid: 'uuid1',
        host: 1,
        host_name: 'host1',
        cluster: null,
        cluster_name: null,
        status: 'suspended',
        vcpu: 1,
        memory: 0,
        disk: 0,
        created_at: '2026-01-01T00:00:00Z'
      }]

      getVMs.mockResolvedValue({ results: mockVMs })
      getClusterTree.mockResolvedValue([])
      getHosts.mockResolvedValue([])

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const statusSpan = wrapper.find('.status-suspended')
      expect(statusSpan.exists()).toBe(true)
      expect(statusSpan.text()).toBe('挂起')
    })
  })

  describe('操作按钮', () => {
    it('运行中的VM显示停止和重启按钮', async () => {
      const mockVMs = [{
        id: 1,
        name: 'vm1',
        uuid: 'uuid1',
        host: 1,
        host_name: 'host1',
        cluster: null,
        cluster_name: null,
        status: 'running',
        vcpu: 1,
        memory: 0,
        disk: 0,
        created_at: '2026-01-01T00:00:00Z'
      }]

      getVMs.mockResolvedValue({ results: mockVMs })
      getClusterTree.mockResolvedValue([])
      getHosts.mockResolvedValue([])

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const buttons = wrapper.findAll('.btn-action')
      expect(buttons.length).toBe(2)
    })

    it('已停止的VM显示启动按钮', async () => {
      const mockVMs = [{
        id: 1,
        name: 'vm1',
        uuid: 'uuid1',
        host: 1,
        host_name: 'host1',
        cluster: null,
        cluster_name: null,
        status: 'stopped',
        vcpu: 1,
        memory: 0,
        disk: 0,
        created_at: '2026-01-01T00:00:00Z'
      }]

      getVMs.mockResolvedValue({ results: mockVMs })
      getClusterTree.mockResolvedValue([])
      getHosts.mockResolvedValue([])

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const startButton = wrapper.find('.btn-start')
      expect(startButton.exists()).toBe(true)
    })
  })

  describe('表单验证', () => {
    it('创建弹窗中必填字段验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.isEdit = false
      wrapper.vm.form = {
        name: '',
        uuid: '',
        host: null,
        cluster: null,
        status: 'stopped',
        vcpu: 1,
        memory: 0,
        disk: 0,
        ip_address: '',
        mac_address: '',
        os_type: ''
      }

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.name).toBe('请输入VM名称')
      expect(wrapper.vm.errors.uuid).toBe('请输入UUID')
      expect(wrapper.vm.errors.host).toBe('请选择宿主机')
    })

    it('编辑弹窗正确填充数据', async () => {
      const mockVMs = [{
        id: 1,
        name: 'vm1',
        uuid: 'uuid1',
        host: 1,
        host_name: 'host1',
        cluster: 1,
        cluster_name: 'cluster1',
        status: 'running',
        vcpu: 4,
        memory: 8589934592,
        disk: 107374182400,
        ip_address: '192.168.1.100',
        mac_address: '00:0c:29:ab:cd:ef',
        os_type: 'CentOS 7.9',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getVMs.mockResolvedValue({ data: { results: mockVMs } })
      getClusterTree.mockResolvedValue({ data: [] })
      getHosts.mockResolvedValue({ data: [] })

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openEditDialog(mockVMs[0])

      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.form.name).toBe('vm1')
      expect(wrapper.vm.form.uuid).toBe('uuid1')
      expect(wrapper.vm.form.vcpu).toBe(4)
    })
  })

  describe('VM操作', () => {
    it('启动VM调用 startVM API', async () => {
      const wrapper = createWrapper()
      const mockVM = { id: 1, name: 'vm1', status: 'stopped' }

      startVM.mockResolvedValue({ data: {} })
      await wrapper.vm.handleStart(mockVM)

      expect(startVM).toHaveBeenCalledWith(1)
    })

    it('停止VM调用 stopVM API', async () => {
      const wrapper = createWrapper()
      const mockVM = { id: 1, name: 'vm1', status: 'running' }

      stopVM.mockResolvedValue({ data: {} })
      await wrapper.vm.handleStop(mockVM)

      expect(stopVM).toHaveBeenCalledWith(1)
    })

    it('重启VM调用 rebootVM API', async () => {
      const wrapper = createWrapper()
      const mockVM = { id: 1, name: 'vm1', status: 'running' }

      rebootVM.mockResolvedValue({ data: {} })
      await wrapper.vm.handleReboot(mockVM)

      expect(rebootVM).toHaveBeenCalledWith(1)
    })

    it('删除VM调用 deleteVM API', async () => {
      const wrapper = createWrapper()
      const mockVM = { id: 1, name: 'vm1' }

      deleteVM.mockResolvedValue({ data: {} })
      await wrapper.vm.handleDelete()

      expect(deleteVM).toHaveBeenCalledWith(1)
    })
  })

  describe('工具方法', () => {
    it('formatBytes 正确转换字节到GB', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatBytes(107374182400)).toBe('100.00 GB')
    })

    it('formatBytes 正确转换字节到MB', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatBytes(52428800)).toBe('50.00 MB')
    })

    it('formatBytes 处理0值', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatBytes(0)).toBe('-')
    })

    it('formatBytes 处理null值', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatBytes(null)).toBe('-')
    })

    it('getStatusText 返回正确的中文状态', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.getStatusText('running')).toBe('运行中')
      expect(wrapper.vm.getStatusText('stopped')).toBe('已停止')
      expect(wrapper.vm.getStatusText('paused')).toBe('暂停')
      expect(wrapper.vm.getStatusText('suspended')).toBe('挂起')
    })

    it('formatDate 正确格式化日期', () => {
      const wrapper = createWrapper()
      const result = wrapper.vm.formatDate('2026-01-15T10:30:00Z')
      expect(result).toContain('2026')
    })

    it('formatDate 处理空值', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatDate('')).toBe('-')
      expect(wrapper.vm.formatDate(null)).toBe('-')
    })
  })

  describe('对话框', () => {
    it('创建对话框正确初始化', async () => {
      getVMs.mockResolvedValue([])
      getClusterTree.mockResolvedValue([])
      getHosts.mockResolvedValue([])

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openCreateDialog()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
      expect(wrapper.vm.form.name).toBe('')
      expect(wrapper.vm.form.status).toBe('stopped')
    })

    it('关闭对话框清空错误', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.formError = 'some error'
      wrapper.vm.errors = { name: 'error' }

      await wrapper.vm.closeDialog()

      expect(wrapper.vm.dialogVisible).toBe(false)
      expect(wrapper.vm.formError).toBe('')
      expect(wrapper.vm.errors).toEqual({})
    })

    it('删除确认对话框设置正确', async () => {
      const wrapper = createWrapper()
      const mockVM = { id: 1, name: 'vm1' }

      wrapper.vm.confirmDelete(mockVM)

      expect(wrapper.vm.deleteDialogVisible).toBe(true)
      expect(wrapper.vm.selectedVM).toEqual(mockVM)
    })
  })
})
