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

})
