import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Dashboard from '@/views/Dashboard.vue'
import { getHosts, getVMs, getClusters } from '@/api/host'
import { getTasks } from '@/api/task'

vi.mock('@/api/host')
vi.mock('@/api/task')

describe('Dashboard 页面测试', () => {
  let wrapper

  const mockHosts = { results: [], total: 10 }
  const mockVMs = { results: [], total: 25 }
  const mockClusters = { results: [], total: 3 }
  const mockTasks = {
    results: [
      { id: 1, name: '安装系统', status: 'SUCCESS', task_id: 'task-1' },
      { id: 2, name: '迁移系统', status: 'RUNNING', task_id: 'task-2' },
      { id: 3, name: '部署应用', status: 'PENDING', task_id: 'task-3' }
    ], total: 3
  }

  beforeEach(() => {
    vi.clearAllMocks()
    getHosts.mockResolvedValue(mockHosts)
    getVMs.mockResolvedValue(mockVMs)
    getClusters.mockResolvedValue(mockClusters)
    getTasks.mockResolvedValue(mockTasks)
    vi.spyOn(console, 'error').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Dashboard, {
      global: {
        mocks: {
          $router: {
            push: vi.fn()
          }
        },
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用所有统计数据 API', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getHosts).toHaveBeenCalledWith({ page_size: 1 })
      expect(getVMs).toHaveBeenCalledWith({ page_size: 1 })
      expect(getClusters).toHaveBeenCalledWith({ page_size: 1 })
      expect(getTasks).toHaveBeenCalledWith({ page_size: 1 })
    })

    it('应该显示统计数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('10')
      expect(wrapper.text()).toContain('25')
      expect(wrapper.text()).toContain('3')
      expect(wrapper.text()).toContain('2')
    })

    it('应该显示最近任务列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('安装系统')
      expect(wrapper.text()).toContain('迁移系统')
      expect(wrapper.text()).toContain('部署应用')
    })

    it('应该显示页面标题和描述', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('控制面板')
      expect(wrapper.text()).toContain('一站式服务器运维管理中心')
    })
  })

  describe('快速入口', () => {
    it('应该显示所有快速入口', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('添加主机')
      expect(wrapper.text()).toContain('安装系统')
      expect(wrapper.text()).toContain('迁移系统')
      expect(wrapper.text()).toContain('配置负载均衡')
      expect(wrapper.text()).toContain('查看任务')
    })
  })

  describe('工具函数', () => {
    it('formatStatus 应该正确格式化状态', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatStatus('SUCCESS')).toBe('成功')
      expect(wrapper.vm.formatStatus('FAILURE')).toBe('失败')
      expect(wrapper.vm.formatStatus('RUNNING')).toBe('运行中')
      expect(wrapper.vm.formatStatus('PENDING')).toBe('等待中')
      expect(wrapper.vm.formatStatus('RETRY')).toBe('重试中')
      expect(wrapper.vm.formatStatus('UNKNOWN')).toBe('UNKNOWN')
      expect(wrapper.vm.formatStatus(null)).toBe('未知')
    })
  })

  describe('错误处理', () => {
    it('加载统计数据失败时应该在控制台打印错误', async () => {
      getHosts.mockRejectedValue(new Error('加载失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(console.error).toHaveBeenCalledWith('加载概览数据失败', expect.any(Error))
    })

    it('加载最近任务失败时应该在控制台打印错误', async () => {
      getTasks.mockRejectedValue(new Error('加载失败'))
      wrapper = createWrapper()
      await flushPromises()

      expect(console.error).toHaveBeenCalledWith('加载最近任务失败', expect.any(Error))
    })
  })
})
