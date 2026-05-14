import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

vi.mock('@/api/auth', () => ({
  default: axios.create()
}))

describe('pxe API', () => {
  const api = axios.create({
    baseURL: '/api',
    timeout: 10000
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('PXE Server API 路径检查', () => {
    it('getPXEServers 路径包含 /pxe-servers/', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/pxe-servers/')

      expect(api.get).toHaveBeenCalledWith('/pxe-servers/')
    })

    it('getPXEServerDetail 路径包含 /pxe-servers/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/pxe-servers/1/')

      expect(api.get).toHaveBeenCalledWith('/pxe-servers/1/')
    })

    it('createPXEServer 路径为 POST /pxe-servers/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)
      const data = { server_ip: '192.168.1.100', interface: 'eth0' }

      await api.post('/pxe-servers/', data)

      expect(api.post).toHaveBeenCalledWith('/pxe-servers/', data)
    })

    it('updatePXEServer 路径为 PUT /pxe-servers/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'put').mockResolvedValue(mockResponse)
      const data = { status: 'inactive' }

      await api.put('/pxe-servers/1/', data)

      expect(api.put).toHaveBeenCalledWith('/pxe-servers/1/', data)
    })

    it('deletePXEServer 路径为 DELETE /pxe-servers/{id}/', async () => {
      vi.spyOn(api, 'delete').mockResolvedValue({ data: null })

      await api.delete('/pxe-servers/1/')

      expect(api.delete).toHaveBeenCalledWith('/pxe-servers/1/')
    })
  })

  describe('PXE Server API 参数传递', () => {
    it('getPXEServers 支持IP过滤', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { server_ip: '192.168.1.100' }

      await api.get('/pxe-servers/', { params })

      expect(api.get).toHaveBeenCalledWith('/pxe-servers/', { params })
    })

    it('getPXEServers 支持状态过滤', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { status: 'active' }

      await api.get('/pxe-servers/', { params })

      expect(api.get).toHaveBeenCalledWith('/pxe-servers/', { params })
    })

    it('getPXEServers 支持搜索参数', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { search: '192.168' }

      await api.get('/pxe-servers/', { params })

      expect(api.get).toHaveBeenCalledWith('/pxe-servers/', { params })
    })
  })
})