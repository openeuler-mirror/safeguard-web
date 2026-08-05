import { describe, it, expect, vi, beforeEach } from 'vitest'
import { getTasks, getTask, queryTasks, pageTasks } from '@/api/task'
import api from '@/api/auth'

// 模拟 api 模块
vi.mock('@/api/auth', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('task API 测试', () => {
  const mockResponse = { data: {} }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getTasks API 路径测试', () => {
    it('应调用正确的URL获取任务列表', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getTasks()

      expect(api.get).toHaveBeenCalledWith('/tasks/', { params: undefined })
    })

    it('应传递正确的参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = { page: 1, page_size: 20, status: 'running' }

      await getTasks(params)

      expect(api.get).toHaveBeenCalledWith('/tasks/', { params })
    })
  })

  describe('getTask API 路径测试', () => {
    it('应调用正确的URL获取单个任务详情', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getTask(1)

      expect(api.get).toHaveBeenCalledWith('/tasks/1/')
    })

    it('应正确传递不同的任务ID', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getTask(123)

      expect(api.get).toHaveBeenCalledWith('/tasks/123/')
    })
  })

})
