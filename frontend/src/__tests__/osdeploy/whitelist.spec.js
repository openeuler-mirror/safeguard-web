import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import WhiteList from '@/views/osdeploy/WhiteList.vue'

// Mock API
vi.mock('@/api/osdeploy/whitelist', () => ({
  getWhiteList: vi.fn(),
  createWhiteList: vi.fn(),
  updateWhiteList: vi.fn(),
  deleteWhiteList: vi.fn(),
  importWhiteList: vi.fn()
}))

import {
  getWhiteList,
  createWhiteList,
  updateWhiteList,
  deleteWhiteList,
  importWhiteList
} from '@/api/osdeploy/whitelist'

const createWrapper = () => {
  return mount(WhiteList, {
    global: {
      stubs: {
        'router-link': true,
        router: { push: vi.fn() }
      }
    }
  })
}

describe('WhiteList.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('UI 渲染', () => {
    it('渲染标题', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('MAC地址白名单')
    })

    it('渲染批量导入和添加按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.findAll('.btn-import').length).toBe(1)
      expect(wrapper.findAll('.btn-primary').length).toBe(1)
    })
  })

  describe('数据加载', () => {
    it('初始加载时 loading 为 true', async () => {
      getWhiteList.mockImplementation(() => new Promise(() => {}))
      const wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(true)
    })

    it('加载失败时显示错误', async () => {
      getWhiteList.mockRejectedValue(new Error('加载失败'))
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.error).toBe('加载失败')
    })

    it('无数据时显示暂无数据', async () => {
      getWhiteList.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.empty-text').exists()).toBe(true)
    })
  })

  describe('表格渲染', () => {
    it('正确加载白名单数据', async () => {
      const mockWhiteList = [{
        id: 1,
        mac_address: '00:11:22:33:44:55',
        hostname: 'server-01',
        ip_address: '192.168.1.100',
        is_active: true,
        description: 'Test server',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getWhiteList.mockResolvedValue({ results: mockWhiteList, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await wrapper.vm.loadWhiteList()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.whitelist.length).toBe(1)
      expect(wrapper.vm.whitelist[0].mac_address).toBe('00:11:22:33:44:55')
    })
  })

  describe('创建/编辑弹窗', () => {
    it('创建弹窗正确初始化', async () => {
      getWhiteList.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openCreateDialog()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
      expect(wrapper.vm.form.mac_address).toBe('')
      expect(wrapper.vm.form.is_active).toBe(true)
    })

    it('编辑弹窗正确填充数据', async () => {
      const mockWhiteList = [{
        id: 1,
        mac_address: '00:11:22:33:44:55',
        hostname: 'server-01',
        ip_address: '192.168.1.100',
        is_active: false,
        description: 'Test description',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getWhiteList.mockResolvedValue({ results: mockWhiteList, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openEditDialog(mockWhiteList[0])

      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.selectedItem).toEqual(mockWhiteList[0])
      expect(wrapper.vm.form.mac_address).toBe('00:11:22:33:44:55')
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

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.mac_address).toBe('请输入MAC地址')
    })

    it('MAC地址格式验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.mac_address = 'invalid-mac'

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.mac_address).toBe('MAC地址格式不正确，应为如: 00:11:22:33:44:55')
    })

    it('正确格式的MAC通过验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.isEdit = false
      wrapper.vm.form = {
        mac_address: '00:11:22:33:44:55',
        hostname: '',
        ip_address: '',
        description: '',
        is_active: true
      }
      createWhiteList.mockResolvedValue({})

      await wrapper.vm.submitForm()

      expect(createWhiteList).toHaveBeenCalled()
    })
  })

  describe('导入弹窗', () => {
    it('导入弹窗正确初始化', async () => {
      const wrapper = createWrapper()

      await wrapper.vm.openImportDialog()

      expect(wrapper.vm.importDialogVisible).toBe(true)
      expect(wrapper.vm.selectedFile).toBe(null)
      expect(wrapper.vm.uploadProgress).toBe(0)
    })

    it('关闭导入弹窗重置状态', async () => {
      const wrapper = createWrapper()
      wrapper.vm.importDialogVisible = true
      wrapper.vm.selectedFile = { name: 'test.xlsx' }
      wrapper.vm.uploadProgress = 50

      await wrapper.vm.closeImportDialog()

      expect(wrapper.vm.importDialogVisible).toBe(false)
      expect(wrapper.vm.selectedFile).toBe(null)
      expect(wrapper.vm.uploadProgress).toBe(0)
    })

    it('文件选择后更新selectedFile', async () => {
      const wrapper = createWrapper()
      const mockFile = new File(['test'], 'test.xlsx')
      const mockEvent = { target: { files: [mockFile] } }

      await wrapper.vm.handleFileChange(mockEvent)

      expect(wrapper.vm.selectedFile).toEqual(mockFile)
    })
  })

  describe('删除操作', () => {
    it('确认删除对话框设置正确', async () => {
      const mockWhiteList = [{
        id: 1,
        mac_address: '00:11:22:33:44:55',
        hostname: '',
        ip_address: '',
        is_active: true,
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      const wrapper = createWrapper()
      await wrapper.vm.confirmDelete(mockWhiteList[0])

      expect(wrapper.vm.deleteDialogVisible).toBe(true)
      expect(wrapper.vm.selectedItem).toEqual(mockWhiteList[0])
    })

    it('删除成功后刷新列表', async () => {
      getWhiteList.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      wrapper.vm.selectedItem = { id: 1, mac_address: '00:11:22:33:44:55' }
      deleteWhiteList.mockResolvedValue({})

      await wrapper.vm.handleDelete()

      expect(deleteWhiteList).toHaveBeenCalledWith(1)
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
      getWhiteList.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()

      await wrapper.vm.handlePageChange(3)

      expect(wrapper.vm.page).toBe(3)
    })
  })
})