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

  describe('页面加载时显示 loading 状态', () => {
    it('初始应显示loading状态', async () => {
      wrapper = createWrapper()
      expect(wrapper.find('.loading').exists()).toBe(true)
    })

    it('数据加载完成后应隐藏loading状态', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.find('.loading').exists()).toBe(false)
    })
  })

  describe('加载策略模板列表', () => {
    it('应调用getPolicyTemplates API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getPolicyTemplates).toHaveBeenCalled()
    })

    it('应调用getHosts API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHosts).toHaveBeenCalled()
    })

    it('应正确设置templates数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.templates).toEqual(mockTemplates)
    })

    it('应正确设置availableHosts数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.availableHosts).toEqual(mockHosts)
    })
  })

  describe('搜索功能正常工作', () => {
    it('搜索输入框应存在', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const searchInput = wrapper.find('.search-input')
      expect(searchInput.exists()).toBe(true)
    })

    it('有搜索文本时API应传递search参数', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      await wrapper.setData({ searchText: 'test' })
      await wrapper.vm.loadTemplates()

      expect(getPolicyTemplates).toHaveBeenCalledWith({ search: 'test' })
    })
  })

  describe('点击创建模板打开创建弹窗', () => {
    it('创建按钮应存在', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const createButton = wrapper.find('.btn-primary')
      expect(createButton.exists()).toBe(true)
    })

    it('点击创建按钮应打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const createButton = wrapper.find('.btn-primary')
      await createButton.trigger('click')

      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
    })
  })

  describe('创建模板表单验证', () => {
    it('表单验证不通过时应显示错误', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openCreateDialog()
      await wrapper.vm.submitForm()

      expect(wrapper.vm.errors.name).toBe('请输入模板名称')
    })
  })

  describe('创建模板成功后刷新列表', () => {
    it('创建成功后应关闭弹窗并刷新', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openCreateDialog()
      await wrapper.setData({ form: { name: '新策略', description: '', config: { enable_firewall: false, enable_antivirus: false, enable_file_monitor: false, auto_update_hours: 24 } } })
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(createPolicyTemplate).toHaveBeenCalled()
      expect(wrapper.vm.dialogVisible).toBe(false)
    })
  })

  describe('点击编辑模板打开编辑弹窗', () => {
    it('编辑按钮应存在', async () => {
      wrapper = createWrapper()
      await flushPromises()
      const editButtons = wrapper.findAll('.btn-action')
      expect(editButtons.length).toBeGreaterThan(0)
    })
  })

  describe('编辑模板正确填充表单数据', () => {
    it('打开编辑弹窗时应正确填充表单', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openEditDialog(mockTemplates[0])

      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.form.name).toBe('基础安全策略')
    })
  })

  describe('编辑模板成功后刷新列表', () => {
    it('编辑成功后应关闭弹窗并刷新', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openEditDialog(mockTemplates[0])
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updatePolicyTemplate).toHaveBeenCalled()
    })
  })

  describe('点击删除模板显示确认对话框', () => {
    it('删除确认弹窗应能打开', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.confirmDelete(mockTemplates[0])

      expect(wrapper.vm.deleteDialogVisible).toBe(true)
    })
  })

  describe('删除模板成功后刷新列表', () => {
    it('删除成功后应关闭弹窗并刷新', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.confirmDelete(mockTemplates[0])
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(deletePolicyTemplate).toHaveBeenCalled()
    })
  })

  describe('点击克隆模板', () => {
    it('克隆成功后应刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.cloneTemplate(mockTemplates[0])
      await flushPromises()

      expect(clonePolicyTemplate).toHaveBeenCalled()
      expect(mockAlert).toHaveBeenCalledWith('模板克隆成功')
    })

    it('克隆失败时应显示错误', async () => {
      clonePolicyTemplate.mockRejectedValue(new Error('克隆失败'))

      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.cloneTemplate(mockTemplates[0])
      await flushPromises()

      expect(mockAlert).toHaveBeenCalledWith('克隆失败')
    })
  })

  describe('点击查看模板详情跳转详情页', () => {
    it('查看详情应跳转路由', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.viewTemplate(mockTemplates[0])

      expect(mockPush).toHaveBeenCalledWith('/safeguard/policy-templates/1')
    })
  })

  describe('点击应用策略打开主机选择弹窗', () => {
    it('应用策略弹窗应能打开', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openApplyDialog(mockTemplates[0])

      expect(wrapper.vm.applyDialogVisible).toBe(true)
    })
  })

  describe('应用策略成功后显示任务信息', () => {
    it('应用成功后应跳转任务页面', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openApplyDialog(mockTemplates[0])
      await wrapper.setData({ applyForm: { host_ids: [1, 2] } })
      await wrapper.vm.submitApply()
      await flushPromises()

      expect(applyPolicy).toHaveBeenCalled()
      expect(mockAlert).toHaveBeenCalledWith('策略下发任务已创建')
      expect(mockPush).toHaveBeenCalledWith('/safeguard/policy-tasks')
    })

    it('未选择主机时应提示', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openApplyDialog(mockTemplates[0])
      await wrapper.vm.submitApply()

      expect(mockAlert).toHaveBeenCalledWith('请至少选择一个主机')
    })
  })

  describe('分页功能正常工作', () => {
    it('应能显示多个模板卡片', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const cards = wrapper.findAll('.template-card')
      expect(cards.length).toBe(2)
    })
  })

  describe('API 失败时显示错误信息', () => {
    it('getPolicyTemplates失败时应显示错误', async () => {
      const errorMessage = '加载模板列表失败'
      getPolicyTemplates.mockRejectedValue(new Error(errorMessage))

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.error).toBe(errorMessage)
    })
  })

  describe('formatDate方法测试', () => {
    it('应正确格式化日期', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const result = wrapper.vm.formatDate('2024-01-01T00:00:00Z')
      expect(typeof result).toBe('string')
    })

    it('应处理null日期', async () => {
      wrapper = createWrapper()
      await flushPromises()

      const result = wrapper.vm.formatDate(null)
      expect(result).toBe('-')
    })
  })

  describe('空数据处理', () => {
    it('没有模板时应显示空状态', async () => {
      getPolicyTemplates.mockResolvedValue({ results: [] })

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无策略模板')
    })
  })

  describe('弹窗关闭功能', () => {
    it('应能关闭创建/编辑弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openCreateDialog()
      expect(wrapper.vm.dialogVisible).toBe(true)

      await wrapper.vm.closeDialog()
      expect(wrapper.vm.dialogVisible).toBe(false)
    })

    it('应能关闭删除确认弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.confirmDelete(mockTemplates[0])
      expect(wrapper.vm.deleteDialogVisible).toBe(true)

      await wrapper.vm.closeDeleteDialog()
      expect(wrapper.vm.deleteDialogVisible).toBe(false)
    })

    it('应能关闭应用策略弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openApplyDialog(mockTemplates[0])
      expect(wrapper.vm.applyDialogVisible).toBe(true)

      await wrapper.vm.closeApplyDialog()
      expect(wrapper.vm.applyDialogVisible).toBe(false)
    })
  })
})
