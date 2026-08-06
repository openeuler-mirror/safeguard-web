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

  describe('createMigrateInit API 路径测试', () => {
    it('应调用正确的URL并传递数据创建迁移初始化', async () => {
      api.post.mockResolvedValue(mockResponse)
      const data = { source_host: '192.168.1.1', target_host: '192.168.1.2' }

      await createMigrateInit(data)

      expect(api.post).toHaveBeenCalledWith('/migrates/init/', data)
    })
  })

  describe('createMigrate API 路径测试', () => {
    it('应调用正确的URL并传递数据创建迁移', async () => {
      api.post.mockResolvedValue(mockResponse)
      const data = { init_id: 1, options: {} }

      await createMigrate(data)

      expect(api.post).toHaveBeenCalledWith('/migrates/migrate/', data)
    })
  })

  describe('createMigrateBack API 路径测试', () => {
    it('应调用正确的URL并传递数据创建回滚', async () => {
      api.post.mockResolvedValue(mockResponse)
      const data = { migrate_id: 1, options: {} }

      await createMigrateBack(data)

      expect(api.post).toHaveBeenCalledWith('/migrates/back/', data)
    })
  })

  describe('getMigrateStatus API 路径测试', () => {
    it('应调用正确的URL获取迁移状态', async () => {
      api.get.mockResolvedValue(mockResponse)
      const migrateId = 1

      await getMigrateStatus(migrateId)

      expect(api.get).toHaveBeenCalledWith('/migrates/1/status/')
    })
  })

  describe('API 错误响应处理', () => {
    it('getMigrates 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getMigrates()).rejects.toThrow('API Error')
    })

    it('getMigrate 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getMigrate(1)).rejects.toThrow('API Error')
    })

    it('createMigrateInit 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.post.mockRejectedValue(mockError)

      await expect(createMigrateInit({ source_host: 'test' })).rejects.toThrow('API Error')
    })

    it('createMigrate 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.post.mockRejectedValue(mockError)

      await expect(createMigrate({ init_id: 1 })).rejects.toThrow('API Error')
    })

    it('createMigrateBack 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.post.mockRejectedValue(mockError)

      await expect(createMigrateBack({ migrate_id: 1 })).rejects.toThrow('API Error')
    })

    it('getMigrateStatus 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getMigrateStatus(1)).rejects.toThrow('API Error')
    })
  })
})
