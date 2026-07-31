import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import ServiceControl from '@/components/safeguard/ServiceControl.vue'

// Mock window.alert
const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => { })

const createWrapper = (props = {}) => {
  return mount(ServiceControl, {
    props,
    global: {
      stubs: {
        StatusBadge: { template: '<span class="status-badge"></span>' }
      }
    }
  })
}

const mockServices = [
  { name: 'nginx', active: true, enabled: true },
  { name: 'mysql', active: false, enabled: true },
  { name: 'redis', active: true, enabled: false }
]

describe('ServiceControl.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('渲染服务列表', () => {
    it('应渲染服务表格', () => {
      const wrapper = createWrapper({ services: mockServices })
      expect(wrapper.find('.service-table').exists()).toBe(true)
    })

    it('应渲染正确数量的服务行', () => {
      const wrapper = createWrapper({ services: mockServices })
      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(mockServices.length)
    })

    it('应显示服务名称', () => {
      const wrapper = createWrapper({ services: mockServices })
      expect(wrapper.text()).toContain('nginx')
      expect(wrapper.text()).toContain('mysql')
      expect(wrapper.text()).toContain('redis')
    })
  })

  describe('显示服务状态', () => {
    it('应显示StatusBadge组件', () => {
      const wrapper = createWrapper({ services: mockServices })
      expect(wrapper.find('.status-badge').exists()).toBe(true)
    })
  })

  describe('点击启动按钮', () => {
    it('点击启动按钮应显示确认弹窗', async () => {
      const wrapper = createWrapper({ services: mockServices })
      const startBtn = wrapper.findAll('.btn-start')[0]
      await startBtn.trigger('click')
      expect(wrapper.find('.dialog-overlay').exists()).toBe(true)
      expect(wrapper.find('.dialog-header h3').text()).toBe('启动')
    })

    it('确认启动应调用onControl回调', async () => {
      const onControl = vi.fn().mockResolvedValue({})
      const wrapper = createWrapper({ services: mockServices, onControl })

      const startBtn = wrapper.findAll('.btn-start')[0]
      await startBtn.trigger('click')

      const confirmBtn = wrapper.find('.btn-primary')
      await confirmBtn.trigger('click')
      await flushPromises()

      expect(onControl).toHaveBeenCalledWith('mysql', 'start')
    })
  })

  describe('点击停止按钮', () => {
    it('点击停止按钮应显示确认弹窗', async () => {
      const wrapper = createWrapper({ services: mockServices })
      const stopBtn = wrapper.findAll('.btn-stop')[0]
      await stopBtn.trigger('click')
      expect(wrapper.find('.dialog-overlay').exists()).toBe(true)
      expect(wrapper.find('.dialog-header h3').text()).toBe('停止')
    })

    it('确认停止应调用onControl回调', async () => {
      const onControl = vi.fn().mockResolvedValue({})
      const wrapper = createWrapper({ services: mockServices, onControl })

      const stopBtn = wrapper.findAll('.btn-stop')[0]
      await stopBtn.trigger('click')

      const confirmBtn = wrapper.find('.btn-primary')
      await confirmBtn.trigger('click')
      await flushPromises()

      expect(onControl).toHaveBeenCalledWith('nginx', 'stop')
    })
  })

  describe('点击重启按钮', () => {
    it('点击重启按钮应显示确认弹窗', async () => {
      const wrapper = createWrapper({ services: mockServices })
      const restartBtn = wrapper.findAll('.btn-restart')[0]
      await restartBtn.trigger('click')
      expect(wrapper.find('.dialog-overlay').exists()).toBe(true)
      expect(wrapper.find('.dialog-header h3').text()).toBe('重启')
    })

    it('确认重启应调用onControl回调', async () => {
      const onControl = vi.fn().mockResolvedValue({})
      const wrapper = createWrapper({ services: mockServices, onControl })

      const restartBtn = wrapper.findAll('.btn-restart')[0]
      await restartBtn.trigger('click')

      const confirmBtn = wrapper.find('.btn-primary')
      await confirmBtn.trigger('click')
      await flushPromises()

      expect(onControl).toHaveBeenCalledWith('nginx', 'restart')
    })
  })

  describe('点击查看日志按钮', () => {
    it('点击日志按钮应显示日志弹窗', async () => {
      const wrapper = createWrapper({ services: mockServices })
      const logsBtn = wrapper.findAll('.btn-logs')[0]
      await logsBtn.trigger('click')
      expect(wrapper.find('.dialog-overlay').exists()).toBe(true)
      expect(wrapper.find('.dialog-header h3').text()).toContain('服务日志')
    })

    it('应调用onGetLogs回调获取日志', async () => {
      const onGetLogs = vi.fn().mockResolvedValue('log content')
      const wrapper = createWrapper({ services: mockServices, onGetLogs })

      const logsBtn = wrapper.findAll('.btn-logs')[0]
      await logsBtn.trigger('click')
      await flushPromises()

      expect(onGetLogs).toHaveBeenCalledWith('nginx')
    })
  })

  describe('操作进行中显示 loading 状态', () => {
    it('操作进行中确认按钮应显示loading文本并禁用', async () => {
      const onControl = vi.fn().mockImplementation(() => new Promise(() => { }))
      const wrapper = createWrapper({ services: mockServices, onControl })

      const stopBtn = wrapper.findAll('.btn-stop')[0]
      await stopBtn.trigger('click')

      const confirmBtn = wrapper.find('.btn-primary')
      await confirmBtn.trigger('click')
      await wrapper.vm.$nextTick()

      expect(confirmBtn.text()).toBe('操作中...')
      expect(confirmBtn.attributes('disabled')).toBe('')
    })
  })

  describe('显示操作成功/失败提示', () => {
    it('操作失败应显示alert提示', async () => {
      const onControl = vi.fn().mockRejectedValue(new Error('操作失败'))
      const wrapper = createWrapper({ services: mockServices, onControl })

      const stopBtn = wrapper.findAll('.btn-stop')[0]
      await stopBtn.trigger('click')

      const confirmBtn = wrapper.find('.btn-primary')
      await confirmBtn.trigger('click')
      await flushPromises()

      expect(alertMock).toHaveBeenCalledWith('操作失败')
    })
  })

  describe('loading状态', () => {
    it('应显示loading文本', () => {
      const wrapper = createWrapper({ loading: true })
      expect(wrapper.find('.loading').text()).toBe('加载中...')
    })
  })

  describe('error状态', () => {
    it('应显示错误信息', () => {
      const wrapper = createWrapper({ error: '加载失败' })
      expect(wrapper.find('.error').text()).toBe('加载失败')
    })
  })

  describe('空服务列表', () => {
    it('应显示空提示', () => {
      const wrapper = createWrapper({ services: [] })
      expect(wrapper.find('.empty-text').text()).toBe('暂无服务信息')
    })
  })
})
