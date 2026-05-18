import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ISOFiles from '@/views/osdeploy/ISOFiles.vue'

// Mock API
vi.mock('@/api/osdeploy/iso', () => ({
  getISOFiles: vi.fn(),
  createISOFile: vi.fn(),
  updateISOFile: vi.fn(),
  deleteISOFile: vi.fn(),
  uploadISOFile: vi.fn()
}))

import {
  getISOFiles,
  createISOFile,
  updateISOFile,
  deleteISOFile,
  uploadISOFile
} from '@/api/osdeploy/iso'

const createWrapper = () => {
  return mount(ISOFiles, {
    global: {
      stubs: {
        'router-link': true,
        router: { push: vi.fn() }
      }
    }
  })
}

describe('ISOFiles.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('UI 渲染', () => {
    it('渲染标题', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('ISO 文件管理')
    })

    it('渲染上传按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.btn-upload').text()).toBe('上传ISO文件')
    })

    it('渲染添加记录按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.btn-primary').text()).toBe('添加记录')
    })
  })

  describe('数据加载', () => {
    it('加载时显示 loading', async () => {
      getISOFiles.mockImplementation(() => new Promise(() => {}))
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
      getISOFiles.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.empty-text').exists()).toBe(true)
    })
  })

  describe('表格渲染', () => {
    it('正确显示ISO文件数据', async () => {
      const mockISOFiles = [{
        id: 1,
        filename: 'CentOS-7-x86_64-Everything.iso',
        size: 4294967296,
        md5sum: 'd41d8cd98f00b204e9800998ecf8427e',
        status: 'available',
        description: 'CentOS 7 Full ISO',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getISOFiles.mockResolvedValue({ results: mockISOFiles, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(1)
      expect(rows[0].find('td:nth-child(2)').text()).toBe('CentOS-7-x86_64-Everything.iso')
    })

    it('文件大小正确格式化', async () => {
      const mockISOFiles = [{
        id: 1,
        filename: 'CentOS-7.iso',
        size: 4294967296,
        md5sum: 'abc123',
        status: 'available',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getISOFiles.mockResolvedValue({ results: mockISOFiles, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('td:nth-child(3)').text()).toBe('4.00 GB')
    })

    it('MD5列正确显示', async () => {
      const mockISOFiles = [{
        id: 1,
        filename: 'CentOS-7.iso',
        size: 4294967296,
        md5sum: 'd41d8cd98f00b204e9800998ecf8427e',
        status: 'available',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getISOFiles.mockResolvedValue({ results: mockISOFiles, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const md5Cell = wrapper.find('.md5-cell')
      expect(md5Cell.exists()).toBe(true)
      expect(md5Cell.text()).toBe('d41d8cd98f00b204e9800998ecf8427e')
    })
  })

  describe('状态显示', () => {
    it('available 状态显示绿色', async () => {
      const mockISOFiles = [{
        id: 1,
        filename: 'CentOS-7.iso',
        size: 4294967296,
        md5sum: 'abc123',
        status: 'available',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getISOFiles.mockResolvedValue({ results: mockISOFiles, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const statusSpan = wrapper.find('.status-available')
      expect(statusSpan.exists()).toBe(true)
      expect(statusSpan.text()).toBe('可用')
    })

    it('uploading 状态显示橙色', async () => {
      const mockISOFiles = [{
        id: 1,
        filename: 'CentOS-7.iso',
        size: 4294967296,
        md5sum: 'abc123',
        status: 'uploading',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getISOFiles.mockResolvedValue({ results: mockISOFiles, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const statusSpan = wrapper.find('.status-uploading')
      expect(statusSpan.exists()).toBe(true)
      expect(statusSpan.text()).toBe('上传中')
    })

    it('processing 状态显示蓝色', async () => {
      const mockISOFiles = [{
        id: 1,
        filename: 'CentOS-7.iso',
        size: 4294967296,
        md5sum: 'abc123',
        status: 'processing',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getISOFiles.mockResolvedValue({ results: mockISOFiles, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const statusSpan = wrapper.find('.status-processing')
      expect(statusSpan.exists()).toBe(true)
      expect(statusSpan.text()).toBe('处理中')
    })

    it('unavailable 状态显示红色', async () => {
      const mockISOFiles = [{
        id: 1,
        filename: 'CentOS-7.iso',
        size: 4294967296,
        md5sum: 'abc123',
        status: 'unavailable',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getISOFiles.mockResolvedValue({ results: mockISOFiles, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const statusSpan = wrapper.find('.status-unavailable')
      expect(statusSpan.exists()).toBe(true)
      expect(statusSpan.text()).toBe('不可用')
    })
  })

  describe('操作按钮', () => {
    it('显示编辑、删除按钮', async () => {
      const mockISOFiles = [{
        id: 1,
        filename: 'CentOS-7.iso',
        size: 4294967296,
        md5sum: 'abc123',
        status: 'available',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getISOFiles.mockResolvedValue({ results: mockISOFiles, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.findAll('.btn-edit').length).toBe(1)
      expect(wrapper.findAll('.btn-danger').length).toBe(1)
    })
  })

  describe('创建/编辑弹窗', () => {
    it('创建弹窗正确初始化', async () => {
      getISOFiles.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openCreateDialog()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
      expect(wrapper.vm.form.filename).toBe('')
      expect(wrapper.vm.form.size).toBe('')
    })

    it('编辑弹窗正确填充数据', async () => {
      const mockISOFiles = [{
        id: 1,
        filename: 'CentOS-7.iso',
        size: 4294967296,
        md5sum: 'd41d8cd98f00b204e9800998ecf8427e',
        status: 'available',
        description: 'CentOS 7 Full',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getISOFiles.mockResolvedValue({ results: mockISOFiles, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openEditDialog(mockISOFiles[0])

      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.selectedItem).toEqual(mockISOFiles[0])
      expect(wrapper.vm.form.filename).toBe('CentOS-7.iso')
    })

    it('关闭弹窗清空错误', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.formError = 'some error'
      wrapper.vm.errors = { filename: 'error' }

      await wrapper.vm.closeDialog()

      expect(wrapper.vm.dialogVisible).toBe(false)
      expect(wrapper.vm.formError).toBe('')
      expect(wrapper.vm.errors).toEqual({})
    })
  })

  describe('上传弹窗', () => {
    it('上传弹窗正确初始化', async () => {
      const wrapper = createWrapper()

      await wrapper.vm.openUploadDialog()

      expect(wrapper.vm.uploadDialogVisible).toBe(true)
      expect(wrapper.vm.selectedFile).toBe(null)
      expect(wrapper.vm.uploadProgress).toBe(0)
    })

    it('关闭上传弹窗重置状态', async () => {
      const wrapper = createWrapper()
      wrapper.vm.uploadDialogVisible = true
      wrapper.vm.selectedFile = { name: 'test.iso' }
      wrapper.vm.uploadProgress = 50

      await wrapper.vm.closeUploadDialog()

      expect(wrapper.vm.uploadDialogVisible).toBe(false)
      expect(wrapper.vm.selectedFile).toBe(null)
      expect(wrapper.vm.uploadProgress).toBe(0)
    })

    it('文件选择后更新selectedFile', async () => {
      const wrapper = createWrapper()
      const mockFile = new File(['test'], 'test.iso')
      const mockEvent = { target: { files: [mockFile] } }

      await wrapper.vm.handleFileChange(mockEvent)

      expect(wrapper.vm.selectedFile).toEqual(mockFile)
    })
  })

  describe('表单验证', () => {
    it('文件名必填验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.filename = ''
      wrapper.vm.form.size = 4294967296

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.filename).toBe('请输入文件名')
    })

    it('文件大小必填验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.filename = 'CentOS-7.iso'
      wrapper.vm.form.size = ''

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.size).toBe('请输入文件大小')
    })

    it('验证通过调用创建API', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.isEdit = false
      wrapper.vm.form = {
        filename: 'CentOS-7.iso',
        size: 4294967296,
        md5sum: 'abc123',
        description: ''
      }
      createISOFile.mockResolvedValue({})

      await wrapper.vm.submitForm()

      expect(createISOFile).toHaveBeenCalled()
    })
  })

  describe('删除操作', () => {
    it('确认删除对话框设置正确', async () => {
      const mockISOFiles = [{
        id: 1,
        filename: 'CentOS-7.iso',
        size: 4294967296,
        md5sum: 'abc123',
        status: 'available',
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      const wrapper = createWrapper()
      await wrapper.vm.confirmDelete(mockISOFiles[0])

      expect(wrapper.vm.deleteDialogVisible).toBe(true)
      expect(wrapper.vm.selectedItem).toEqual(mockISOFiles[0])
    })

    it('删除成功后刷新列表', async () => {
      getISOFiles.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      wrapper.vm.selectedItem = { id: 1, filename: 'CentOS-7.iso' }
      deleteISOFile.mockResolvedValue({})

      await wrapper.vm.handleDelete()

      expect(deleteISOFile).toHaveBeenCalledWith(1)
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

    it('formatSize 正确转换字节到GB', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatSize(107374182400)).toBe('100.00 GB')
    })

    it('formatSize 正确转换字节到MB', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatSize(52428800)).toBe('50.00 MB')
    })

    it('formatSize 处理0值', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatSize(0)).toBe('-')
    })

    it('formatSize 处理空值', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatSize(null)).toBe('-')
    })

    it('formatStatus 返回正确的状态中文', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatStatus('available')).toBe('可用')
      expect(wrapper.vm.formatStatus('uploading')).toBe('上传中')
      expect(wrapper.vm.formatStatus('processing')).toBe('处理中')
      expect(wrapper.vm.formatStatus('unavailable')).toBe('不可用')
    })

    it('getStatusClass 返回正确的样式类', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.getStatusClass('available')).toBe('status-available')
      expect(wrapper.vm.getStatusClass('uploading')).toBe('status-uploading')
      expect(wrapper.vm.getStatusClass('processing')).toBe('status-processing')
      expect(wrapper.vm.getStatusClass('unavailable')).toBe('status-unavailable')
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

  describe('筛选和搜索', () => {
    it('handlePageChange 更改页码', async () => {
      getISOFiles.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()

      await wrapper.vm.handlePageChange(3)

      expect(wrapper.vm.page).toBe(3)
    })
  })
})