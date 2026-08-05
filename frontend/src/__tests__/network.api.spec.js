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

  // ========== Listener 测试 ==========
  describe('Listener API 测试', () => {
    describe('getListeners API 路径测试', () => {
      it('应调用正确的URL获取监听器列表', async () => {
        api.get.mockResolvedValue(mockResponse)
        const params = { page: 1, page_size: 10 }

        await getListeners(params)

        expect(api.get).toHaveBeenCalledWith('/listeners/', { params })
      })
    })

    describe('getListener API 路径测试', () => {
      it('应调用正确的URL获取监听器详情', async () => {
        api.get.mockResolvedValue(mockResponse)

        await getListener(1)

        expect(api.get).toHaveBeenCalledWith('/listeners/1/')
      })
    })

    describe('createListener API 路径测试', () => {
      it('应调用正确的URL并传递监听器数据', async () => {
        api.post.mockResolvedValue(mockResponse)
        const listenerData = { name: 'test-listener', protocol: 'HTTP' }

        await createListener(listenerData)

        expect(api.post).toHaveBeenCalledWith('/listeners/', listenerData)
      })
    })

    describe('updateListener API 路径测试', () => {
      it('应调用正确的URL并传递监听器ID和数据', async () => {
        api.put.mockResolvedValue(mockResponse)
        const listenerData = { name: 'updated-listener' }

        await updateListener(1, listenerData)

        expect(api.put).toHaveBeenCalledWith('/listeners/1/', listenerData)
      })
    })

    describe('deleteListener API 路径测试', () => {
      it('应调用正确的URL并传递监听器ID', async () => {
        api.delete.mockResolvedValue(mockResponse)

        await deleteListener(1)

        expect(api.delete).toHaveBeenCalledWith('/listeners/1/')
      })
    })
  })

  // ========== Pool 测试 ==========
  describe('Pool API 测试', () => {
    describe('getPools API 路径测试', () => {
      it('应调用正确的URL获取后端池列表', async () => {
        api.get.mockResolvedValue(mockResponse)
        const params = { page: 1, page_size: 10 }

        await getPools(params)

        expect(api.get).toHaveBeenCalledWith('/pools/', { params })
      })
    })

    describe('getPool API 路径测试', () => {
      it('应调用正确的URL获取后端池详情', async () => {
        api.get.mockResolvedValue(mockResponse)

        await getPool(1)

        expect(api.get).toHaveBeenCalledWith('/pools/1/')
      })
    })

    describe('createPool API 路径测试', () => {
      it('应调用正确的URL并传递后端池数据', async () => {
        api.post.mockResolvedValue(mockResponse)
        const poolData = { name: 'test-pool', protocol: 'HTTP' }

        await createPool(poolData)

        expect(api.post).toHaveBeenCalledWith('/pools/', poolData)
      })
    })

    describe('updatePool API 路径测试', () => {
      it('应调用正确的URL并传递后端池ID和数据', async () => {
        api.put.mockResolvedValue(mockResponse)
        const poolData = { name: 'updated-pool' }

        await updatePool(1, poolData)

        expect(api.put).toHaveBeenCalledWith('/pools/1/', poolData)
      })
    })

    describe('deletePool API 路径测试', () => {
      it('应调用正确的URL并传递后端池ID', async () => {
        api.delete.mockResolvedValue(mockResponse)

        await deletePool(1)

        expect(api.delete).toHaveBeenCalledWith('/pools/1/')
      })
    })
  })

  // ========== Member 测试 ==========
  describe('Member API 测试', () => {
    describe('getMembers API 路径测试', () => {
      it('应调用正确的URL获取池成员列表', async () => {
        api.get.mockResolvedValue(mockResponse)
        const params = { page: 1, page_size: 10 }

        await getMembers(params)

        expect(api.get).toHaveBeenCalledWith('/members/', { params })
      })
    })

    describe('getMember API 路径测试', () => {
      it('应调用正确的URL获取池成员详情', async () => {
        api.get.mockResolvedValue(mockResponse)

        await getMember(1)

        expect(api.get).toHaveBeenCalledWith('/members/1/')
      })
    })

    describe('createMember API 路径测试', () => {
      it('应调用正确的URL并传递池成员数据', async () => {
        api.post.mockResolvedValue(mockResponse)
        const memberData = { name: 'test-member', address: '192.168.1.1' }

        await createMember(memberData)

        expect(api.post).toHaveBeenCalledWith('/members/', memberData)
      })
    })

    describe('updateMember API 路径测试', () => {
      it('应调用正确的URL并传递池成员ID和数据', async () => {
        api.put.mockResolvedValue(mockResponse)
        const memberData = { name: 'updated-member' }

        await updateMember(1, memberData)

        expect(api.put).toHaveBeenCalledWith('/members/1/', memberData)
      })
    })

    describe('deleteMember API 路径测试', () => {
      it('应调用正确的URL并传递池成员ID', async () => {
        api.delete.mockResolvedValue(mockResponse)

        await deleteMember(1)

        expect(api.delete).toHaveBeenCalledWith('/members/1/')
      })
    })
  })

  // ========== HealthMonitor 测试 ==========
  describe('HealthMonitor API 测试', () => {
    describe('getHealthMonitors API 路径测试', () => {
      it('应调用正确的URL获取健康检查列表', async () => {
        api.get.mockResolvedValue(mockResponse)
        const params = { page: 1, page_size: 10 }

        await getHealthMonitors(params)

        expect(api.get).toHaveBeenCalledWith('/health-monitors/', { params })
      })
    })

    describe('getHealthMonitor API 路径测试', () => {
      it('应调用正确的URL获取健康检查详情', async () => {
        api.get.mockResolvedValue(mockResponse)

        await getHealthMonitor(1)

        expect(api.get).toHaveBeenCalledWith('/health-monitors/1/')
      })
    })

    describe('createHealthMonitor API 路径测试', () => {
      it('应调用正确的URL并传递健康检查数据', async () => {
        api.post.mockResolvedValue(mockResponse)
        const hmData = { name: 'test-hm', type: 'HTTP' }

        await createHealthMonitor(hmData)

        expect(api.post).toHaveBeenCalledWith('/health-monitors/', hmData)
      })
    })

    describe('updateHealthMonitor API 路径测试', () => {
      it('应调用正确的URL并传递健康检查ID和数据', async () => {
        api.put.mockResolvedValue(mockResponse)
        const hmData = { name: 'updated-hm' }

        await updateHealthMonitor(1, hmData)

        expect(api.put).toHaveBeenCalledWith('/health-monitors/1/', hmData)
      })
    })

    describe('deleteHealthMonitor API 路径测试', () => {
      it('应调用正确的URL并传递健康检查ID', async () => {
        api.delete.mockResolvedValue(mockResponse)

        await deleteHealthMonitor(1)

        expect(api.delete).toHaveBeenCalledWith('/health-monitors/1/')
      })
    })
  })

  // ========== API 错误响应处理 ==========
  describe('API 错误响应处理', () => {
    it('getLBs 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getLBs({})).rejects.toThrow('API Error')
    })

    it('createLB 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.post.mockRejectedValue(mockError)

      await expect(createLB({})).rejects.toThrow('API Error')
    })

    it('getListeners 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getListeners({})).rejects.toThrow('API Error')
    })

    it('getPools 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getPools({})).rejects.toThrow('API Error')
    })

    it('getMembers 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getMembers({})).rejects.toThrow('API Error')
    })

    it('getHealthMonitors 应正确处理API错误', async () => {
      const mockError = new Error('API Error')
      api.get.mockRejectedValue(mockError)

      await expect(getHealthMonitors({})).rejects.toThrow('API Error')
    })
  })
})
