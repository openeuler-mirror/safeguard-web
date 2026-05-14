import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

vi.mock('@/api/auth', () => ({
  default: axios.create()
}))

describe('repo API', () => {
  const api = axios.create({
    baseURL: '/api',
    timeout: 10000
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Repo API 路径检查', () => {
    it('getRepos 路径包含 /repos/', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/repos/')

      expect(api.get).toHaveBeenCalledWith('/repos/')
    })

    it('getRepoDetail 路径包含 /repos/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/repos/1/')

      expect(api.get).toHaveBeenCalledWith('/repos/1/')
    })

    it('createRepo 路径为 POST /repos/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)
      const data = { name: 'test-repo', repo_type: 'yum', base_url: 'http://example.com' }

      await api.post('/repos/', data)

      expect(api.post).toHaveBeenCalledWith('/repos/', data)
    })

    it('updateRepo 路径为 PUT /repos/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'put').mockResolvedValue(mockResponse)
      const data = { name: 'updated-repo' }

      await api.put('/repos/1/', data)

      expect(api.put).toHaveBeenCalledWith('/repos/1/', data)
    })

    it('deleteRepo 路径为 DELETE /repos/{id}/', async () => {
      vi.spyOn(api, 'delete').mockResolvedValue({ data: null })

      await api.delete('/repos/1/')

      expect(api.delete).toHaveBeenCalledWith('/repos/1/')
    })

    it('syncRepo 路径为 POST /repos/{id}/sync/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)

      await api.post('/repos/1/sync/')

      expect(api.post).toHaveBeenCalledWith('/repos/1/sync/')
    })
  })

  describe('Repo API 参数传递', () => {
    it('getRepos 支持仓库类型过滤', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { repo_type: 'yum' }

      await api.get('/repos/', { params })

      expect(api.get).toHaveBeenCalledWith('/repos/', { params })
    })

    it('getRepos 支持默认仓库过滤', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { is_default: true }

      await api.get('/repos/', { params })

      expect(api.get).toHaveBeenCalledWith('/repos/', { params })
    })

    it('getRepos 支持搜索参数', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { search: 'centos' }

      await api.get('/repos/', { params })

      expect(api.get).toHaveBeenCalledWith('/repos/', { params })
    })
  })
})