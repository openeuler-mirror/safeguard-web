import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostSafeguardPolicy from '@/views/hosts/safeguard/HostSafeguardPolicy.vue'
import { getHostPolicy, bindHostPolicy } from '@/api/safeguard/policy'
import { getPolicyTemplates } from '@/api/safeguard/policy'
import { getHost } from '@/api/host'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

vi.mock('@/api/safeguard/policy')
vi.mock('@/api/host')

const mockPush = vi.fn()
const mockAlert = vi.fn()
window.alert = mockAlert

describe('HostSafeguardPolicy 页面测试', () => {
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockPolicy = {
    id: 1,
    template_name: '基础安全策略',
    status: 'active',
    bound_at: '2024-01-01T00:00:00Z',
    config: {
      enable_firewall: true,
      enable_antivirus: true,
      enable_file_monitor: false,
      auto_update_hours: 24
    }
  }
  const mockTemplates = [
    { id: 1, name: '基础安全策略' },
    { id: 2, name: '高级安全策略' }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockAlert.mockReset()

    getHost.mockResolvedValue(mockHost)
    getHostPolicy.mockResolvedValue(mockPolicy)
    getPolicyTemplates.mockResolvedValue({ results: mockTemplates })
    bindHostPolicy.mockResolvedValue({ success: true })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostSafeguardPolicy, {
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

  describe('加载主机、策略和模板列表', () => {
    it('应调用 getHost、getHostPolicy 和 getPolicyTemplates API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHost).toHaveBeenCalledWith(1)
      expect(getHostPolicy).toHaveBeenCalledWith(1)
      expect(getPolicyTemplates).toHaveBeenCalled()
    })

    it('应正确设置 host、currentPolicy 和 templates 数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.host).toEqual(mockHost)
      expect(wrapper.vm.currentPolicy).toEqual(mockPolicy)
      expect(wrapper.vm.templates).toEqual(mockTemplates)
    })

    it('没有策略时 currentPolicy 应为 null', async () => {
      getHostPolicy.mockResolvedValue(null)

      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.currentPolicy).toBeNull()
    })
  })

  describe('绑定策略弹窗', () => {
    it('点击绑定按钮应打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openBindDialog()
      expect(wrapper.vm.bindDialogVisible).toBe(true)
    })

    it('表单验证 - 未选择模板时应显示错误', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openBindDialog()
      await wrapper.vm.submitBind()
      expect(wrapper.vm.errors.template_id).toBe('请选择策略模板')
    })

    it('绑定成功后应关闭弹窗、alert 并刷新数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openBindDialog()
      await wrapper.setData({ bindForm: { template_id: 1 } })
      await wrapper.vm.submitBind()
      await flushPromises()

      expect(bindHostPolicy).toHaveBeenCalledWith(1, { template_id: 1 })
      expect(wrapper.vm.bindDialogVisible).toBe(false)
      expect(mockAlert).toHaveBeenCalledWith('策略绑定成功')
    })

    it('绑定失败时应显示错误', async () => {
      bindHostPolicy.mockRejectedValue(new Error('操作失败'))

      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openBindDialog()
      await wrapper.setData({ bindForm: { template_id: 1 } })
      await wrapper.vm.submitBind()
      await flushPromises()

      expect(wrapper.vm.formError).toBe('操作失败')
    })
  })

  describe('formatDate 方法测试', () => {
    it('应正确格式化日期', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const result = wrapper.vm.formatDate('2024-01-01T00:00:00Z')
      expect(typeof result).toBe('string')
    })

    it('应处理 null 日期', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const result = wrapper.vm.formatDate(null)
      expect(result).toBe('-')
    })
  })

  describe('API 失败时显示错误信息', () => {
    it('getHost 失败时应显示错误', async () => {
      getHost.mockRejectedValue(new Error('加载数据失败'))

      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.error).toBe('加载数据失败')
    })
  })

})
