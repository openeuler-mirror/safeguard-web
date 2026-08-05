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

  describe('queryTasks API 路径测试', () => {
    it('应调用正确的URL进行任务查询', async () => {
      api.post.mockResolvedValue(mockResponse)
      const queryData = { search: 'test', job_type: 'os_install' }

      await queryTasks(queryData)

      expect(api.post).toHaveBeenCalledWith('/tasks/query/', queryData)
    })

    it('应正确传递查询数据', async () => {
      api.post.mockResolvedValue(mockResponse)
      const queryData = { status: 'success', target: 'host1' }

      await queryTasks(queryData)

      expect(api.post).toHaveBeenCalledWith('/tasks/query/', queryData)
    })
  })

  describe('pageTasks API 路径测试', () => {
    it('应调用正确的URL进行分页任务查询', async () => {
      api.post.mockResolvedValue(mockResponse)
      const pageData = { page: 1, page_size: 20 }
      const params = { sort: 'created_at' }

      await pageTasks(pageData, params)

      expect(api.post).toHaveBeenCalledWith('/tasks/page/', pageData, { params })
    })

    it('应正确传递分页数据和参数', async () => {
      api.post.mockResolvedValue(mockResponse)
      const pageData = { page: 2, page_size: 50, search: 'test' }
      const params = { sort: '-created_at', status: 'pending' }

      await pageTasks(pageData, params)

      expect(api.post).toHaveBeenCalledWith('/tasks/page/', pageData, { params })
    })

    it('应正确处理params为undefined的情况', async () => {
      api.post.mockResolvedValue(mockResponse)
      const pageData = { page: 1 }

      await pageTasks(pageData)

      expect(api.post).toHaveBeenCalledWith('/tasks/page/', pageData, { params: undefined })
    })
  })

})
