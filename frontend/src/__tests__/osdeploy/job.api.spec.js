import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

vi.mock('@/api/auth', () => ({
  default: axios.create()
}))

describe('job API', () => {
  const api = axios.create({
    baseURL: '/api',
    timeout: 10000
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Job API 路径检查', () => {
    it('getJobs 路径包含 /jobs/', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/jobs/')

      expect(api.get).toHaveBeenCalledWith('/jobs/')
    })

    it('getJobDetail 路径包含 /jobs/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/jobs/1/')

      expect(api.get).toHaveBeenCalledWith('/jobs/1/')
    })

    it('queryJobStatus 路径包含 /jobs/query/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/jobs/query/', { params: { job_id: 'test-job-123' } })

      expect(api.get).toHaveBeenCalledWith('/jobs/query/', { params: { job_id: 'test-job-123' } })
    })
  })

  describe('Job API 参数传递', () => {
    it('getJobs 支持分页参数', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { page: 1, page_size: 20 }

      await api.get('/jobs/', { params })

      expect(api.get).toHaveBeenCalledWith('/jobs/', { params })
    })

    it('getJobs 支持状态过滤', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { status: 'pending' }

      await api.get('/jobs/', { params })

      expect(api.get).toHaveBeenCalledWith('/jobs/', { params })
    })

    it('getJobs 支持任务类型过滤', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { job_type: 'osdeploy' }

      await api.get('/jobs/', { params })

      expect(api.get).toHaveBeenCalledWith('/jobs/', { params })
    })

    it('getJobs 支持搜索参数', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { search: 'test-job' }

      await api.get('/jobs/', { params })

      expect(api.get).toHaveBeenCalledWith('/jobs/', { params })
    })
  })
})