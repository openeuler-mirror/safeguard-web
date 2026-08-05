import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Tasks from '@/views/Tasks.vue'
import { getTasks } from '@/api/task'

vi.mock('@/api/task')

describe('Tasks 页面测试', () => {
  let wrapper

  const mockTasks = [
    { id: 1, job_id: 'task-001', job_type: 'os_install', target: 'host-01', status: 'success', progress: 100, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:01:00Z' },
    { id: 2, job_id: 'task-002', job_type: 'os_migrate', target: 'host-02', status: 'running', progress: 50, created_at: '2024-01-02T00:00:00Z', updated_at: '2024-01-02T00:01:00Z' },
    { id: 3, job_id: 'task-003', job_type: 'safeguard_deploy', target: 'host-03', status: 'pending', progress: 0, created_at: '2024-01-03T00:00:00Z', updated_at: '2024-01-03T00:00:00Z' },
    { id: 4, job_id: 'task-004', job_type: 'safeguard_rollback', target: 'host-04', status: 'failed', progress: 30, error_message: '部署失败', created_at: '2024-01-04T00:00:00Z', updated_at: '2024-01-04T00:00:30Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getTasks.mockResolvedValue({ results: mockTasks, count: 4 })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Tasks, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getTasks', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getTasks).toHaveBeenCalled()
    })

    it('应该显示任务列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('task-001')
      expect(wrapper.text()).toContain('task-002')
      expect(wrapper.text()).toContain('host-01')
      expect(wrapper.text()).toContain('host-02')
    })

    it('应该显示加载状态', async () => {
      let resolvePromise
      getTasks.mockImplementation(() => new Promise(resolve => {
        resolvePromise = resolve
      }))

      wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(true)

      resolvePromise({ results: mockTasks, count: 4 })
      await flushPromises()

      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('任务状态显示', () => {
    it('应该显示正确的任务状态文本', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('成功')
      expect(wrapper.text()).toContain('运行中')
      expect(wrapper.text()).toContain('等待中')
      expect(wrapper.text()).toContain('失败')
    })

    it('应该显示正确的状态样式类', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.status-success').exists()).toBe(true)
      expect(wrapper.find('.status-running').exists()).toBe(true)
      expect(wrapper.find('.status-pending').exists()).toBe(true)
      expect(wrapper.find('.status-failed').exists()).toBe(true)
    })

    it('应该显示正确的任务类型文本', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('系统安装')
      expect(wrapper.text()).toContain('系统迁移')
      expect(wrapper.text()).toContain('安全部署')
      expect(wrapper.text()).toContain('安全回滚')
    })
  })

  describe('进度条显示', () => {
    it('应该显示进度百分比', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('100%')
      expect(wrapper.text()).toContain('50%')
      expect(wrapper.text()).toContain('0%')
      expect(wrapper.text()).toContain('30%')
    })

    it('应该显示正确的进度条样式类', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.progress-success').exists()).toBe(true)
      expect(wrapper.find('.progress-running').exists()).toBe(true)
      expect(wrapper.find('.progress-pending').exists()).toBe(true)
      expect(wrapper.find('.progress-failed').exists()).toBe(true)
    })
  })

  describe('搜索功能', () => {
    it('按回车搜索应该调用 loadTasks 并重置页码', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.searchTarget = 'host-01'
      const searchInput = wrapper.find('input.search-input')
      await searchInput.setValue('host-01')
      await searchInput.trigger('keyup.enter')
      await flushPromises()

      expect(getTasks).toHaveBeenCalledTimes(2)
      expect(getTasks).toHaveBeenLastCalledWith({ page: 1, page_size: 20, search: 'host-01' })
    })
  })

  describe('过滤功能', () => {
    it('改变任务类型过滤应该调用 loadTasks 并重置页码', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.filterType = 'os_install'
      await wrapper.vm.handleFilter()
      await flushPromises()

      expect(getTasks).toHaveBeenCalledTimes(2)
      expect(getTasks).toHaveBeenLastCalledWith({ page: 1, page_size: 20, job_type: 'os_install' })
    })

    it('改变任务状态过滤应该调用 loadTasks 并重置页码', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.filterStatus = 'running'
      await wrapper.vm.handleFilter()
      await flushPromises()

      expect(getTasks).toHaveBeenCalledTimes(2)
      expect(getTasks).toHaveBeenLastCalledWith({ page: 1, page_size: 20, status: 'running' })
    })

    it('同时应用多个过滤条件应该正确传递参数', async () => {
      wrapper = createWrapper()
      await flushPromises()

      wrapper.vm.searchTarget = 'host'
      wrapper.vm.filterType = 'os_install'
      wrapper.vm.filterStatus = 'success'
      await wrapper.vm.handleFilter()
      await flushPromises()

      expect(getTasks).toHaveBeenLastCalledWith({ page: 1, page_size: 20, search: 'host', job_type: 'os_install', status: 'success' })
    })
  })

  describe('分页功能', () => {
    it('点击下一页应该调用 loadTasks 并传递新页码', async () => {
      getTasks.mockResolvedValue({ results: mockTasks, count: 100 })
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.handlePageChange(2)
      await flushPromises()

      expect(getTasks).toHaveBeenCalledTimes(2)
      expect(getTasks).toHaveBeenLastCalledWith({ page: 2, page_size: 20 })
    })

    it('应该正确计算总页数', async () => {
      getTasks.mockResolvedValue({ results: mockTasks, count: 50 })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.totalPages).toBe(3)
    })

    it('没有数据时总页数应该为1', async () => {
      getTasks.mockResolvedValue({ results: [], count: 0 })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.totalPages).toBe(1)
    })
  })

  describe('详情弹窗', () => {
    it('点击详情按钮应该打开弹窗并显示任务信息', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.findAll('button.btn-view')[0].trigger('click')
      await flushPromises()

      expect(wrapper.vm.detailDialogVisible).toBe(true)
      expect(wrapper.vm.selectedTask).toEqual(mockTasks[0])
    })

    it('弹窗应该显示任务的详细信息', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openDetailDialog(mockTasks[0])
      await flushPromises()

      expect(wrapper.text()).toContain('task-001')
      expect(wrapper.text()).toContain('系统安装')
      expect(wrapper.text()).toContain('host-01')
      expect(wrapper.text()).toContain('100%')
    })

    it('失败任务应该显示错误信息', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openDetailDialog(mockTasks[3])
      await flushPromises()

      expect(wrapper.text()).toContain('部署失败')
    })

    it('点击关闭按钮应该关闭弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openDetailDialog(mockTasks[0])
      await flushPromises()

      await wrapper.vm.closeDetailDialog()

      expect(wrapper.vm.detailDialogVisible).toBe(false)
      expect(wrapper.vm.selectedTask).toBeNull()
    })

    it('点击遮罩层应该关闭弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openDetailDialog(mockTasks[0])
      await flushPromises()

      const overlay = wrapper.find('.dialog-overlay')
      await overlay.trigger('click')

      expect(wrapper.vm.detailDialogVisible).toBe(false)
    })
  })

  describe('日期格式化', () => {
    it('应该正确格式化日期', () => {
      wrapper = createWrapper()

      const formattedDate = wrapper.vm.formatDate('2024-01-01T00:00:00Z')
      expect(formattedDate).not.toBe('-')
    })

    it('空日期应该返回"-"', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.formatDate('')).toBe('-')
      expect(wrapper.vm.formatDate(null)).toBe('-')
      expect(wrapper.vm.formatDate(undefined)).toBe('-')
    })
  })

  describe('空数据', () => {
    it('没有数据时应该显示空提示', async () => {
      getTasks.mockResolvedValue({ results: [], count: 0 })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无数据')
    })
  })

  describe('错误处理', () => {
    it('加载失败时应该显示错误信息', async () => {
      getTasks.mockRejectedValue(new Error('加载任务列表失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe('加载任务列表失败')
      expect(wrapper.find('.error').exists()).toBe(true)
    })

    it('应该使用默认错误信息', async () => {
      getTasks.mockRejectedValue({ message: '' })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe('加载任务列表失败')
    })
  })

  describe('格式化函数测试', () => {
    it('formatType 应该正确映射任务类型', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.formatType('os_install')).toBe('系统安装')
      expect(wrapper.vm.formatType('os_migrate')).toBe('系统迁移')
      expect(wrapper.vm.formatType('safeguard_deploy')).toBe('安全部署')
      expect(wrapper.vm.formatType('safeguard_rollback')).toBe('安全回滚')
      expect(wrapper.vm.formatType('hardware_collect')).toBe('硬件采集')
      expect(wrapper.vm.formatType('repo_sync')).toBe('仓库同步')
    })

    it('formatType 应该返回原值对于未知类型', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.formatType('unknown_type')).toBe('unknown_type')
    })

    it('formatStatus 应该正确映射任务状态', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.formatStatus('pending')).toBe('等待中')
      expect(wrapper.vm.formatStatus('running')).toBe('运行中')
      expect(wrapper.vm.formatStatus('success')).toBe('成功')
      expect(wrapper.vm.formatStatus('failed')).toBe('失败')
    })

    it('formatStatus 应该返回原值对于未知状态', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.formatStatus('unknown_status')).toBe('unknown_status')
    })

    it('getStatusClass 应该返回正确的样式类', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.getStatusClass('pending')).toBe('status-pending')
      expect(wrapper.vm.getStatusClass('running')).toBe('status-running')
      expect(wrapper.vm.getStatusClass('success')).toBe('status-success')
      expect(wrapper.vm.getStatusClass('failed')).toBe('status-failed')
    })

    it('getProgressClass 应该返回正确的样式类', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.getProgressClass('pending')).toBe('progress-pending')
      expect(wrapper.vm.getProgressClass('running')).toBe('progress-running')
      expect(wrapper.vm.getProgressClass('success')).toBe('progress-success')
      expect(wrapper.vm.getProgressClass('failed')).toBe('progress-failed')
    })
  })

  describe('API响应格式兼容性', () => {
    it('应该兼容直接返回数组的响应格式', async () => {
      getTasks.mockResolvedValue(mockTasks)
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.tasks).toEqual(mockTasks)
    })

    it('应该兼容带results字段的响应格式', async () => {
      getTasks.mockResolvedValue({ results: mockTasks, count: 4 })
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.tasks).toEqual(mockTasks)
      expect(wrapper.vm.totalCount).toBe(4)
    })
  })
})
