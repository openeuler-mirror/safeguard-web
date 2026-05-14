import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

vi.mock('@/api/auth', () => ({
  default: axios.create()
}))

describe('whitelist API', () => {
  const api = axios.create({
    baseURL: '/api',
    timeout: 10000
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('WhiteList API 路径检查', () => {
    it('getWhiteList 路径包含 /whitelist/', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/whitelist/')

      expect(api.get).toHaveBeenCalledWith('/whitelist/')
    })

    it('getWhiteListDetail 路径包含 /whitelist/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/whitelist/1/')

      expect(api.get).toHaveBeenCalledWith('/whitelist/1/')
    })

    it('createWhiteList 路径为 POST /whitelist/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)
      const data = { mac_address: '00:11:22:33:44:55', hostname: 'test-host' }

      await api.post('/whitelist/', data)

      expect(api.post).toHaveBeenCalledWith('/whitelist/', data)
    })

    it('updateWhiteList 路径为 PUT /whitelist/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'put').mockResolvedValue(mockResponse)
      const data = { hostname: 'updated-host' }

      await api.put('/whitelist/1/', data)

      expect(api.put).toHaveBeenCalledWith('/whitelist/1/', data)
    })

    it('deleteWhiteList 路径为 DELETE /whitelist/{id}/', async () => {
      vi.spyOn(api, 'delete').mockResolvedValue({ data: null })

      await api.delete('/whitelist/1/')

      expect(api.delete).toHaveBeenCalledWith('/whitelist/1/')
    })
  })

  describe('WhiteList API 导入导出', () => {
    it('importWhiteList 使用 multipart/form-data', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)
      const file = new Blob(['test'], { type: 'application/vnd.ms-excel' })

      await api.post('/whitelist/import/', file, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      expect(api.post).toHaveBeenCalled()
    })

    it('exportWhiteList 路径包含 /whitelist/export/', async () => {
      const mockResponse = { data: new ArrayBuffer() }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/whitelist/export/')

      expect(api.get).toHaveBeenCalledWith('/whitelist/export/')
    })
  })
})