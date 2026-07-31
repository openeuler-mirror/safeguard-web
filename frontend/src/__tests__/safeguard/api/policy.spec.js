import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  getPolicyTemplates,
  getPolicyTemplate,
  createPolicyTemplate,
  updatePolicyTemplate,
  deletePolicyTemplate,
  clonePolicyTemplate,
  getHostPolicy,
  bindHostPolicy,
  applyPolicy,
  getPolicyTask,
  getPolicyTasks
} from '@/api/safeguard/policy'
import api from '@/api/auth'

// 模拟 api 模块
vi.mock('@/api/auth', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('policy API 测试', () => {
  const mockTemplateId = 1
  const mockHostId = 1
  const mockTaskId = 'task-123'
  const mockResponse = { data: {} }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getPolicyTemplates 正确调用 API 路径', () => {
    it('应调用正确的URL', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getPolicyTemplates()

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/policy/templates/',
        { params: undefined }
      )
    })
  })

  describe('getPolicyTemplates 正确传递搜索和过滤参数', () => {
    it('应调用正确的URL并传递搜索和过滤参数', async () => {
      api.get.mockResolvedValue(mockResponse)
      const params = { search: 'test', status: 'active', page: 1 }

      await getPolicyTemplates(params)

      expect(api.get).toHaveBeenCalledWith(
        '/safeguard/policy/templates/',
        { params }
      )
    })
  })

  describe('getPolicyTemplate 正确传递模板ID', () => {
    it('应调用正确的URL并包含模板ID', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getPolicyTemplate(mockTemplateId)

      expect(api.get).toHaveBeenCalledWith(
        `/safeguard/policy/templates/${mockTemplateId}/`
      )
    })
  })

  describe('createPolicyTemplate 正确传递模板数据', () => {
    it('应调用正确的URL并传递模板数据', async () => {
      api.post.mockResolvedValue(mockResponse)
      const templateData = { name: 'Test Policy', description: 'Test' }

      await createPolicyTemplate(templateData)

      expect(api.post).toHaveBeenCalledWith(
        '/safeguard/policy/templates/',
        templateData
      )
    })
  })
})
