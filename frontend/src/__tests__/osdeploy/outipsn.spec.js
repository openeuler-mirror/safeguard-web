import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import OutIpSN from '@/views/osdeploy/OutIpSN.vue'

// Mock API
vi.mock('@/api/osdeploy/outipsn', () => ({
  getOutIpSNs: vi.fn(),
  createOutIpSN: vi.fn(),
  updateOutIpSN: vi.fn(),
  deleteOutIpSN: vi.fn()
}))

import {
  getOutIpSNs,
  createOutIpSN,
  updateOutIpSN,
  deleteOutIpSN
} from '@/api/osdeploy/outipsn'

const createWrapper = () => {
  return mount(OutIpSN, {
    global: {
      stubs: {
        'router-link': true,
        router: { push: vi.fn() }
      }
    }
  })
}

describe('OutIpSN.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getOutIpSNs.mockResolvedValue({ results: [], count: 0 })
  })

  describe('UI 渲染', () => {
    it('渲染添加记录按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.btn-primary').text()).toBe('添加记录')
    })
  })

  describe('数据加载', () => {
    it('加载时显示 loading', async () => {
      getOutIpSNs.mockImplementation(() => new Promise(() => {}))
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
      getOutIpSNs.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.empty-text').exists()).toBe(true)
    })
  })

  describe('表格渲染', () => {
    it('正确显示出口IP数据', async () => {
      const mockOutIpSNs = [{
        id: 1,
        mac_address: '00:11:22:33:44:55',
        sn: 'SN-001-2026',
        description: 'Test device',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getOutIpSNs.mockResolvedValue({ results: mockOutIpSNs, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(1)
      expect(rows[0].find('td:nth-child(2)').text()).toBe('00:11:22:33:44:55')
    })

    it('正确显示序列号', async () => {
      const mockOutIpSNs = [{
        id: 1,
        mac_address: '00:11:22:33:44:55',
        sn: 'SN-001-2026',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getOutIpSNs.mockResolvedValue({ results: mockOutIpSNs, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('td:nth-child(3)').text()).toBe('SN-001-2026')
    })

    it('空描述显示横杠', async () => {
      const mockOutIpSNs = [{
        id: 1,
        mac_address: '00:11:22:33:44:55',
        sn: 'SN-001-2026',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getOutIpSNs.mockResolvedValue({ results: mockOutIpSNs, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('td:nth-child(4)').text()).toBe('-')
    })

    it('有描述时正确显示', async () => {
      const mockOutIpSNs = [{
        id: 1,
        mac_address: '00:11:22:33:44:55',
        sn: 'SN-001-2026',
        description: 'Production server',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getOutIpSNs.mockResolvedValue({ results: mockOutIpSNs, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('td:nth-child(4)').text()).toBe('Production server')
    })
  })

  describe('操作按钮', () => {
    it('显示编辑、删除按钮', async () => {
      const mockOutIpSNs = [{
        id: 1,
        mac_address: '00:11:22:33:44:55',
        sn: 'SN-001-2026',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getOutIpSNs.mockResolvedValue({ results: mockOutIpSNs, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.findAll('.btn-edit').length).toBe(1)
      expect(wrapper.findAll('.btn-danger').length).toBe(1)
    })
  })

  describe('创建/编辑弹窗', () => {
    it('创建弹窗正确初始化', async () => {
      getOutIpSNs.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openCreateDialog()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
      expect(wrapper.vm.form.mac_address).toBe('')
      expect(wrapper.vm.form.sn).toBe('')
    })

    it('编辑弹窗正确填充数据', async () => {
      const mockOutIpSNs = [{
        id: 1,
        mac_address: '00:11:22:33:44:55',
        sn: 'SN-001-2026',
        description: 'Test description',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getOutIpSNs.mockResolvedValue({ results: mockOutIpSNs, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openEditDialog(mockOutIpSNs[0])

      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.selectedItem).toEqual(mockOutIpSNs[0])
      expect(wrapper.vm.form.mac_address).toBe('00:11:22:33:44:55')
      expect(wrapper.vm.form.sn).toBe('SN-001-2026')
    })

    it('关闭弹窗清空错误', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.formError = 'some error'
      wrapper.vm.errors = { mac_address: 'error' }

      await wrapper.vm.closeDialog()

      expect(wrapper.vm.dialogVisible).toBe(false)
      expect(wrapper.vm.formError).toBe('')
      expect(wrapper.vm.errors).toEqual({})
    })
  })

  describe('表单验证', () => {
    it('MAC地址必填验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.mac_address = ''
      wrapper.vm.form.sn = 'SN-001'

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.mac_address).toBe('请输入MAC地址')
    })

    it('序列号必填验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.mac_address = '00:11:22:33:44:55'
      wrapper.vm.form.sn = ''

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.sn).toBe('请输入序列号')
    })

    it('验证通过调用创建API', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.isEdit = false
      wrapper.vm.form = {
        mac_address: '00:11:22:33:44:55',
        sn: 'SN-001-2026',
        description: ''
      }
      createOutIpSN.mockResolvedValue({})

      await wrapper.vm.submitForm()

      expect(createOutIpSN).toHaveBeenCalled()
    })

    it('验证通过调用更新API', async () => {
      const mockOutIpSNs = [{
        id: 1,
        mac_address: '00:11:22:33:44:55',
        sn: 'SN-001-2026',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getOutIpSNs.mockResolvedValue({ results: mockOutIpSNs, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.openEditDialog(mockOutIpSNs[0])
      wrapper.vm.isEdit = true
      updateOutIpSN.mockResolvedValue({})

      await wrapper.vm.submitForm()

      expect(updateOutIpSN).toHaveBeenCalledWith(1, expect.any(Object))
    })
  })

  describe('删除操作', () => {
    it('确认删除对话框设置正确', async () => {
      const mockOutIpSNs = [{
        id: 1,
        mac_address: '00:11:22:33:44:55',
        sn: 'SN-001-2026',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      const wrapper = createWrapper()
      await wrapper.vm.confirmDelete(mockOutIpSNs[0])

      expect(wrapper.vm.deleteDialogVisible).toBe(true)
      expect(wrapper.vm.selectedItem).toEqual(mockOutIpSNs[0])
    })

    it('删除成功后刷新列表', async () => {
      getOutIpSNs.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      wrapper.vm.selectedItem = { id: 1, mac_address: '00:11:22:33:44:55' }
      deleteOutIpSN.mockResolvedValue({})

      await wrapper.vm.handleDelete()

      expect(deleteOutIpSN).toHaveBeenCalledWith(1)
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
      getOutIpSNs.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()

      await wrapper.vm.handlePageChange(3)

      expect(wrapper.vm.page).toBe(3)
    })
  })
})