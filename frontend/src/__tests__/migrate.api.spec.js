import { describe, it, expect, vi, beforeEach } from 'vitest'
import api from '@/api/auth'
import {
  getMigrates,
  getMigrate,
  createMigrateInit,
  createMigrate,
  createMigrateBack,
  getMigrateStatus
} from '@/api/migrate'

// 模拟 api 模块
vi.mock('@/api/auth', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('migrate API 测试', () => {
  const mockResponse = { data: {} }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getMigrates API 路径测试', () => {
    it('应调用正确的URL获取迁移列表', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getMigrates()

      expect(api.get).toHaveBeenCalledWith('/migrates/', { params: undefined })
    })

    it('应支持传递查询参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = { page: 1, status: 'running' }

      await getMigrates(params)

      expect(api.get).toHaveBeenCalledWith('/migrates/', { params })
    })
  })

  describe('getMigrate API 路径测试', () => {
    it('应调用正确的URL获取迁移详情', async () => {
      api.get.mockResolvedValue(mockResponse)
      const migrateId = 1

      await getMigrate(migrateId)

      expect(api.get).toHaveBeenCalledWith('/migrates/1/')
    })
  })

})
