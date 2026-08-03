import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AuditDashboard from '@/views/audit/AuditDashboard.vue'
import { getAuditStats } from '@/api/safeguard/audit'
import MetricCard from '@/components/safeguard/MetricCard.vue'

vi.mock('@/api/safeguard/audit')

describe('AuditDashboard 页面测试', () => {
  const mockStats = {
    today_count: 150,
    week_count: 980,
    active_users: 25,
    anomaly_count: 3,
    action_distribution: {
      create: 50,
      update: 70,
      delete: 20,
      login: 100,
      logout: 80
    },
    user_ranking: [
      { username: 'admin', count: 120 },
      { username: 'user1', count: 80 },
      { username: 'user2', count: 50 }
    ]
  }

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    getAuditStats.mockResolvedValue(mockStats)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(AuditDashboard, {
      global: {
        stubs: {
          MetricCard
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

  describe('加载统计数据', () => {
    it('应调用 getAuditStats API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getAuditStats).toHaveBeenCalled()
    })

    it('应正确设置 stats 数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.stats).toEqual(mockStats)
    })
  })

  describe('getBarWidth 方法测试', () => {
    it('应返回正确的宽度百分比', async () => {
      wrapper = createWrapper()
      await flushPromises()

      // 最大值是 100 (login)
      expect(wrapper.vm.getBarWidth(50)).toBe(50)
      expect(wrapper.vm.getBarWidth(100)).toBe(100)
      expect(wrapper.vm.getBarWidth(70)).toBe(70)
    })

    it('无数据时应处理为 0', async () => {
      getAuditStats.mockResolvedValue({})
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.getBarWidth(50)).toBe(0)
    })
  })

  describe('getBarColor 方法测试', () => {
    it('应返回正确的颜色', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.vm.getBarColor('create')).toBe('#67c23a')
      expect(wrapper.vm.getBarColor('update')).toBe('#e6a23c')
      expect(wrapper.vm.getBarColor('delete')).toBe('#f56c6c')
      expect(wrapper.vm.getBarColor('login')).toBe('#409eff')
      expect(wrapper.vm.getBarColor('logout')).toBe('#909399')
      expect(wrapper.vm.getBarColor('unknown')).toBe('#909399')
    })
  })

})
