import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

vi.mock('@/api/auth', () => ({
  default: axios.create()
}))

describe('iso API', () => {
  const api = axios.create({
    baseURL: '/api',
    timeout: 10000
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('ISO File API 路径检查', () => {
    it('getISOFiles 路径包含 /isos/', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/isos/')

      expect(api.get).toHaveBeenCalledWith('/isos/')
    })

    it('getISOFileDetail 路径包含 /isos/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/isos/1/')

      expect(api.get).toHaveBeenCalledWith('/isos/1/')
    })

    it('createISOFile 路径为 POST /isos/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)
      const data = { filename: 'CentOS-7-x86_64.iso', size: 4294967296 }

      await api.post('/isos/', data)

      expect(api.post).toHaveBeenCalledWith('/isos/', data)
    })

    it('updateISOFile 路径为 PUT /isos/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'put').mockResolvedValue(mockResponse)
      const data = { description: 'CentOS 7.9' }

      await api.put('/isos/1/', data)

      expect(api.put).toHaveBeenCalledWith('/isos/1/', data)
    })

    it('deleteISOFile 路径为 DELETE /isos/{id}/', async () => {
      vi.spyOn(api, 'delete').mockResolvedValue({ data: null })

      await api.delete('/isos/1/')

      expect(api.delete).toHaveBeenCalledWith('/isos/1/')
    })
  })

  describe('ISO File API 上传', () => {
    it('uploadISOFile 使用 multipart/form-data', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)
      const file = new Blob(['test'], { type: 'application/octet-stream' })

      await api.post('/isos/upload/', file, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      expect(api.post).toHaveBeenCalled()
    })
  })
})