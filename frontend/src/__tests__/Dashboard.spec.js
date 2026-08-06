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

})
