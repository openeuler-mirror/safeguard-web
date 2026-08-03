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

})
