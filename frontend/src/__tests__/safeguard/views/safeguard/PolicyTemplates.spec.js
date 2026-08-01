import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import PolicyTemplates from '@/views/safeguard/PolicyTemplates.vue'
import {
  getPolicyTemplates,
  createPolicyTemplate,
  updatePolicyTemplate,
  deletePolicyTemplate,
  clonePolicyTemplate,
  applyPolicy
} from '@/api/safeguard/policy'
import { getHosts } from '@/api/host'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

vi.mock('@/api/safeguard/policy')
vi.mock('@/api/host')

const mockPush = vi.fn()
const mockAlert = vi.fn()
window.alert = mockAlert

describe('PolicyTemplates 页面测试', () => {
  const mockTemplates = [
    { id: 1, name: '基础安全策略', description: '基础的安全配置', is_default: true, created_at: '2024-01-01T00:00:00Z', config: {} },
    { id: 2, name: '高级安全策略', description: '更严格的安全配置', is_default: false, created_at: '2024-01-02T00:00:00Z', config: {} }
  ]
  const mockHosts = [
    { id: 1, hostname: 'host1', ip_address: '192.168.1.1' },
    { id: 2, hostname: 'host2', ip_address: '192.168.1.2' }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockAlert.mockReset()

    getPolicyTemplates.mockResolvedValue({ results: mockTemplates })
    getHosts.mockResolvedValue({ results: mockHosts })
    createPolicyTemplate.mockResolvedValue({ success: true })
    updatePolicyTemplate.mockResolvedValue({ success: true })
    deletePolicyTemplate.mockResolvedValue({ success: true })
    clonePolicyTemplate.mockResolvedValue({ success: true })
    applyPolicy.mockResolvedValue({ success: true })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(PolicyTemplates, {
      global: {
        mocks: {
          $router: {
            push: mockPush
          }
        },
        stubs: {
          StatusBadge
        }
      }
    })
  }

})
