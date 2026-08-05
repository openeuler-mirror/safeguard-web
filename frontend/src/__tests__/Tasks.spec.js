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

})
