import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import FileMonitorEvents from '@/views/hosts/FileMonitorEvents.vue'
import { getFileMonitorEvents, collectFileMonitorEvents } from '@/api/safeguard/file-monitor'
import { getHost } from '@/api/host'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

vi.mock('@/api/safeguard/file-monitor')
vi.mock('@/api/host')

const mockPush = vi.fn()
const mockAlert = vi.fn()
window.alert = mockAlert

describe('FileMonitorEvents 页面测试', () => {
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockEvents = [
    { id: 1, path: '/etc/passwd', event_type: 'read', process_name: 'cat', user: 'root', timestamp: '2024-01-01T10:00:00Z' },
    { id: 2, path: '/etc/hosts', event_type: 'write', process_name: 'vi', user: 'admin', timestamp: '2024-01-01T11:00:00Z' }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockAlert.mockReset()

    getHost.mockResolvedValue(mockHost)
    getFileMonitorEvents.mockResolvedValue({ results: mockEvents })
    collectFileMonitorEvents.mockResolvedValue({ success: true })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(FileMonitorEvents, {
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

  describe('加载主机和事件列表', () => {
    it('应调用 getHost 和 getFileMonitorEvents API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHost).toHaveBeenCalledWith(1)
      expect(getFileMonitorEvents).toHaveBeenCalledWith({ host_id: 1 })
    })

    it('应正确设置 host 和 events 数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.host).toEqual(mockHost)
      expect(wrapper.vm.events).toEqual(mockEvents)
    })
  })

  describe('事件类型筛选', () => {
    it('改变 filterType 时应重新加载事件', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.setData({ filterType: 'read' })
      await wrapper.vm.loadEvents()

      expect(getFileMonitorEvents).toHaveBeenCalledWith({ host_id: 1, event_type: 'read' })
    })
  })

  describe('采集事件功能', () => {
    it('调用 collectEvents 时应触发采集并刷新列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.collectEvents()
      await flushPromises()

      expect(collectFileMonitorEvents).toHaveBeenCalledWith(1)
      expect(mockAlert).toHaveBeenCalledWith('事件采集任务已触发')
    })

    it('采集失败时应显示错误', async () => {
      collectFileMonitorEvents.mockRejectedValue(new Error('触发采集失败'))

      wrapper = createWrapper()
      await flushPromises()

      await wrapper.vm.collectEvents()
      await flushPromises()

      expect(mockAlert).toHaveBeenCalledWith('触发采集失败')
    })
  })

  describe('getEventTypeColor 方法测试', () => {
    it('应返回正确的颜色类型', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.getEventTypeColor('read')).toBe('info')
      expect(wrapper.vm.getEventTypeColor('write')).toBe('warning')
      expect(wrapper.vm.getEventTypeColor('create')).toBe('success')
      expect(wrapper.vm.getEventTypeColor('delete')).toBe('danger')
      expect(wrapper.vm.getEventTypeColor('modify')).toBe('info')
      expect(wrapper.vm.getEventTypeColor('unknown')).toBe('info')
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

    it('getFileMonitorEvents 失败时应显示错误', async () => {
      getFileMonitorEvents.mockRejectedValue(new Error('获取事件失败'))

      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.error).toBe('获取事件失败')
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
    it('没有事件时应显示空状态', async () => {
      getFileMonitorEvents.mockResolvedValue({ results: [] })

      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('暂无事件')
    })
  })

  describe('刷新按钮', () => {
    it('点击刷新应重新加载事件列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      vi.clearAllMocks()
      await wrapper.vm.loadEvents()

      expect(getFileMonitorEvents).toHaveBeenCalledWith({ host_id: 1 })
    })
  })
})
