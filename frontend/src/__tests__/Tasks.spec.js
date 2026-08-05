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
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('加载中...')
      await flushPromises()
      expect(wrapper.text()).not.toContain('加载中...')
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

})
