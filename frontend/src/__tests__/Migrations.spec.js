import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Migrations from '@/views/osmigrate/Migrations.vue'
import {
  getMigrates,
  createMigrateInit,
  createMigrate,
  createMigrateBack,
  getMigrateStatus
} from '@/api/migrate'

vi.mock('@/api/migrate')

describe('Migrations 页面测试', () => {
  let wrapper

  const mockJobs = [
    { id: 1, job_id: 'job-1', job_type: 'init', migrate_type: 'centos_to_culinux', target_host: '192.168.1.1', status: 'success', progress: 100, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:01:00Z' },
    { id: 2, job_id: 'job-2', job_type: 'migrate', migrate_type: 'centos_to_culinux', target_host: '192.168.1.2', status: 'running', progress: 50, created_at: '2024-01-02T00:00:00Z', updated_at: '2024-01-02T00:01:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getMigrates.mockResolvedValue({ results: mockJobs, count: 2 })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Migrations, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getMigrates', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getMigrates).toHaveBeenCalled()
    })

    it('应该显示迁移任务列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('job-1')
      expect(wrapper.text()).toContain('job-2')
      expect(wrapper.text()).toContain('192.168.1.1')
    })

    it('应该显示状态标签', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.status-success').exists()).toBe(true)
      expect(wrapper.find('.status-running').exists()).toBe(true)
    })

    it('应该显示加载状态', async () => {
      getMigrates.mockImplementation(() => new Promise(() => { }))
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('加载中...')
    })
  })

  describe('迁移初始化', () => {
    it('点击迁移初始化按钮应该打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-primary')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.initDialogVisible).toBe(true)
    })

    it('提交初始化成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createMigrateInit.mockResolvedValue({})

      await wrapper.findAll('button.btn-primary')[0].trigger('click')
      await flushPromises()

      wrapper.vm.initForm.host = '192.168.1.100'
      wrapper.vm.initForm.username = 'root'
      wrapper.vm.initForm.password = 'password'
      await wrapper.vm.submitInit()
      await flushPromises()

      expect(createMigrateInit).toHaveBeenCalled()
      expect(getMigrates).toHaveBeenCalledTimes(2)
    })

    it('必填项为空时应该显示 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-primary')[0].trigger('click')
      await flushPromises()

      wrapper.vm.initForm.host = ''
      await wrapper.vm.submitInit()

      expect(window.alert).toHaveBeenCalledWith('请填写必填项')
      expect(createMigrateInit).not.toHaveBeenCalled()
    })

    it('创建失败时应该显示 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createMigrateInit.mockRejectedValue(new Error('创建初始化任务失败'))

      await wrapper.findAll('button.btn-primary')[0].trigger('click')
      await flushPromises()

      wrapper.vm.initForm.host = '192.168.1.100'
      wrapper.vm.initForm.username = 'root'
      wrapper.vm.initForm.password = 'password'
      await wrapper.vm.submitInit()
      await flushPromises()

      expect(window.alert).toHaveBeenCalledWith('创建初始化任务失败')
    })
  })

  describe('执行迁移', () => {
    it('点击执行迁移按钮应该打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-primary')[1].trigger('click')
      await flushPromises()

      expect(wrapper.vm.migrateDialogVisible).toBe(true)
    })

    it('提交迁移成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createMigrate.mockResolvedValue({})

      await wrapper.findAll('button.btn-primary')[1].trigger('click')
      await flushPromises()

      wrapper.vm.migrateForm.host = '192.168.1.100'
      wrapper.vm.migrateForm.username = 'root'
      wrapper.vm.migrateForm.password = 'password'
      await wrapper.vm.submitMigrate()
      await flushPromises()

      expect(createMigrate).toHaveBeenCalled()
      expect(getMigrates).toHaveBeenCalledTimes(2)
    })

    it('必填项为空时应该显示 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-primary')[1].trigger('click')
      await flushPromises()

      wrapper.vm.migrateForm.host = ''
      await wrapper.vm.submitMigrate()

      expect(window.alert).toHaveBeenCalledWith('请填写必填项')
      expect(createMigrate).not.toHaveBeenCalled()
    })
  })

  describe('迁移回滚', () => {
    it('点击迁移回滚按钮应该打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('button.btn-warning').trigger('click')
      await flushPromises()

      expect(wrapper.vm.backDialogVisible).toBe(true)
    })

    it('提交回滚成功后应该刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      createMigrateBack.mockResolvedValue({})

      await wrapper.find('button.btn-warning').trigger('click')
      await flushPromises()

      wrapper.vm.backForm.host = '192.168.1.100'
      wrapper.vm.backForm.username = 'root'
      wrapper.vm.backForm.password = 'password'
      await wrapper.vm.submitBack()
      await flushPromises()

      expect(createMigrateBack).toHaveBeenCalled()
      expect(getMigrates).toHaveBeenCalledTimes(2)
    })
  })

  describe('查看详情', () => {
    it('点击详情按钮应该打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-view')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.detailDialogVisible).toBe(true)
      expect(wrapper.vm.selectedJob).toEqual(mockJobs[0])
    })

    it('刷新状态应该调用 getMigrateStatus', async () => {
      wrapper = createWrapper()
      await flushPromises()

      getMigrateStatus.mockResolvedValue({ data: { status: 'success' } })

      await wrapper.findAll('button.btn-view')[0].trigger('click')
      await flushPromises()
      await wrapper.vm.fetchStatus()
      await flushPromises()

      expect(getMigrateStatus).toHaveBeenCalledWith(1)
    })

    it('获取状态失败时应该显示 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      getMigrateStatus.mockRejectedValue(new Error('获取状态失败'))

      await wrapper.findAll('button.btn-view')[0].trigger('click')
      await flushPromises()
      await wrapper.vm.fetchStatus()
      await flushPromises()

      expect(window.alert).toHaveBeenCalledWith('获取状态失败')
    })
  })

  describe('搜索和过滤', () => {
    it('按回车搜索应该调用 loadJobs', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const searchInput = wrapper.find('input.search-input')
      await searchInput.setValue('192.168.1.1')
      await searchInput.trigger('keyup.enter')
      await flushPromises()

      expect(getMigrates).toHaveBeenCalledWith(expect.objectContaining({ search: '192.168.1.1' }))
    })

    it('改变任务类型过滤应该调用 loadJobs', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.filterType = 'migrate'
      await wrapper.vm.handleFilter()
      await flushPromises()

      expect(getMigrates).toHaveBeenCalledWith(expect.objectContaining({ job_type: 'migrate' }))
    })

    it('改变状态过滤应该调用 loadJobs', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.filterStatus = 'success'
      await wrapper.vm.handleFilter()
      await flushPromises()

      expect(getMigrates).toHaveBeenCalledWith(expect.objectContaining({ status: 'success' }))
    })
  })

  describe('分页', () => {
    it('点击下一页应该改变页码并刷新', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.page = 1
      wrapper.vm.totalCount = 40
      await wrapper.vm.handlePageChange(2)
      await flushPromises()

      expect(getMigrates).toHaveBeenCalledWith(expect.objectContaining({ page: 2 }))
    })
  })

  describe('空数据', () => {
    it('没有数据时应该显示空提示', async () => {
      getMigrates.mockResolvedValue({ results: [], count: 0 })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无数据')
    })
  })

  describe('错误处理', () => {
    it('加载失败时应该显示错误信息', async () => {
      getMigrates.mockRejectedValue(new Error('加载迁移任务列表失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe('加载迁移任务列表失败')
      expect(wrapper.find('.error').exists()).toBe(true)
    })
  })

  describe('工具函数', () => {
    it('formatJobType 应该正确格式化任务类型', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatJobType('init')).toBe('初始化')
      expect(wrapper.vm.formatJobType('migrate')).toBe('迁移')
      expect(wrapper.vm.formatJobType('back')).toBe('回滚')
      expect(wrapper.vm.formatJobType('unknown')).toBe('unknown')
    })

    it('formatStatus 应该正确格式化状态', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatStatus('pending')).toBe('等待中')
      expect(wrapper.vm.formatStatus('running')).toBe('运行中')
      expect(wrapper.vm.formatStatus('success')).toBe('成功')
      expect(wrapper.vm.formatStatus('failed')).toBe('失败')
      expect(wrapper.vm.formatStatus('unknown')).toBe('unknown')
    })

    it('getStatusClass 应该返回正确的 CSS 类', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusClass('pending')).toBe('status-pending')
      expect(wrapper.vm.getStatusClass('running')).toBe('status-running')
      expect(wrapper.vm.getStatusClass('success')).toBe('status-success')
      expect(wrapper.vm.getStatusClass('failed')).toBe('status-failed')
      expect(wrapper.vm.getStatusClass('unknown')).toBe('')
    })

    it('getProgressClass 应该返回正确的 CSS 类', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getProgressClass('pending')).toBe('progress-pending')
      expect(wrapper.vm.getProgressClass('running')).toBe('progress-running')
      expect(wrapper.vm.getProgressClass('success')).toBe('progress-success')
      expect(wrapper.vm.getProgressClass('failed')).toBe('progress-failed')
      expect(wrapper.vm.getProgressClass('unknown')).toBe('')
    })
  })
})
