import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

vi.mock('@/api/auth', () => ({
  default: axios.create()
}))

describe('kickstart API', () => {
  const api = axios.create({
    baseURL: '/api',
    timeout: 10000
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Kickstart API 路径检查', () => {
    it('getKickstarts 路径包含 /kickstarts/', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/kickstarts/')

      expect(api.get).toHaveBeenCalledWith('/kickstarts/')
    })

    it('getKickstartDetail 路径包含 /kickstarts/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/kickstarts/1/')

      expect(api.get).toHaveBeenCalledWith('/kickstarts/1/')
    })

    it('createKickstart 路径为 POST /kickstarts/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)
      const data = { name: 'test-ks', content: '#test' }

      await api.post('/kickstarts/', data)

      expect(api.post).toHaveBeenCalledWith('/kickstarts/', data)
    })

    it('updateKickstart 路径为 PUT /kickstarts/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'put').mockResolvedValue(mockResponse)
      const data = { name: 'updated-ks' }

      await api.put('/kickstarts/1/', data)

      expect(api.put).toHaveBeenCalledWith('/kickstarts/1/', data)
    })

    it('deleteKickstart 路径为 DELETE /kickstarts/{id}/', async () => {
      vi.spyOn(api, 'delete').mockResolvedValue({ data: null })

      await api.delete('/kickstarts/1/')

      expect(api.delete).toHaveBeenCalledWith('/kickstarts/1/')
    })

    it('validateKickstart 路径为 POST /kickstarts/{id}/validate/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)

      await api.post('/kickstarts/1/validate/')

      expect(api.post).toHaveBeenCalledWith('/kickstarts/1/validate/')
    })

    it('previewKickstart 路径为 POST /kickstarts/{id}/preview/', async () => {
      const mockResponse = { data: { content: '#test' } }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)
      const vars = { hostname: 'test', ip: '192.168.1.1' }

      await api.post('/kickstarts/1/preview/', { vars })

      expect(api.post).toHaveBeenCalledWith('/kickstarts/1/preview/', { vars })
    })
  })

  describe('Kickstart API 参数传递', () => {
    it('getKickstarts 支持仓库过滤', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { repo: 1 }

      await api.get('/kickstarts/', { params })

      expect(api.get).toHaveBeenCalledWith('/kickstarts/', { params })
    })

    it('getKickstarts 支持搜索参数', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { search: 'centos' }

      await api.get('/kickstarts/', { params })

      expect(api.get).toHaveBeenCalledWith('/kickstarts/', { params })
    })
  })
})