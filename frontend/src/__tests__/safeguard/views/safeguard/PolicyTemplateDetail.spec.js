import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import PolicyTemplateDetail from '@/views/safeguard/PolicyTemplateDetail.vue'
import { getPolicyTemplate, updatePolicyTemplate, applyPolicy } from '@/api/safeguard/policy'
import { getHosts } from '@/api/host'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

vi.mock('@/api/safeguard/policy')
vi.mock('@/api/host')

const mockPush = vi.fn()
const mockAlert = vi.fn()
window.alert = mockAlert

describe('PolicyTemplateDetail 页面测试', () => {
  const mockTemplate = {
    id: 1,
    name: '基础安全策略',
    description: '基础安全配置',
    is_default: false,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
    config: {
      enable_firewall: true,
      enable_antivirus: true,
      enable_file_monitor: false,
      auto_update_hours: 24
    }
  }
  const mockHosts = [
    { id: 1, hostname: 'host1', ip_address: '192.168.1.1' },
    { id: 2, hostname: 'host2', ip_address: '192.168.1.2' }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockAlert.mockReset()

    getPolicyTemplate.mockResolvedValue(mockTemplate)
    getHosts.mockResolvedValue({ results: mockHosts })
    updatePolicyTemplate.mockResolvedValue({ success: true })
    applyPolicy.mockResolvedValue({ success: true })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(PolicyTemplateDetail, {
      global: {
        mocks: {
          $router: {
            push: mockPush
          },
          $route: {
            params: { id: 1 }
          }
        },
        stubs: {
          StatusBadge
        }
      }
    })
  }

})
