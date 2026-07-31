import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SimpleLineChart from '@/components/safeguard/SimpleLineChart.vue'

const createWrapper = (props = {}) => {
  return mount(SimpleLineChart, {
    props
  })
}

const mockSingleData = [
  { y: 10 },
  { y: 20 },
  { y: 15 },
  { y: 30 },
  { y: 25 }
]

const mockMultiData = [
  { label: 'CPU', color: '#ff0000', data: [{ y: 10 }, { y: 20 }, { y: 15 }] },
  { label: 'Memory', color: '#00ff00', data: [{ y: 30 }, { y: 25 }, { y: 35 }] }
]

describe('SimpleLineChart.vue', () => {
  describe('渲染折线图 Canvas/SVG', () => {
    it('应渲染SVG元素', () => {
      const wrapper = createWrapper({ data: mockSingleData })
      expect(wrapper.find('svg').exists()).toBe(true)
    })

    it('应使用自定义宽度和高度', () => {
      const wrapper = createWrapper({ data: mockSingleData, width: 600, height: 300 })
      expect(wrapper.find('svg').attributes('width')).toBe('600')
      expect(wrapper.find('svg').attributes('height')).toBe('300')
    })
  })

  describe('正确绘制数据点', () => {
    it('应渲染正确数量的数据点', () => {
      const wrapper = createWrapper({ data: mockSingleData })
      const circles = wrapper.findAll('circle')
      expect(circles.length).toBe(mockSingleData.length)
    })
  })

  describe('正确绘制连线', () => {
    it('应渲染path元素表示连线', () => {
      const wrapper = createWrapper({ data: mockSingleData })
      expect(wrapper.find('path').exists()).toBe(true)
    })
  })

  describe('显示X轴和Y轴', () => {
    it('应渲染X轴线', () => {
      const wrapper = createWrapper({ data: mockSingleData })
      const lines = wrapper.findAll('line')
      const hasXAxis = lines.some(line => {
        const y2 = line.attributes('y2')
        const y1 = line.attributes('y1')
        return y1 === y2
      })
      expect(hasXAxis).toBe(true)
    })

    it('应渲染Y轴线', () => {
      const wrapper = createWrapper({ data: mockSingleData })
      const lines = wrapper.findAll('line')
      const hasYAxis = lines.some(line => {
        const x2 = line.attributes('x2')
        const x1 = line.attributes('x1')
        return x1 === x2
      })
      expect(hasYAxis).toBe(true)
    })

    it('应显示Y轴刻度标签', () => {
      const wrapper = createWrapper({ data: mockSingleData })
      expect(wrapper.find('text').exists()).toBe(true)
    })
  })

  describe('处理空数据情况', () => {
    it('空数组不应出错', () => {
      expect(() => {
        createWrapper({ data: [] })
      }).not.toThrow()
    })

    it('未提供data不应出错', () => {
      expect(() => {
        createWrapper()
      }).not.toThrow()
    })
  })

  describe('处理单数据点情况', () => {
    it('单个数据点应正常渲染', () => {
      const wrapper = createWrapper({ data: [{ y: 50 }] })
      expect(wrapper.find('svg').exists()).toBe(true)
    })
  })

})
