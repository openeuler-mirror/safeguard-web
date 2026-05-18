import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import PXEConfig from '@/views/osdeploy/PXEConfig.vue'

// Mock API
vi.mock('@/api/osdeploy/pxe', () => ({
  getPXEServers: vi.fn(),
  createPXEServer: vi.fn(),
  updatePXEServer: vi.fn(),
  deletePXEServer: vi.fn()
}))

import {
  getPXEServers,
  createPXEServer,
  updatePXEServer,
  deletePXEServer
} from '@/api/osdeploy/pxe'

const createWrapper = () => {
  return mount(PXEConfig, {
    global: {
      stubs: {
        'router-link': true,
        router: { push: vi.fn() }
      }
    }
  })
}

describe('PXEConfig.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('UI 渲染', () => {
    it('渲染标题', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('PXE 服务器配置')
    })

    it('渲染添加服务器按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.btn-primary').text()).toBe('添加服务器')
    })
  })

  describe('数据加载', () => {
    it('加载时显示 loading', async () => {
      getPXEServers.mockImplementation(() => new Promise(() => {}))
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
      getPXEServers.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.empty-text').exists()).toBe(true)
    })
  })

  describe('表格渲染', () => {
    it('正确显示PXE服务器数据', async () => {
      const mockServers = [{
        id: 1,
        server_ip: '192.168.1.100',
        interface: 'eth0',
        dhcp_range_start: '192.168.1.10',
        dhcp_range_end: '192.168.1.200',
        status: 'active',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getPXEServers.mockResolvedValue({ results: mockServers, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(1)
      expect(rows[0].find('td:nth-child(2)').text()).toBe('192.168.1.100')
    })

    it('显示网卡信息', async () => {
      const mockServers = [{
        id: 1,
        server_ip: '192.168.1.100',
        interface: 'eth1',
        dhcp_range_start: '192.168.1.10',
        dhcp_range_end: '192.168.1.200',
        status: 'active',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getPXEServers.mockResolvedValue({ results: mockServers, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('td:nth-child(3)').text()).toBe('eth1')
    })
  })

  describe('状态显示', () => {
    it('active 状态显示绿色', async () => {
      const mockServers = [{
        id: 1,
        server_ip: '192.168.1.100',
        interface: 'eth0',
        dhcp_range_start: '192.168.1.10',
        dhcp_range_end: '192.168.1.200',
        status: 'active',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getPXEServers.mockResolvedValue({ results: mockServers, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const statusSpan = wrapper.find('.status-active')
      expect(statusSpan.exists()).toBe(true)
      expect(statusSpan.text()).toBe('活跃')
    })

    it('inactive 状态显示灰色', async () => {
      const mockServers = [{
        id: 1,
        server_ip: '192.168.1.100',
        interface: 'eth0',
        dhcp_range_start: '192.168.1.10',
        dhcp_range_end: '192.168.1.200',
        status: 'inactive',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getPXEServers.mockResolvedValue({ results: mockServers, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const statusSpan = wrapper.find('.status-inactive')
      expect(statusSpan.exists()).toBe(true)
      expect(statusSpan.text()).toBe('未激活')
    })
  })

  describe('操作按钮', () => {
    it('显示编辑、删除按钮', async () => {
      const mockServers = [{
        id: 1,
        server_ip: '192.168.1.100',
        interface: 'eth0',
        dhcp_range_start: '192.168.1.10',
        dhcp_range_end: '192.168.1.200',
        status: 'active',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getPXEServers.mockResolvedValue({ results: mockServers, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.findAll('.btn-edit').length).toBe(1)
      expect(wrapper.findAll('.btn-danger').length).toBe(1)
    })
  })

  describe('创建/编辑弹窗', () => {
    it('创建弹窗正确初始化', async () => {
      getPXEServers.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openCreateDialog()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
      expect(wrapper.vm.form.server_ip).toBe('')
      expect(wrapper.vm.form.interface).toBe('eth0')
    })

    it('编辑弹窗正确填充数据', async () => {
      const mockServers = [{
        id: 1,
        server_ip: '192.168.1.100',
        interface: 'eth1',
        dhcp_range_start: '192.168.1.50',
        dhcp_range_end: '192.168.1.150',
        status: 'inactive',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getPXEServers.mockResolvedValue({ results: mockServers, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openEditDialog(mockServers[0])

      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.selectedServer).toEqual(mockServers[0])
      expect(wrapper.vm.form.server_ip).toBe('192.168.1.100')
      expect(wrapper.vm.form.interface).toBe('eth1')
    })

    it('关闭弹窗清空错误', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.formError = 'some error'
      wrapper.vm.errors = { server_ip: 'error' }

      await wrapper.vm.closeDialog()

      expect(wrapper.vm.dialogVisible).toBe(false)
      expect(wrapper.vm.formError).toBe('')
      expect(wrapper.vm.errors).toEqual({})
    })
  })

  describe('表单验证', () => {
    it('服务器IP必填验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.server_ip = ''
      wrapper.vm.form.interface = 'eth0'
      wrapper.vm.form.dhcp_range_start = '192.168.1.10'
      wrapper.vm.form.dhcp_range_end = '192.168.1.200'

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.server_ip).toBe('请输入服务器IP')
    })

    it('网卡必填验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.server_ip = '192.168.1.100'
      wrapper.vm.form.interface = ''
      wrapper.vm.form.dhcp_range_start = '192.168.1.10'
      wrapper.vm.form.dhcp_range_end = '192.168.1.200'

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.interface).toBe('请输入网卡名称')
    })

    it('DHCP起始IP必填验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.server_ip = '192.168.1.100'
      wrapper.vm.form.interface = 'eth0'
      wrapper.vm.form.dhcp_range_start = ''
      wrapper.vm.form.dhcp_range_end = '192.168.1.200'

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.dhcp_range_start).toBe('请输入DHCP起始IP')
    })

    it('DHCP结束IP必填验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.server_ip = '192.168.1.100'
      wrapper.vm.form.interface = 'eth0'
      wrapper.vm.form.dhcp_range_start = '192.168.1.10'
      wrapper.vm.form.dhcp_range_end = ''

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.dhcp_range_end).toBe('请输入DHCP结束IP')
    })

    it('验证通过调用创建API', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.isEdit = false
      wrapper.vm.form = {
        server_ip: '192.168.1.100',
        interface: 'eth0',
        dhcp_range_start: '192.168.1.10',
        dhcp_range_end: '192.168.1.200',
        status: 'active'
      }
      createPXEServer.mockResolvedValue({})

      await wrapper.vm.submitForm()

      expect(createPXEServer).toHaveBeenCalled()
    })

    it('验证通过调用更新API', async () => {
      const mockServers = [{
        id: 1,
        server_ip: '192.168.1.100',
        interface: 'eth0',
        dhcp_range_start: '192.168.1.10',
        dhcp_range_end: '192.168.1.200',
        status: 'active',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getPXEServers.mockResolvedValue({ results: mockServers, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.openEditDialog(mockServers[0])
      wrapper.vm.isEdit = true
      updatePXEServer.mockResolvedValue({})

      await wrapper.vm.submitForm()

      expect(updatePXEServer).toHaveBeenCalledWith(1, expect.any(Object))
    })
  })

  describe('删除操作', () => {
    it('确认删除对话框设置正确', async () => {
      const mockServers = [{
        id: 1,
        server_ip: '192.168.1.100',
        interface: 'eth0',
        dhcp_range_start: '192.168.1.10',
        dhcp_range_end: '192.168.1.200',
        status: 'active',
        created_at: '2026-01-01T00:00:00Z'
      }]

      const wrapper = createWrapper()
      await wrapper.vm.confirmDelete(mockServers[0])

      expect(wrapper.vm.deleteDialogVisible).toBe(true)
      expect(wrapper.vm.selectedServer).toEqual(mockServers[0])
    })

    it('删除成功后刷新列表', async () => {
      getPXEServers.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      wrapper.vm.selectedServer = { id: 1, server_ip: '192.168.1.100' }
      deletePXEServer.mockResolvedValue({})

      await wrapper.vm.handleDelete()

      expect(deletePXEServer).toHaveBeenCalledWith(1)
      expect(wrapper.vm.deleteDialogVisible).toBe(false)
    })
  })

  describe('工具方法', () => {
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

    it('formatStatus 返回正确的状态中文', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatStatus('active')).toBe('活跃')
      expect(wrapper.vm.formatStatus('inactive')).toBe('未激活')
    })

    it('getStatusClass 返回正确的样式类', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.getStatusClass('active')).toBe('status-active')
      expect(wrapper.vm.getStatusClass('inactive')).toBe('status-inactive')
    })
  })

  describe('分页', () => {
    it('正确计算总页数', () => {
      const wrapper = createWrapper()
      wrapper.vm.totalCount = 45
      wrapper.vm.pageSize = 20
      expect(wrapper.vm.totalPages).toBe(3)
    })

    it('总页数为0时返回1', () => {
      const wrapper = createWrapper()
      wrapper.vm.totalCount = 0
      wrapper.vm.pageSize = 20
      expect(wrapper.vm.totalPages).toBe(1)
    })
  })

  describe('页码切换', () => {
    it('handlePageChange 更改页码', async () => {
      getPXEServers.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()

      await wrapper.vm.handlePageChange(3)

      expect(wrapper.vm.page).toBe(3)
    })
  })
})