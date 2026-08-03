import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import PolicyTasks from '@/views/safeguard/PolicyTasks.vue'
import { getPolicyTasks, getPolicyTask } from '@/api/safeguard/policy'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

vi.mock('@/api/safeguard/policy')

const mockAlert = vi.fn()
window.alert = mockAlert

describe('PolicyTasks 页面测试', () => {
  const mockTasks = [
    {
      id: 1,
      template_name: '基础安全策略',
      host_count: 5,
      status: 'success',
      created_at: '2024-01-01T00:00:00Z',
      host_names: ['host1', 'host2'],
      result: { success: 5, failed: 0 }
    },
    {
      id: 2,
      template_name: '高级安全策略',
      host_count: 3,
      status: 'pending',
      created_at: '2024-01-02T00:00:00Z'
    }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockAlert.mockReset()

    getPolicyTasks.mockResolvedValue({ results: mockTasks })
    getPolicyTask.mockResolvedValue(mockTasks[0])
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(PolicyTasks, {
      global: {
        stubs: {
          StatusBadge
        }
      }
    })
  }

  describe('页面加载时显示 loading 状态', () => {
    it('初始 loading 应为 true', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(true)
    })

    it('数据加载完成后应隐藏 loading 状态', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('加载任务列表', () => {
    it('应调用 getPolicyTasks API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getPolicyTasks).toHaveBeenCalledWith({})
    })

    it('应正确设置 tasks 数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.tasks).toEqual(mockTasks)
    })
  })

  describe('状态筛选', () => {
    it('改变 filterStatus 时应重新加载任务', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.setData({ filterStatus: 'success' })
      await wrapper.vm.loadTasks()

      expect(getPolicyTasks).toHaveBeenCalledWith({ status: 'success' })
    })
  })

  describe('任务详情弹窗', () => {
    it('点击查看详情应打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.viewTask(mockTasks[0])
      await flushPromises()

      expect(getPolicyTask).toHaveBeenCalledWith(1)
      expect(wrapper.vm.detailDialogVisible).toBe(true)
      expect(wrapper.vm.selectedTask).toEqual(mockTasks[0])
    })

    it('获取详情失败时应 alert', async () => {
      getPolicyTask.mockRejectedValue(new Error('获取任务详情失败'))

      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.viewTask(mockTasks[0])
      await flushPromises()

      expect(mockAlert).toHaveBeenCalledWith('获取任务详情失败')
    })
  })

})
