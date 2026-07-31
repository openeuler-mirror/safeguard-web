import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PortList from '@/components/safeguard/PortList.vue'

const createWrapper = (props = {}) => {
  return mount(PortList, {
    props,
    global: {
      stubs: {
        StatusBadge: { template: '<span class="status-badge"></span>' }
      }
    }
  })
}

const mockPorts = [
  { port: 22, protocol: 'tcp', state: 'LISTEN', process_name: 'sshd', pid: 1234 },
  { port: 80, protocol: 'tcp', state: 'LISTEN', process_name: 'nginx', pid: 5678 },
  { port: 3306, protocol: 'tcp', state: 'LISTEN', process_name: 'mysql', pid: 9012 }
]

describe('PortList.vue', () => {
  describe('渲染端口列表', () => {
    it('应渲染端口表格', () => {
      const wrapper = createWrapper({ ports: mockPorts })
      expect(wrapper.find('.port-table').exists()).toBe(true)
    })

    it('应渲染正确数量的端口行', () => {
      const wrapper = createWrapper({ ports: mockPorts })
      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(mockPorts.length)
    })
  })

  describe('显示端口号、协议、进程名、状态', () => {
    it('应显示端口号', () => {
      const wrapper = createWrapper({ ports: mockPorts })
      expect(wrapper.text()).toContain('22')
      expect(wrapper.text()).toContain('80')
      expect(wrapper.text()).toContain('3306')
    })

    it('应显示协议类型', () => {
      const wrapper = createWrapper({ ports: mockPorts })
      expect(wrapper.text()).toContain('tcp')
    })

    it('应显示StatusBadge组件', () => {
      const wrapper = createWrapper({ ports: mockPorts })
      expect(wrapper.find('.status-badge').exists()).toBe(true)
    })

    it('应显示进程名称', () => {
      const wrapper = createWrapper({ ports: mockPorts })
      expect(wrapper.text()).toContain('sshd')
      expect(wrapper.text()).toContain('nginx')
      expect(wrapper.text()).toContain('mysql')
    })

    it('应显示PID', () => {
      const wrapper = createWrapper({ ports: mockPorts })
      expect(wrapper.text()).toContain('1234')
      expect(wrapper.text()).toContain('5678')
      expect(wrapper.text()).toContain('9012')
    })
  })

  describe('处理缺失的进程名', () => {
    it('进程名为空时应显示-', () => {
      const ports = [{ port: 1234, protocol: 'tcp', state: 'LISTEN', process_name: null, pid: null }]
      const wrapper = createWrapper({ ports })
      expect(wrapper.text()).toContain('-')
    })
  })

})
