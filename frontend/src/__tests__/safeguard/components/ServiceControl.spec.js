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

})
