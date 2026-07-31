import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import ProcessList from '@/components/safeguard/ProcessList.vue'

// Mock window.alert
const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => { })

const createWrapper = (props = {}) => {
  return mount(ProcessList, {
    props,
    global: {
      stubs: {
        StatusBadge: { template: '<span class="status-badge"></span>' }
      }
    }
  })
}

const mockProcesses = [
  { pid: 1234, name: 'nginx', user: 'www-data', cpu_percent: 10, mem_percent: 5, status: 'running' },
  { pid: 5678, name: 'mysql', user: 'mysql', cpu_percent: 60, mem_percent: 40, status: 'running' },
  { pid: 1, name: 'init', user: 'root', cpu_percent: 0, mem_percent: 1, status: 'running' }
]

describe('ProcessList.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('渲染进程列表表格', () => {
    it('应渲染进程表格', () => {
      const wrapper = createWrapper({ processes: mockProcesses })
      expect(wrapper.find('.process-table').exists()).toBe(true)
    })

    it('应渲染正确数量的进程行', () => {
      const wrapper = createWrapper({ processes: mockProcesses })
      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(mockProcesses.length)
    })

    it('应显示进程PID、名称、用户、CPU、内存等信息', () => {
      const wrapper = createWrapper({ processes: mockProcesses })
      expect(wrapper.text()).toContain('1234')
      expect(wrapper.text()).toContain('nginx')
      expect(wrapper.text()).toContain('www-data')
      expect(wrapper.text()).toContain('10%')
      expect(wrapper.text()).toContain('5%')
    })
  })

  describe('高 CPU 占用进程高亮显示', () => {
    it('CPU超过50%的进程应添加high-resource类', () => {
      const wrapper = createWrapper({ processes: mockProcesses })
      const cpuCells = wrapper.findAll('td').filter(td => td.text().includes('60%'))
      expect(cpuCells[0].classes()).toContain('high-resource')
    })

    it('CPU不超过50%的进程不应添加high-resource类', () => {
      const wrapper = createWrapper({ processes: mockProcesses })
      const cpuCells = wrapper.findAll('td').filter(td => td.text().includes('10%'))
      expect(cpuCells[0].classes()).not.toContain('high-resource')
    })
  })

  describe('高内存占用进程高亮显示', () => {
    it('内存超过50%的进程应添加high-resource类', () => {
      const highMemProcesses = [{ ...mockProcesses[0], mem_percent: 60 }]
      const wrapper = createWrapper({ processes: highMemProcesses })
      const memCells = wrapper.findAll('td').filter(td => td.text().includes('60%'))
      expect(memCells[0].classes()).toContain('high-resource')
    })
  })

  describe('点击终止按钮', () => {
    it('点击终止按钮应显示确认对话框', async () => {
      const wrapper = createWrapper({ processes: mockProcesses })
      const killBtn = wrapper.findAll('.btn-kill')[0]
      await killBtn.trigger('click')
      expect(wrapper.find('.dialog-overlay').exists()).toBe(true)
      expect(wrapper.find('.dialog-header h3').text()).toBe('确认终止进程')
    })

    it('对话框应显示进程名称和PID', async () => {
      const wrapper = createWrapper({ processes: mockProcesses })
      const killBtn = wrapper.findAll('.btn-kill')[0]
      await killBtn.trigger('click')
      expect(wrapper.text()).toContain('nginx')
      expect(wrapper.text()).toContain('1234')
    })
  })

  describe('确认终止', () => {
    it('确认终止应调用onKill回调', async () => {
      const onKill = vi.fn().mockResolvedValue({})
      const wrapper = createWrapper({ processes: mockProcesses, onKill })

      const killBtn = wrapper.findAll('.btn-kill')[0]
      await killBtn.trigger('click')

      const confirmBtn = wrapper.find('.btn-danger')
      await confirmBtn.trigger('click')
      await flushPromises()

      expect(onKill).toHaveBeenCalledWith(1234, false)
    })

    it('勾选强制终止应传递force=true', async () => {
      const onKill = vi.fn().mockResolvedValue({})
      const wrapper = createWrapper({ processes: mockProcesses, onKill })

      const killBtn = wrapper.findAll('.btn-kill')[0]
      await killBtn.trigger('click')

      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)

      const confirmBtn = wrapper.find('.btn-danger')
      await confirmBtn.trigger('click')
      await flushPromises()

      expect(onKill).toHaveBeenCalledWith(1234, true)
    })
  })

  describe('取消终止', () => {
    it('取消终止不调用onKill回调', async () => {
      const onKill = vi.fn()
      const wrapper = createWrapper({ processes: mockProcesses, onKill })

      const killBtn = wrapper.findAll('.btn-kill')[0]
      await killBtn.trigger('click')

      const cancelBtn = wrapper.find('.btn-cancel')
      await cancelBtn.trigger('click')

      expect(onKill).not.toHaveBeenCalled()
    })
  })

})
