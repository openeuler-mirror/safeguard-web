import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Repos from '@/views/osdeploy/Repos.vue'

// Mock API
vi.mock('@/api/osdeploy/repo', () => ({
  getRepos: vi.fn(),
  createRepo: vi.fn(),
  updateRepo: vi.fn(),
  deleteRepo: vi.fn(),
  syncRepo: vi.fn()
}))

import { getRepos, createRepo, updateRepo, deleteRepo, syncRepo } from '@/api/osdeploy/repo'

const createWrapper = () => {
  return mount(Repos, {
    global: {
      stubs: {
        'router-link': true,
        router: { push: vi.fn() }
      }
    }
  })
}

describe('Repos.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('UI 渲染', () => {
    it('渲染标题', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('仓库管理')
    })

    it('渲染创建按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.btn-primary').text()).toBe('创建仓库')
    })

    it('渲染类型筛选下拉框', () => {
      const wrapper = createWrapper()
      expect(wrapper.findAll('.filter-select').length).toBe(2)
    })

    it('渲染搜索输入框', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.search-input').exists()).toBe(true)
    })
  })

  describe('数据加载', () => {
    it('初始加载时 loading 为 true', async () => {
      getRepos.mockImplementation(() => new Promise(() => {}))
      const wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(true)
    })

    it('加载失败时显示错误', async () => {
      getRepos.mockRejectedValue(new Error('加载失败'))
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.error).toBe('加载失败')
    })

    it('无数据时显示暂无数据', async () => {
      getRepos.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.empty-text').exists()).toBe(true)
    })
  })

  describe('表格渲染', () => {
    it('正确加载仓库数据', async () => {
      const mockRepos = [{
        id: 1,
        name: 'centos-repo',
        repo_type: 'yum',
        base_url: 'http://mirror.example.com/centos',
        is_default: true,
        description: 'CentOS 镜像仓库',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getRepos.mockResolvedValue({ results: mockRepos, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await wrapper.vm.loadRepos()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.repos.length).toBe(1)
      expect(wrapper.vm.repos[0].name).toBe('centos-repo')
    })

    it('默认仓库 is_default 为 true', async () => {
      const mockRepos = [{
        id: 1,
        name: 'centos-repo',
        repo_type: 'yum',
        base_url: 'http://mirror.example.com/centos',
        is_default: true,
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getRepos.mockResolvedValue({ results: mockRepos, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await wrapper.vm.loadRepos()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.repos[0].is_default).toBe(true)
    })
  })

  describe('仓库类型显示', () => {
    it('formatRepoType 返回正确的中文类型', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatRepoType('yum')).toBe('YUM')
      expect(wrapper.vm.formatRepoType('iso')).toBe('ISO')
      expect(wrapper.vm.formatRepoType('http')).toBe('HTTP')
    })

    it('getRepoTypeClass 返回正确的样式类', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.getRepoTypeClass('yum')).toBe('type-yum')
      expect(wrapper.vm.getRepoTypeClass('iso')).toBe('type-iso')
      expect(wrapper.vm.getRepoTypeClass('http')).toBe('type-http')
    })
  })

  describe('创建/编辑弹窗', () => {
    it('创建弹窗正确初始化', async () => {
      getRepos.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openCreateDialog()

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
      expect(wrapper.vm.form.name).toBe('')
      expect(wrapper.vm.form.repo_type).toBe('yum')
    })

    it('编辑弹窗正确填充数据', async () => {
      const mockRepos = [{
        id: 1,
        name: 'repo1',
        repo_type: 'iso',
        base_url: 'http://example.com',
        is_default: true,
        description: 'test description',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getRepos.mockResolvedValue({ results: mockRepos, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      await wrapper.vm.openEditDialog(mockRepos[0])

      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.selectedRepo).toEqual(mockRepos[0])
      expect(wrapper.vm.form.name).toBe('repo1')
      expect(wrapper.vm.form.repo_type).toBe('iso')
    })

    it('关闭弹窗清空错误', async () => {
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

  describe('表单验证', () => {
    it('仓库名称必填验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.name = ''
      wrapper.vm.form.base_url = 'http://example.com'

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.name).toBe('请输入仓库名称')
    })

    it('仓库地址必填验证', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.name = 'test-repo'
      wrapper.vm.form.base_url = ''

      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.base_url).toBe('请输入仓库地址')
    })

    it('验证通过调用创建API', async () => {
      const wrapper = createWrapper()
      wrapper.vm.dialogVisible = true
      wrapper.vm.isEdit = false
      wrapper.vm.form = {
        name: 'test-repo',
        repo_type: 'yum',
        base_url: 'http://example.com',
        description: '',
        is_default: false
      }
      createRepo.mockResolvedValue({})

      await wrapper.vm.submitForm()

      expect(createRepo).toHaveBeenCalled()
    })

    it('验证通过调用更新API', async () => {
      const mockRepos = [{
        id: 1,
        name: 'repo1',
        repo_type: 'yum',
        base_url: 'http://example.com',
        is_default: false,
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      getRepos.mockResolvedValue({ results: mockRepos, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.openEditDialog(mockRepos[0])
      wrapper.vm.isEdit = true
      updateRepo.mockResolvedValue({})

      await wrapper.vm.submitForm()

      expect(updateRepo).toHaveBeenCalledWith(1, expect.any(Object))
    })
  })

  describe('删除操作', () => {
    it('确认删除对话框设置正确', async () => {
      const mockRepos = [{
        id: 1,
        name: 'repo1',
        repo_type: 'yum',
        base_url: 'http://example.com',
        is_default: false,
        description: '',
        created_at: '2026-01-01T00:00:00Z'
      }]

      const wrapper = createWrapper()
      await wrapper.vm.confirmDelete(mockRepos[0])

      expect(wrapper.vm.deleteDialogVisible).toBe(true)
      expect(wrapper.vm.selectedRepo).toEqual(mockRepos[0])
    })

    it('删除成功后刷新列表', async () => {
      getRepos.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      wrapper.vm.selectedRepo = { id: 1, name: 'repo1' }
      deleteRepo.mockResolvedValue({})

      await wrapper.vm.handleDelete()

      expect(deleteRepo).toHaveBeenCalledWith(1)
      expect(wrapper.vm.deleteDialogVisible).toBe(false)
    })
  })

  describe('同步操作', () => {
    it('同步成功后刷新列表', async () => {
      getRepos.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      const mockRepo = { id: 1, name: 'repo1' }
      syncRepo.mockResolvedValue({})

      await wrapper.vm.handleSync(mockRepo)

      expect(syncRepo).toHaveBeenCalledWith(1)
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

  describe('筛选和搜索', () => {
    it('handleFilter 重置页码', async () => {
      getRepos.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      wrapper.vm.page = 5

      await wrapper.vm.handleFilter()

      expect(wrapper.vm.page).toBe(1)
    })

    it('handleSearch 重置页码', async () => {
      getRepos.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      wrapper.vm.page = 5

      await wrapper.vm.handleSearch()

      expect(wrapper.vm.page).toBe(1)
    })

    it('handlePageChange 更改页码', async () => {
      getRepos.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()

      await wrapper.vm.handlePageChange(3)

      expect(wrapper.vm.page).toBe(3)
    })
  })
})