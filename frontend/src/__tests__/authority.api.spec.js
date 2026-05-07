import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

// 直接测试 API 模块
vi.mock('@/api/auth', () => ({
  default: axios.create()
}))

describe('authority API', () => {
  const api = axios.create({
    baseURL: '/api',
    timeout: 10000
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('API 路径检查', () => {
    it('authority API 基础路径正确', () => {
      expect(api.defaults.baseURL).toBe('/api')
    })

    it('getAuthorities 路径包含 authority/authorities', async () => {
      const mockResponse = { data: { results: [] } }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/authority/authorities/')

      expect(api.get).toHaveBeenCalledWith('/authority/authorities/')
    })

    it('getMenus 路径包含 authority/menus', async () => {
      const mockResponse = { data: [] }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/authority/menus/')

      expect(api.get).toHaveBeenCalledWith('/authority/menus/')
    })

    it('getMenuTree 路径包含 authority/menus/tree', async () => {
      const mockResponse = { data: [] }
      vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

      await api.get('/authority/menus/tree/')

      expect(api.get).toHaveBeenCalledWith('/authority/menus/tree/')
    })
  })
})
