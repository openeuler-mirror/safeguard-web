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

  describe('显示图标和图标背景色', () => {
    it('应显示默认图标', () => {
      const wrapper = createWrapper({ label: 'CPU使用率', value: 50 })
      expect(wrapper.find('.metric-icon').exists()).toBe(true)
    })

    it('应使用自定义图标', () => {
      const wrapper = createWrapper({ label: 'CPU使用率', value: 50, icon: '📊' })
      expect(wrapper.find('.metric-icon').text()).toBe('📊')
    })

    it('应使用自定义图标背景色', () => {
      const wrapper = createWrapper({ label: 'CPU使用率', value: 50, iconBg: '#ff0000' })
      expect(wrapper.find('.metric-icon').attributes('style')).toContain('background: #ff0000')
    })
  })

  describe('显示正向趋势', () => {
    it('正趋势应显示↑和绿色样式', () => {
      const wrapper = createWrapper({ label: 'CPU使用率', value: 50, trend: 10 })
      expect(wrapper.find('.metric-trend').text()).toContain('↑')
      expect(wrapper.find('.metric-trend').text()).toContain('10%')
      expect(wrapper.find('.metric-trend').classes()).toContain('trend-up')
    })
  })

  describe('显示负向趋势', () => {
    it('负趋势应显示↓和红色样式', () => {
      const wrapper = createWrapper({ label: 'CPU使用率', value: 50, trend: -10 })
      expect(wrapper.find('.metric-trend').text()).toContain('↓')
      expect(wrapper.find('.metric-trend').text()).toContain('10%')
      expect(wrapper.find('.metric-trend').classes()).toContain('trend-down')
    })
  })
})
