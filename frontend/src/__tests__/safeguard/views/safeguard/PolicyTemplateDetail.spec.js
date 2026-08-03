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

  describe('编辑模板弹窗', () => {
    it('点击编辑按钮应打开弹窗并填充数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openEditDialog()
      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.form.name).toBe('基础安全策略')
      expect(wrapper.vm.form.description).toBe('基础安全配置')
      expect(wrapper.vm.form.config.enable_firewall).toBe(true)
    })

    it('表单验证 - 名称为空时应显示错误', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openEditDialog()
      await wrapper.setData({ form: { ...wrapper.vm.form, name: '' } })
      await wrapper.vm.submitForm()
      expect(wrapper.vm.errors.name).toBe('请输入模板名称')
    })

    it('编辑成功后应关闭弹窗并刷新数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openEditDialog()
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updatePolicyTemplate).toHaveBeenCalledWith(1, expect.any(Object))
      expect(wrapper.vm.dialogVisible).toBe(false)
    })

    it('编辑失败时应显示错误', async () => {
      updatePolicyTemplate.mockRejectedValue(new Error('操作失败'))

      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openEditDialog()
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(wrapper.vm.formError).toBe('操作失败')
    })
  })

  describe('应用策略弹窗', () => {
    it('点击应用按钮应打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openApplyDialog()
      expect(wrapper.vm.applyDialogVisible).toBe(true)
    })

    it('未选择主机时应 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openApplyDialog()
      await wrapper.setData({ applyForm: { host_ids: [] } })
      await wrapper.vm.submitApply()

      expect(mockAlert).toHaveBeenCalledWith('请至少选择一个主机')
    })

    it('应用成功后应 alert 并跳转到任务页面', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openApplyDialog()
      await wrapper.setData({ applyForm: { host_ids: [1, 2] } })
      await wrapper.vm.submitApply()
      await flushPromises()

      expect(applyPolicy).toHaveBeenCalledWith(1, [1, 2])
      expect(mockAlert).toHaveBeenCalledWith('策略下发任务已创建')
      expect(mockPush).toHaveBeenCalledWith('/safeguard/policy-tasks')
    })

    it('应用失败时应显示错误', async () => {
      applyPolicy.mockRejectedValue(new Error('应用失败'))

      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openApplyDialog()
      await wrapper.setData({ applyForm: { host_ids: [1] } })
      await wrapper.vm.submitApply()
      await flushPromises()

      expect(mockAlert).toHaveBeenCalledWith('应用失败')
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
    it('getPolicyTemplate 失败时应显示错误', async () => {
      getPolicyTemplate.mockRejectedValue(new Error('加载模板详情失败'))

      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.error).toBe('加载模板详情失败')
    })
  })

  describe('返回按钮', () => {
    it('点击返回应跳转到模板列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.goBack()
      expect(mockPush).toHaveBeenCalledWith('/safeguard/policy-templates')
    })
  })

  describe('弹窗关闭功能', () => {
    it('应能关闭编辑弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openEditDialog()
      expect(wrapper.vm.dialogVisible).toBe(true)

      await wrapper.vm.closeDialog()
      expect(wrapper.vm.dialogVisible).toBe(false)
    })

    it('应能关闭应用策略弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openApplyDialog()
      expect(wrapper.vm.applyDialogVisible).toBe(true)

      await wrapper.vm.closeApplyDialog()
      expect(wrapper.vm.applyDialogVisible).toBe(false)
    })
  })
})
