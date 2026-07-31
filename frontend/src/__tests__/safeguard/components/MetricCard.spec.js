import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MetricCard from '@/components/safeguard/MetricCard.vue'

const createWrapper = (props = {}) => {
  return mount(MetricCard, {
    props
  })
}

describe('MetricCard.vue', () => {
  describe('渲染标签和数值', () => {
    it('应正确渲染标签文本', () => {
      const wrapper = createWrapper({ label: 'CPU使用率', value: 50 })
      expect(wrapper.find('.metric-label').text()).toBe('CPU使用率')
    })

    it('应正确渲染数值', () => {
      const wrapper = createWrapper({ label: 'CPU使用率', value: 50 })
      expect(wrapper.find('.metric-value').text()).toContain('50')
    })
  })

  describe('显示单位', () => {
    it('应在数值后面显示单位', () => {
      const wrapper = createWrapper({ label: 'CPU使用率', value: 50, unit: '%' })
      expect(wrapper.find('.metric-value').text()).toContain('%')
    })
  })

})
