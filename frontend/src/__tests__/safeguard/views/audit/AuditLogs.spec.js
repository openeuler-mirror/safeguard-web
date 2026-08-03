import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AuditLogs from '@/views/audit/AuditLogs.vue'
import { getAuditLogs } from '@/api/safeguard/audit'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

vi.mock('@/api/safeguard/audit')

describe('AuditLogs 页面测试', () => {
  const mockLogs = [
    {
      id: 1,
      timestamp: '2024-01-01T10:00:00Z',
      username: 'admin',
      action: 'create',
      resource_type: 'policy',
      resource_id: 1,
      ip_address: '192.168.1.1'
    },
    {
      id: 2,
      timestamp: '2024-01-01T11:00:00Z',
      username: 'user1',
      action: 'login',
      resource_type: 'user',
      resource_id: 2,
      ip_address: '192.168.1.2'
    }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    getAuditLogs.mockResolvedValue({ results: mockLogs })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(AuditLogs, {
      global: {
        stubs: {
          StatusBadge
        }
      }
    })
  }

  describe('页面加载时显示 loading 状态', () => {
    it('初始 loading 应为 true', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(true)
    })

    it('数据加载完成后应隐藏 loading 状态', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('加载审计日志', () => {
    it('应调用 getAuditLogs API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getAuditLogs).toHaveBeenCalledWith({})
    })

    it('应正确设置 logs 数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.logs).toEqual(mockLogs)
    })
  })

})
