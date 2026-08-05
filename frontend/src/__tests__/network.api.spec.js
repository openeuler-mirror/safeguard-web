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

})
