<template>
  <div class="simple-line-chart">
    <svg ref="chartSvg" :width="width" :height="height">
      <!-- Y轴 -->
      <line :x1="padding.left" :y1="padding.top" :x2="padding.left" :y2="height - padding.bottom" stroke="#ddd" />
      <!-- X轴 -->
      <line :x1="padding.left" :y1="height - padding.bottom" :x2="width - padding.right" :y2="height - padding.bottom" stroke="#ddd" />

      <!-- Y轴刻度 -->
      <g v-for="(tick, i) in yTicks" :key="i">
        <line
          :x1="padding.left - 5"
          :y1="tick.y"
          :x2="padding.left"
          :y2="tick.y"
          stroke="#ddd"
        />
        <text
          :x="padding.left - 10"
          :y="tick.y + 4"
          text-anchor="end"
          fill="#909399"
          font-size="12"
        >{{ tick.value }}</text>
      </g>

      <!-- 网格线 -->
      <g class="grid-lines">
        <line
          v-for="(tick, i) in yTicks"
          :key="`grid-${i}`"
          :x1="padding.left"
          :y1="tick.y"
          :x2="width - padding.right"
          :y2="tick.y"
          stroke="#f5f5f5"
        />
      </g>

      <!-- 数据线 -->
      <g v-for="(series, sIndex) in seriesData" :key="sIndex">
        <path
          :d="series.path"
          fill="none"
          :stroke="series.color"
          stroke-width="2"
        />
        <!-- 数据点 -->
        <g v-for="(point, pIndex) in series.points" :key="pIndex">
          <circle
            :cx="point.x"
            :cy="point.y"
            r="4"
            :fill="series.color"
          />
        </g>
      </g>
    </svg>
  </div>
</template>

<script>
export default {
  name: 'SimpleLineChart',
  props: {
    data: {
      type: [Array, Object],
      default: () => []
    },
    maxValue: {
      type: Number,
      default: 100
    },
    color: {
      type: String,
      default: '#409eff'
    },
    unit: {
      type: String,
      default: ''
    },
    width: {
      type: Number,
      default: 500
    },
    height: {
      type: Number,
      default: 250
    }
  },
  data() {
    return {
      padding: { top: 20, right: 20, bottom: 30, left: 50 }
    }
  },
  computed: {
    seriesData() {
      // 支持单数据系列和多数据系列
      let series = []
      if (Array.isArray(this.data) && this.data.length > 0) {
        if (this.data[0].label && this.data[0].data) {
          // 多数据系列
          series = this.data.map(s => ({
            label: s.label,
            color: s.color || this.color,
            data: s.data
          }))
        } else {
          // 单数据系列
          series = [{
            label: '',
            color: this.color,
            data: this.data
          }]
        }
      }

      // 计算路径和点坐标
      const chartWidth = this.width - this.padding.left - this.padding.right
      const chartHeight = this.height - this.padding.top - this.padding.bottom

      return series.map(s => {
        if (s.data.length === 0) return { ...s, path: '', points: [] }

        const points = s.data.map((d, i) => {
          const x = this.padding.left + (i / Math.max(s.data.length - 1, 1)) * chartWidth
          const y = this.height - this.padding.bottom - (d.y / this.maxValue) * chartHeight
          return { x, y, value: d.y }
        })

        let path = ''
        if (points.length > 0) {
          path = `M ${points[0].x} ${points[0].y}`
          for (let i = 1; i < points.length; i++) {
            path += ` L ${points[i].x} ${points[i].y}`
          }
        }

        return { ...s, path, points }
      })
    },
    yTicks() {
      const ticks = []
      const chartHeight = this.height - this.padding.top - this.padding.bottom
      const tickCount = 5

      for (let i = 0; i <= tickCount; i++) {
        const value = Math.round((i / tickCount) * this.maxValue * 10) / 10
        const y = this.height - this.padding.bottom - (i / tickCount) * chartHeight
        ticks.push({ value: value + (i === tickCount ? this.unit : ''), y })
      }

      return ticks
    }
  }
}
</script>

<style scoped>
.simple-line-chart {
  width: 100%;
  overflow-x: auto;
}
</style>