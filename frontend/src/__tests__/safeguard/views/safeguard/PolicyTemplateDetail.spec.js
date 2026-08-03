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

  describe('加载模板详情和主机列表', () => {
    it('应调用 getPolicyTemplate 和 getHosts API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getPolicyTemplate).toHaveBeenCalledWith(1)
      expect(getHosts).toHaveBeenCalled()
    })

    it('应正确设置 template 和 availableHosts 数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.template).toEqual(mockTemplate)
      expect(wrapper.vm.availableHosts).toEqual(mockHosts)
    })
  })

})
