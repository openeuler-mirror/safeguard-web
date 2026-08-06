import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Migrations from '@/views/osmigrate/Migrations.vue'
import {
  getMigrates,
  createMigrateInit,
  createMigrate,
  createMigrateBack,
  getMigrateStatus
} from '@/api/migrate'

vi.mock('@/api/migrate')

describe('Migrations 页面测试', () => {
  let wrapper

  const mockJobs = [
    { id: 1, job_id: 'job-1', job_type: 'init', migrate_type: 'centos_to_culinux', target_host: '192.168.1.1', status: 'success', progress: 100, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:01:00Z' },
    { id: 2, job_id: 'job-2', job_type: 'migrate', migrate_type: 'centos_to_culinux', target_host: '192.168.1.2', status: 'running', progress: 50, created_at: '2024-01-02T00:00:00Z', updated_at: '2024-01-02T00:01:00Z' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    getMigrates.mockResolvedValue({ results: mockJobs, count: 2 })
    vi.spyOn(window, 'alert').mockImplementation(() => { })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(Migrations, {
      global: {
        stubs: {}
      }
    })
  }

  describe('页面初始加载', () => {
    it('应该调用 getMigrates', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(getMigrates).toHaveBeenCalled()
    })

    it('应该显示迁移任务列表', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('job-1')
      expect(wrapper.text()).toContain('job-2')
      expect(wrapper.text()).toContain('192.168.1.1')
    })

    it('应该显示状态标签', async () => {
      wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.status-success').exists()).toBe(true)
      expect(wrapper.find('.status-running').exists()).toBe(true)
    })

    it('应该显示加载状态', async () => {
      getMigrates.mockImplementation(() => new Promise(() => { }))
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('加载中...')
    })
  })

})
