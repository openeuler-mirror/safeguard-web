import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import PolicyTasks from '@/views/safeguard/PolicyTasks.vue'
import { getPolicyTasks, getPolicyTask } from '@/api/safeguard/policy'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

vi.mock('@/api/safeguard/policy')

const mockAlert = vi.fn()
window.alert = mockAlert

describe('PolicyTasks 页面测试', () => {
  const mockTasks = [
    {
      id: 1,
      template_name: '基础安全策略',
      host_count: 5,
      status: 'success',
      created_at: '2024-01-01T00:00:00Z',
      host_names: ['host1', 'host2'],
      result: { success: 5, failed: 0 }
    },
    {
      id: 2,
      template_name: '高级安全策略',
      host_count: 3,
      status: 'pending',
      created_at: '2024-01-02T00:00:00Z'
    }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockAlert.mockReset()

    getPolicyTasks.mockResolvedValue({ results: mockTasks })
    getPolicyTask.mockResolvedValue(mockTasks[0])
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(PolicyTasks, {
      global: {
        stubs: {
          StatusBadge
        }
      }
    })
  }

})
