import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  // LoadBalancer
  getLBs,
  getLB,
  createLB,
  updateLB,
  deleteLB,
  getLBsByProject,
  getLBsByK8s,
  getLBAzNames,
  // Listener
  getListeners,
  getListener,
  createListener,
  updateListener,
  deleteListener,
  // Pool
  getPools,
  getPool,
  createPool,
  updatePool,
  deletePool,
  // Member
  getMembers,
  getMember,
  createMember,
  updateMember,
  deleteMember,
  // HealthMonitor
  getHealthMonitors,
  getHealthMonitor,
  createHealthMonitor,
  updateHealthMonitor,
  deleteHealthMonitor,
} from '@/api/network'
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

describe('network API 测试', () => {
  const mockResponse = { data: {} }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  // ========== LoadBalancer 测试 ==========
  describe('LoadBalancer API 测试', () => {
    describe('getLBs API 路径测试', () => {
      it('应调用正确的URL获取负载均衡器列表', async () => {
        api.get.mockResolvedValue(mockResponse)
        const params = { page: 1, page_size: 10 }

        await getLBs(params)

        expect(api.get).toHaveBeenCalledWith('/lbs/', { params })
      })
    })

    describe('getLB API 路径测试', () => {
      it('应调用正确的URL获取负载均衡器详情', async () => {
        api.get.mockResolvedValue(mockResponse)

        await getLB(1)

        expect(api.get).toHaveBeenCalledWith('/lbs/1/')
      })
    })

    describe('createLB API 路径测试', () => {
      it('应调用正确的URL并传递负载均衡器数据', async () => {
        api.post.mockResolvedValue(mockResponse)
        const lbData = { name: 'test-lb', description: 'test' }

        await createLB(lbData)

        expect(api.post).toHaveBeenCalledWith('/lbs/', lbData)
      })
    })

    describe('updateLB API 路径测试', () => {
      it('应调用正确的URL并传递负载均衡器ID和数据', async () => {
        api.put.mockResolvedValue(mockResponse)
        const lbData = { name: 'updated-lb' }

        await updateLB(1, lbData)

        expect(api.put).toHaveBeenCalledWith('/lbs/1/', lbData)
      })
    })

    describe('deleteLB API 路径测试', () => {
      it('应调用正确的URL并传递负载均衡器ID', async () => {
        api.delete.mockResolvedValue(mockResponse)

        await deleteLB(1)

        expect(api.delete).toHaveBeenCalledWith('/lbs/1/')
      })
    })

    describe('getLBsByProject API 路径测试', () => {
      it('应调用正确的URL并传递项目ID', async () => {
        api.get.mockResolvedValue(mockResponse)

        await getLBsByProject(123)

        expect(api.get).toHaveBeenCalledWith('/lbs/by_project/', { params: { project_id: 123 } })
      })
    })

    describe('getLBsByK8s API 路径测试', () => {
      it('应调用正确的URL并传递K8s集群', async () => {
        api.get.mockResolvedValue(mockResponse)

        await getLBsByK8s('k8s-cluster-1')

        expect(api.get).toHaveBeenCalledWith('/lbs/by_k8s/', { params: { k8s_cluster: 'k8s-cluster-1' } })
      })
    })

    describe('getLBAzNames API 路径测试', () => {
      it('应调用正确的URL获取可用区名称列表', async () => {
        api.get.mockResolvedValue(mockResponse)

        await getLBAzNames()

        expect(api.get).toHaveBeenCalledWith('/lbs/az_names/')
      })
    })
  })

})
