import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Kickstarts from '@/views/osdeploy/Kickstarts.vue'

// Mock API
vi.mock('@/api/osdeploy/kickstart', () => ({
  getKickstarts: vi.fn(),
  createKickstart: vi.fn(),
  updateKickstart: vi.fn(),
  deleteKickstart: vi.fn(),
  validateKickstart: vi.fn(),
  previewKickstart: vi.fn()
}))

vi.mock('@/api/osdeploy/repo', () => ({
  getRepos: vi.fn()
}))

import {
  getKickstarts,
  createKickstart,
  updateKickstart,
  deleteKickstart,
  validateKickstart,
  previewKickstart
} from '@/api/osdeploy/kickstart'
import { getRepos } from '@/api/osdeploy/repo'

const createWrapper = () => {
  return mount(Kickstarts, {
    global: {
      stubs: {
        'router-link': true,
        router: { push: vi.fn() }
      }
    }
  })
}

describe('Kickstarts.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('UI 渲染', () => {
    it('渲染标题', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('Kickstart 模板管理')
    })

    it('渲染创建按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.btn-primary').text()).toBe('创建模板')
    })

    it('渲染仓库筛选下拉框', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.filter-select').exists()).toBe(true)
    })

    it('渲染搜索输入框', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.search-input').exists()).toBe(true)
    })
  })

  describe('数据加载', () => {
    it('加载时显示 loading', async () => {
      getKickstarts.mockImplementation(() => new Promise(() => {}))
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.loading = true
      expect(wrapper.find('.loading').exists()).toBe(true)
    })

    it('加载失败时显示错误信息', async () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.error = '加载失败'
      wrapper.vm.loading = false
      expect(wrapper.find('.error').text()).toBe('加载失败')
    })

    it('无数据时显示暂无数据', async () => {
      getKickstarts.mockResolvedValue({ results: [], count: 0 })
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.empty-text').exists()).toBe(true)
    })
  })

  describe('表格渲染', () => {
    it('正确显示模板数据', async () => {
      const mockKickstarts = [{
        id: 1,
        name: 'centos-ks',
        repo: 1,
        repo_name: 'centos-repo',
        kernel_options: { ksdevice: 'eth0' },
        created_at: '2026-01-01T00:00:00Z'
      }]

      getKickstarts.mockResolvedValue({ results: mockKickstarts, count: 1 })
      getRepos.mockResolvedValue({ results: [{ id: 1, name: 'centos-repo' }] })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(1)
      expect(rows[0].find('td:nth-child(2)').text()).toBe('centos-ks')
    })

    it('显示仓库名称', async () => {
      const mockKickstarts = [{
        id: 1,
        name: 'centos-ks',
        repo: 1,
        repo_name: 'centos-repo',
        kernel_options: {},
        created_at: '2026-01-01T00:00:00Z'
      }]

      getKickstarts.mockResolvedValue({ results: mockKickstarts, count: 1 })
      getRepos.mockResolvedValue({ results: [{ id: 1, name: 'centos-repo' }] })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('td:nth-child(3)').text()).toBe('centos-repo')
    })

    it('无仓库时显示横杠', async () => {
      const mockKickstarts = [{
        id: 1,
        name: 'centos-ks',
        repo: null,
        repo_name: null,
        kernel_options: {},
        created_at: '2026-01-01T00:00:00Z'
      }]

      getKickstarts.mockResolvedValue({ results: mockKickstarts, count: 1 })
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('td:nth-child(3)').text()).toBe('-')
    })
  })

  describe('操作按钮', () => {
    it('显示编辑、预览、验证、删除按钮', async () => {
      const mockKickstarts = [{
        id: 1,
        name: 'centos-ks',
        repo: null,
        repo_name: null,
        kernel_options: {},
        created_at: '2026-01-01T00:00:00Z'
      }]

      getKickstarts.mockResolvedValue({ results: mockKickstarts, count: 1 })
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.findAll('.btn-edit').length).toBe(1)
      expect(wrapper.findAll('.btn-preview').length).toBe(1)
      expect(wrapper.findAll('.btn-validate').length).toBe(1)
      expect(wrapper.findAll('.btn-danger').length).toBe(1)
    })
  })

  describe('创建/编辑弹窗', () => {
    it('创建弹窗正确初始化', async () => {
      getKickstarts.mockResolvedValue({ results: [], count: 0 })
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openCreateDialog()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
      expect(wrapper.vm.form.name).toBe('')
      expect(wrapper.vm.form.content).toBe('')
    })

    it('编辑弹窗正确填充数据', async () => {
      const mockKickstarts = [{
        id: 1,
        name: 'centos-ks',
        repo: 1,
        content: 'Kickstart content',
        kernel_options: { ksdevice: 'eth0' },
        created_at: '2026-01-01T00:00:00Z'
      }]

      getKickstarts.mockResolvedValue({ results: mockKickstarts, count: 1 })
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openEditDialog(mockKickstarts[0])

      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.selectedKickstart).toEqual(mockKickstarts[0])
      expect(wrapper.vm.form.name).toBe('centos-ks')
    })

    it('关闭弹窗清空错误', async () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.formError = 'some error'
      wrapper.vm.errors = { name: 'error' }

      await wrapper.vm.closeDialog()

      expect(wrapper.vm.dialogVisible).toBe(false)
      expect(wrapper.vm.formError).toBe('')
      expect(wrapper.vm.errors).toEqual({})
    })
  })

  describe('预览弹窗', () => {
    it('预览弹窗正确初始化', async () => {
      const mockKickstarts = [{
        id: 1,
        name: 'centos-ks',
        repo: null,
        content: 'Kickstart content',
        kernel_options: {},
        created_at: '2026-01-01T00:00:00Z'
      }]

      getKickstarts.mockResolvedValue({ results: mockKickstarts, count: 1 })
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openPreviewDialog(mockKickstarts[0])

      expect(wrapper.vm.previewDialogVisible).toBe(true)
      expect(wrapper.vm.selectedKickstart).toEqual(mockKickstarts[0])
      expect(wrapper.vm.varsJson).toBe('{}')
    })

    it('关闭预览弹窗清空数据', async () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.previewDialogVisible = true
      wrapper.vm.selectedKickstart = { id: 1, name: 'ks1' }
      wrapper.vm.varsJson = '{"key": "value"}'
      wrapper.vm.previewContent = 'preview result'

      await wrapper.vm.closePreviewDialog()

      expect(wrapper.vm.previewDialogVisible).toBe(false)
      expect(wrapper.vm.selectedKickstart).toBe(null)
    })
  })

  describe('变量替换预览', () => {
    it('打开变量替换弹窗', async () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.previewDialogVisible = true

      await wrapper.vm.openVarsDialog()

      expect(wrapper.vm.varsDialogVisible).toBe(true)
    })

    it('关闭变量替换弹窗清空数据', async () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.varsDialogVisible = true
      wrapper.vm.varsJson = '{"hostname": "test"}'
      wrapper.vm.previewContent = 'result'

      await wrapper.vm.closeVarsDialog()

      expect(wrapper.vm.varsDialogVisible).toBe(false)
      expect(wrapper.vm.varsJson).toBe('{}')
      expect(wrapper.vm.previewContent).toBe('')
    })

    it('变量替换预览返回内容', async () => {
      const mockKickstarts = [{
        id: 1,
        name: 'centos-ks',
        repo: null,
        content: 'Hostname: {{hostname}}',
        kernel_options: {},
        created_at: '2026-01-01T00:00:00Z'
      }]

      getKickstarts.mockResolvedValue({ results: mockKickstarts, count: 1 })
      getRepos.mockResolvedValue({ results: [] })
      previewKickstart.mockResolvedValue({ content: 'Hostname: test-server' })

      const wrapper = createWrapper()
      wrapper.vm.selectedKickstart = mockKickstarts[0]
      wrapper.vm.varsJson = '{"hostname": "test-server"}'

      await wrapper.vm.doPreview()

      expect(previewKickstart).toHaveBeenCalledWith(1, { hostname: 'test-server' })
      expect(wrapper.vm.previewContent).toBe('Hostname: test-server')
    })
  })

  describe('表单验证', () => {
    it('模板名称必填验证', async () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.name = ''
      wrapper.vm.form.content = 'content'

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.name).toBe('请输入模板名称')
    })

    it('模板内容必填验证', async () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.name = 'test-ks'
      wrapper.vm.form.content = ''

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.content).toBe('请输入模板内容')
    })

    it('验证通过调用创建API', async () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.isEdit = false
      wrapper.vm.form = {
        name: 'test-ks',
        repo: null,
        content: 'Kickstart content',
        kernel_options_json: ''
      }
      createKickstart.mockResolvedValue({})

      await wrapper.vm.submitForm()

      expect(createKickstart).toHaveBeenCalled()
    })
  })

  describe('验证操作', () => {
    it('验证成功后显示提示', async () => {
      const mockKickstarts = [{
        id: 1,
        name: 'centos-ks',
        repo: null,
        content: 'content',
        kernel_options: {},
        created_at: '2026-01-01T00:00:00Z'
      }]

      getKickstarts.mockResolvedValue({ results: mockKickstarts, count: 1 })
      getRepos.mockResolvedValue({ results: [] })
      validateKickstart.mockResolvedValue({})

      const wrapper = createWrapper()
      await wrapper.vm.handleValidate(mockKickstarts[0])

      expect(validateKickstart).toHaveBeenCalledWith(1)
    })
  })

  describe('删除操作', () => {
    it('确认删除对话框设置正确', async () => {
      const mockKickstarts = [{
        id: 1,
        name: 'centos-ks',
        repo: null,
        content: 'content',
        kernel_options: {},
        created_at: '2026-01-01T00:00:00Z'
      }]

      getKickstarts.mockResolvedValue({ results: mockKickstarts, count: 1 })
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      await wrapper.vm.confirmDelete(mockKickstarts[0])

      expect(wrapper.vm.deleteDialogVisible).toBe(true)
      expect(wrapper.vm.selectedKickstart).toEqual(mockKickstarts[0])
    })

    it('删除成功后刷新列表', async () => {
      getKickstarts.mockResolvedValue({ results: [], count: 0 })
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.selectedKickstart = { id: 1, name: 'ks1' }
      deleteKickstart.mockResolvedValue({})

      await wrapper.vm.handleDelete()

      expect(deleteKickstart).toHaveBeenCalledWith(1)
      expect(wrapper.vm.deleteDialogVisible).toBe(false)
    })
  })

  describe('工具方法', () => {
    it('formatDate 正确格式化日期', () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      const result = wrapper.vm.formatDate('2026-01-15T10:30:00Z')
      expect(result).toContain('2026')
    })

    it('formatDate 处理空值', () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      expect(wrapper.vm.formatDate('')).toBe('-')
      expect(wrapper.vm.formatDate(null)).toBe('-')
    })

    it('formatKernelOptions 正确序列化内核参数', () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      const options = { 'ksdevice': 'eth0', 'inst.stage2': 'http://example.com' }
      expect(wrapper.vm.formatKernelOptions(options)).toBe(JSON.stringify(options))
    })

    it('formatKernelOptions 处理空值', () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      expect(wrapper.vm.formatKernelOptions(null)).toBe('-')
      expect(wrapper.vm.formatKernelOptions({})).toBe('-')
    })
  })

  describe('分页', () => {
    it('正确计算总页数', () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.totalCount = 45
      wrapper.vm.pageSize = 20
      expect(wrapper.vm.totalPages).toBe(3)
    })

    it('总页数为0时返回1', () => {
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.totalCount = 0
      wrapper.vm.pageSize = 20
      expect(wrapper.vm.totalPages).toBe(1)
    })
  })

  describe('筛选和搜索', () => {
    it('handleFilter 重置页码', async () => {
      getKickstarts.mockResolvedValue({ results: [], count: 0 })
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.page = 5

      await wrapper.vm.handleFilter()

      expect(wrapper.vm.page).toBe(1)
    })

    it('handleSearch 重置页码', async () => {
      getKickstarts.mockResolvedValue({ results: [], count: 0 })
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()
      wrapper.vm.page = 5

      await wrapper.vm.handleSearch()

      expect(wrapper.vm.page).toBe(1)
    })

    it('handlePageChange 更改页码', async () => {
      getKickstarts.mockResolvedValue({ results: [], count: 0 })
      getRepos.mockResolvedValue({ results: [] })
      const wrapper = createWrapper()

      await wrapper.vm.handlePageChange(3)

      expect(wrapper.vm.page).toBe(3)
    })
  })
})