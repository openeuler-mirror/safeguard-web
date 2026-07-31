import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '@/components/safeguard/StatusBadge.vue'

const createWrapper = (props = {}) => {
  return mount(StatusBadge, {
    props
  })
}

describe('StatusBadge.vue', () => {
  describe('渲染默认状态标签', () => {
    it('默认状态应渲染正确的文本和样式', () => {
      const wrapper = createWrapper()
      expect(wrapper.text()).toBe('default')
      expect(wrapper.classes()).toContain('status-badge')
      expect(wrapper.classes()).toContain('status-default')
    })
  })

  describe('渲染 success 状态', () => {
    it('success状态应显示"成功"文本和status-success样式', () => {
      const wrapper = createWrapper({ type: 'success' })
      expect(wrapper.text()).toBe('成功')
      expect(wrapper.classes()).toContain('status-success')
    })
  })

  describe('渲染 warning 状态', () => {
    it('warning状态应显示"警告"文本和status-warning样式', () => {
      const wrapper = createWrapper({ type: 'warning' })
      expect(wrapper.text()).toBe('警告')
      expect(wrapper.classes()).toContain('status-warning')
    })
  })

  describe('渲染 danger 状态', () => {
    it('danger状态应显示"失败"文本和status-danger样式', () => {
      const wrapper = createWrapper({ type: 'danger' })
      expect(wrapper.text()).toBe('失败')
      expect(wrapper.classes()).toContain('status-danger')
    })
  })

  describe('渲染 info 状态', () => {
    it('info状态应显示"信息"文本和status-info样式', () => {
      const wrapper = createWrapper({ type: 'info' })
      expect(wrapper.text()).toBe('信息')
      expect(wrapper.classes()).toContain('status-info')
    })
  })

})
