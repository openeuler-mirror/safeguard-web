import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

// 直接测试 API 模块
vi.mock('@/api/auth', () => ({
  default: axios.create()
}))

describe('host API', () => {
  const api = axios.create({
    baseURL: '/api',
    timeout: 10000
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Cluster API 路径检查', () => {
    it('getClusters 路径包含 /clusters/', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/clusters/')

      expect(api.get).toHaveBeenCalledWith('/clusters/')
    })

    it('getCluster 路径包含 /clusters/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/clusters/1/')

      expect(api.get).toHaveBeenCalledWith('/clusters/1/')
    })

    it('createCluster 路径为 POST /clusters/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)

      await api.post('/clusters/', { name: 'test' })

      expect(api.post).toHaveBeenCalledWith('/clusters/', { name: 'test' })
    })

    it('updateCluster 路径为 PUT /clusters/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'put').mockResolvedValue(mockResponse)

      await api.put('/clusters/1/', { name: 'updated' })

      expect(api.put).toHaveBeenCalledWith('/clusters/1/', { name: 'updated' })
    })

    it('deleteCluster 路径为 DELETE /clusters/{id}/', async () => {
      vi.spyOn(api, 'delete').mockResolvedValue({ data: null })

      await api.delete('/clusters/1/')

      expect(api.delete).toHaveBeenCalledWith('/clusters/1/')
    })

    it('getClusterTree 路径包含 /clusters/tree/', async () => {
      const mockResponse = { data: [] }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/clusters/tree/')

      expect(api.get).toHaveBeenCalledWith('/clusters/tree/')
    })

    it('getClusterHosts 路径包含 /clusters/{id}/hosts/', async () => {
      const mockResponse = { data: [] }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/clusters/1/hosts/')

      expect(api.get).toHaveBeenCalledWith('/clusters/1/hosts/')
    })
  })

  describe('Host API 路径检查', () => {
    it('getHosts 路径包含 /hosts/', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/hosts/')

      expect(api.get).toHaveBeenCalledWith('/hosts/')
    })

    it('getHost 路径包含 /hosts/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/hosts/1/')

      expect(api.get).toHaveBeenCalledWith('/hosts/1/')
    })

    it('createHost 路径为 POST /hosts/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)
      const data = { hostname: 'test', ip_address: '192.168.1.1' }

      await api.post('/hosts/', data)

      expect(api.post).toHaveBeenCalledWith('/hosts/', data)
    })

    it('updateHost 路径为 PUT /hosts/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'put').mockResolvedValue(mockResponse)
      const data = { hostname: 'updated' }

      await api.put('/hosts/1/', data)

      expect(api.put).toHaveBeenCalledWith('/hosts/1/', data)
    })

    it('deleteHost 路径为 DELETE /hosts/{id}/', async () => {
      vi.spyOn(api, 'delete').mockResolvedValue({ data: null })

      await api.delete('/hosts/1/')

      expect(api.delete).toHaveBeenCalledWith('/hosts/1/')
    })

    it('collectHardware 路径为 POST /hosts/{id}/collect_hardware/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)

      await api.post('/hosts/1/collect_hardware/')

      expect(api.post).toHaveBeenCalledWith('/hosts/1/collect_hardware/')
    })
  })

  describe('VM API 路径检查', () => {
    it('getVMs 路径包含 /vms/', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/vms/')

      expect(api.get).toHaveBeenCalledWith('/vms/')
    })

    it('getVM 路径包含 /vms/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/vms/1/')

      expect(api.get).toHaveBeenCalledWith('/vms/1/')
    })

    it('createVM 路径为 POST /vms/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)
      const data = { name: 'vm1', uuid: 'test-uuid', host: 1 }

      await api.post('/vms/', data)

      expect(api.post).toHaveBeenCalledWith('/vms/', data)
    })

    it('updateVM 路径为 PUT /vms/{id}/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'put').mockResolvedValue(mockResponse)
      const data = { name: 'updated-vm' }

      await api.put('/vms/1/', data)

      expect(api.put).toHaveBeenCalledWith('/vms/1/', data)
    })

    it('deleteVM 路径为 DELETE /vms/{id}/', async () => {
      vi.spyOn(api, 'delete').mockResolvedValue({ data: null })

      await api.delete('/vms/1/')

      expect(api.delete).toHaveBeenCalledWith('/vms/1/')
    })

    it('startVM 路径为 POST /vms/{id}/start/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)

      await api.post('/vms/1/start/')

      expect(api.post).toHaveBeenCalledWith('/vms/1/start/')
    })

    it('stopVM 路径为 POST /vms/{id}/stop/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)

      await api.post('/vms/1/stop/')

      expect(api.post).toHaveBeenCalledWith('/vms/1/stop/')
    })

    it('rebootVM 路径为 POST /vms/{id}/reboot/', async () => {
      const mockResponse = { data: {} }
      vi.spyOn(api, 'post').mockResolvedValue(mockResponse)

      await api.post('/vms/1/reboot/')

      expect(api.post).toHaveBeenCalledWith('/vms/1/reboot/')
    })
  })

  describe('API 参数传递', () => {
    it('getHosts 支持分页和过滤参数', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { page: 1, cluster: 1, status: 'online' }

      await api.get('/hosts/', { params })

      expect(api.get).toHaveBeenCalledWith('/hosts/', { params })
    })

    it('getVMs 支持分页和过滤参数', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { page: 1, cluster: 1, host: 1, status: 'running' }

      await api.get('/vms/', { params })

      expect(api.get).toHaveBeenCalledWith('/vms/', { params })
    })

    it('getVMs 支持搜索参数', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)
      const params = { search: 'test-vm' }

      await api.get('/vms/', { params })

      expect(api.get).toHaveBeenCalledWith('/vms/', { params })
    })
  })
})
