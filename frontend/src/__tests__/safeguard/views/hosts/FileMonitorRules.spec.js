import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import FileMonitorRules from '@/views/hosts/FileMonitorRules.vue'
import {
  getFileMonitorRules,
  createFileMonitorRule,
  updateFileMonitorRule,
  deleteFileMonitorRule
} from '@/api/safeguard/file-monitor'
import { getHost } from '@/api/host'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

vi.mock('@/api/safeguard/file-monitor')
vi.mock('@/api/host')

const mockPush = vi.fn()
const mockAlert = vi.fn()
window.alert = mockAlert

describe('FileMonitorRules 页面测试', () => {
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockRules = [
    { id: 1, path: '/etc/passwd', monitor_types: ['read', 'write'], enabled: true, created_at: '2024-01-01T00:00:00Z' },
    { id: 2, path: '/etc/hosts', monitor_types: ['create', 'delete'], enabled: false, created_at: '2024-01-02T00:00:00Z' }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockAlert.mockReset()

    getHost.mockResolvedValue(mockHost)
    getFileMonitorRules.mockResolvedValue({ results: mockRules })
    createFileMonitorRule.mockResolvedValue({ success: true })
    updateFileMonitorRule.mockResolvedValue({ success: true })
    deleteFileMonitorRule.mockResolvedValue({ success: true })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(FileMonitorRules, {
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

  describe('加载主机和规则列表', () => {
    it('应调用 getHost 和 getFileMonitorRules API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHost).toHaveBeenCalledWith(1)
      expect(getFileMonitorRules).toHaveBeenCalledWith({ host_id: 1 })
    })

    it('应正确设置 host 和 rules 数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.host).toEqual(mockHost)
      expect(wrapper.vm.rules).toEqual(mockRules)
    })
  })

  describe('创建规则弹窗', () => {
    it('点击创建按钮应打开弹窗', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openCreateDialog()
      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
    })

    it('表单验证 - 路径为空时应显示错误', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openCreateDialog()
      await wrapper.vm.submitForm()
      expect(wrapper.vm.errors.path).toBe('请输入监控路径')
    })

    it('表单验证 - 未选择监控类型时应 alert', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openCreateDialog()
      await wrapper.setData({ form: { ...wrapper.vm.form, path: '/test/path', monitor_types: [] } })
      await wrapper.vm.submitForm()
      expect(mockAlert).toHaveBeenCalledWith('请至少选择一种监控类型')
    })

    it('创建成功后应关闭弹窗并刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openCreateDialog()
      await wrapper.setData({ form: { ...wrapper.vm.form, path: '/test/path', monitor_types: ['read'] } })
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(createFileMonitorRule).toHaveBeenCalled()
      expect(wrapper.vm.dialogVisible).toBe(false)
    })
  })

  describe('编辑规则弹窗', () => {
    it('点击编辑按钮应打开弹窗并填充数据', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openEditDialog(mockRules[0])
      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(true)
      expect(wrapper.vm.form.path).toBe('/etc/passwd')
    })

    it('编辑成功后应关闭弹窗并刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.openEditDialog(mockRules[0])
      await wrapper.vm.submitForm()
      await flushPromises()

      expect(updateFileMonitorRule).toHaveBeenCalled()
    })
  })

  describe('启用/禁用规则', () => {
    it('调用 toggleEnabled 时应更新规则', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.toggleEnabled(mockRules[0])
      expect(updateFileMonitorRule).toHaveBeenCalledWith(1, expect.any(Object))
    })
  })

  describe('删除规则', () => {
    it('确认弹窗应正确显示', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.confirmDelete(mockRules[0])
      expect(wrapper.vm.deleteDialogVisible).toBe(true)
      expect(wrapper.vm.selectedRule).toEqual(mockRules[0])
    })

    it('删除成功后应关闭弹窗并刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.confirmDelete(mockRules[0])
      await wrapper.vm.handleDelete()
      await flushPromises()

      expect(deleteFileMonitorRule).toHaveBeenCalledWith(1)
    })
  })

  describe('API 失败时显示错误信息', () => {
    it('getHost 失败时应显示错误', async () => {
      getHost.mockRejectedValue(new Error('加载数据失败'))

      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.error).toBe('加载数据失败')
    })

    it('getFileMonitorRules 失败时应显示错误', async () => {
      getFileMonitorRules.mockRejectedValue(new Error('获取规则失败'))

      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.error).toBe('获取规则失败')
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

  describe('返回按钮', () => {
    it('点击返回应跳转到主机仪表盘', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.goBack()
      expect(mockPush).toHaveBeenCalledWith('/hosts/1/dashboard')
    })
  })

  describe('空数据处理', () => {
    it('没有规则时应显示空状态', async () => {
      getFileMonitorRules.mockResolvedValue({ results: [] })

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无规则')
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

      await wrapper.vm.confirmDelete(mockRules[0])
      expect(wrapper.vm.deleteDialogVisible).toBe(true)

      await wrapper.vm.closeDeleteDialog()
      expect(wrapper.vm.deleteDialogVisible).toBe(false)
    })
  })
})
