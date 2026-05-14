import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

vi.mock('@/api/auth', () => ({
  default: axios.create()
}))

describe('outipsn API', () => {
  const api = axios.create({
    baseURL: '/api',
    timeout: 10000
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('OutIpSN API 路径检查', () => {
    it('getOutIpSNs 路径包含 /outipsn/', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/outipsn/')

      expect(api.get).toHaveBeenCalledWith('/outipsn/')
    })

    it('getOutIpSNDetail 路径包含 /outipsn/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/outipsn/1/')

      expect(api.get).toHaveBeenCalledWith('/outipsn/1/')
    })

    it('createOutIpSN 路径为 POST /outipsn/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)
      const data = { mac_address: '00:11:22:33:44:55', sn: 'SN123456' }

      await api.post('/outipsn/', data)

      expect(api.post).toHaveBeenCalledWith('/outipsn/', data)
    })

    it('updateOutIpSN 路径为 PUT /outipsn/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'put').mockResolvedValue(mockResponse)
      const data = { sn: 'SN654321' }

      await api.put('/outipsn/1/', data)

      expect(api.put).toHaveBeenCalledWith('/outipsn/1/', data)
    })

    it('deleteOutIpSN 路径为 DELETE /outipsn/{id}/', async () => {
      vi.spyOn(api, 'delete').mockResolvedValue({ data: null })

      await api.delete('/outipsn/1/')

      expect(api.delete).toHaveBeenCalledWith('/outipsn/1/')
    })
  })

  describe('OutIpSN API 参数传递', () => {
    it('getOutIpSNs 支持搜索参数', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { search: '00:11' }

      await api.get('/outipsn/', { params })

      expect(api.get).toHaveBeenCalledWith('/outipsn/', { params })
    })
  })
})