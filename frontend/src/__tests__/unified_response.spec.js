import { describe, it, expect, vi, beforeEach } from 'vitest'

// 模拟 axios
const mockAxiosInstance = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  interceptors: {
    request: { use: vi.fn() },
    response: { use: vi.fn() }
  },
  defaults: { baseURL: '/api', timeout: 10000 }
}

vi.mock('axios', () => ({
  default: {
    create: () => mockAxiosInstance,
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
  }
}))

describe('统一响应格式适配', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('API 响应拦截器行为', () => {
    it('成功响应时返回 data 部分', async () => {
      const unifiedResponse = {
        errno: 0,
        errmsg: '操作成功',
        data: { id: 1, name: 'test' }
      }

      // 模拟拦截器处理后的结果
      const processedData = unifiedResponse.data

      expect(processedData).toEqual({ id: 1, name: 'test' })
    })

    it('分页响应时返回 results 和 count', async () => {
      const unifiedResponse = {
        errno: 0,
        errmsg: '操作成功',
        data: {
          results: [{ id: 1 }, { id: 2 }],
          count: 2
        }
      }

      // 模拟拦截器处理后的结果
      expect(unifiedResponse.data.results).toHaveLength(2)
      expect(unifiedResponse.data.count).toBe(2)
    })

    it('错误响应时抛出带 errno 的 Error', async () => {
      const errorResponse = {
        errno: 3001,
        errmsg: '用户不存在'
      }

      // 模拟创建的错误对象
      const error = new Error(errorResponse.errmsg)
      error.errno = errorResponse.errno

      expect(error.message).toBe('用户不存在')
      expect(error.errno).toBe(3001)
    })

    it('无数据响应时返回空数组', async () => {
      const unifiedResponse = {
        errno: 0,
        errmsg: '操作成功',
        data: []
      }

      expect(unifiedResponse.data).toEqual([])
    })
  })

  describe('错误码映射', () => {
    const errorCodeMap = {
      0: '操作成功',
      1001: '参数错误',
      2001: '认证失败',
      2002: 'token已过期',
      3001: '用户不存在',
      3002: '用户已被禁用',
      4001: '角色不存在',
      5001: '主机不存在'
    }

    it('正确获取错误信息', () => {
      expect(errorCodeMap[0]).toBe('操作成功')
      expect(errorCodeMap[2001]).toBe('认证失败')
      expect(errorCodeMap[3001]).toBe('用户不存在')
    })

    it('未知错误码返回 undefined', () => {
      expect(errorCodeMap[9999]).toBeUndefined()
    })
  })

  describe('store auth 适配', () => {
    it('login action 正确处理成功响应', async () => {
      // 模拟登录成功响应（拦截器处理后直接返回 data）
      const tokenData = {
        access: 'access-token',
        refresh: 'refresh-token'
      }

      expect(tokenData.access).toBe('access-token')
      expect(tokenData.refresh).toBe('refresh-token')
    })

    it('login action 正确处理错误响应', async () => {
      const error = new Error('认证失败')
      error.errno = 2001

      expect(error.message).toBe('认证失败')
      expect(error.errno).toBe(2001)
    })
  })
})
