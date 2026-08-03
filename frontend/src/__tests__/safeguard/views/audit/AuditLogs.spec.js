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

  describe('筛选功能', () => {
    it('改变 filterAction 时应重新加载日志', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.setData({ filterAction: 'create' })
      await wrapper.vm.loadLogs()

      expect(getAuditLogs).toHaveBeenCalledWith({ action: 'create' })
    })

    it('改变 filterResource 时应重新加载日志', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.setData({ filterResource: 'policy' })
      await wrapper.vm.loadLogs()

      expect(getAuditLogs).toHaveBeenCalledWith({ resource_type: 'policy' })
    })

    it('同时设置两个筛选条件时都应传递', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.setData({ filterAction: 'create', filterResource: 'policy' })
      await wrapper.vm.loadLogs()

      expect(getAuditLogs).toHaveBeenCalledWith({ action: 'create', resource_type: 'policy' })
    })

    it('筛选条件为空时不传该参数', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.setData({ filterAction: '', filterResource: '' })
      await wrapper.vm.loadLogs()

      expect(getAuditLogs).toHaveBeenCalledWith({})
    })
  })

  describe('getActionColor 方法测试', () => {
    it('应返回正确的颜色类型', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.getActionColor('create')).toBe('success')
      expect(wrapper.vm.getActionColor('update')).toBe('warning')
      expect(wrapper.vm.getActionColor('delete')).toBe('danger')
      expect(wrapper.vm.getActionColor('login')).toBe('info')
      expect(wrapper.vm.getActionColor('logout')).toBe('info')
      expect(wrapper.vm.getActionColor('unknown')).toBe('info')
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

})
