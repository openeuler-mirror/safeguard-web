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

  describe('updatePolicyTemplate 正确传递模板ID和数据', () => {
    it('应调用正确的URL并传递模板ID和数据', async () => {
      api.put.mockResolvedValue(mockResponse)
      const templateData = { name: 'Updated Policy' }

      await updatePolicyTemplate(mockTemplateId, templateData)

      expect(api.put).toHaveBeenCalledWith(
        `/safeguard/policy/templates/${mockTemplateId}/`,
        templateData
      )
    })
  })

  describe('deletePolicyTemplate 正确传递模板ID', () => {
    it('应调用正确的URL并包含模板ID', async () => {
      api.delete.mockResolvedValue(mockResponse)

      await deletePolicyTemplate(mockTemplateId)

      expect(api.delete).toHaveBeenCalledWith(
        `/safeguard/policy/templates/${mockTemplateId}/`
      )
    })
  })

  describe('clonePolicyTemplate 正确调用克隆接口', () => {
    it('应调用正确的克隆URL', async () => {
      api.post.mockResolvedValue(mockResponse)

      await clonePolicyTemplate(mockTemplateId)

      expect(api.post).toHaveBeenCalledWith(
        `/safeguard/policy/templates/${mockTemplateId}/clone/`
      )
    })
  })

  describe('getHostPolicy 正确传递主机ID', () => {
    it('应调用正确的URL并包含主机ID', async () => {
      api.get.mockResolvedValue(mockResponse)

      await getHostPolicy(mockHostId)

      expect(api.get).toHaveBeenCalledWith(
        `/safeguard/policy/host/${mockHostId}/`
      )
    })
  })

  describe('bindHostPolicy 正确传递主机ID和策略数据', () => {
    it('应调用正确的URL并传递主机ID和策略数据', async () => {
      api.post.mockResolvedValue(mockResponse)
      const policyData = { template_id: 1 }

      await bindHostPolicy(mockHostId, policyData)

      expect(api.post).toHaveBeenCalledWith(
        `/safeguard/policy/host/${mockHostId}/bind/`,
        policyData
      )
    })
  })
})
