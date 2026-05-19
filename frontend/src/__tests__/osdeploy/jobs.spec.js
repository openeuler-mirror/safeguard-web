import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Jobs from '@/views/osdeploy/Jobs.vue'

// Mock API
vi.mock('@/api/osdeploy/job', () => ({
  getJobs: vi.fn(),
  getJobDetail: vi.fn(),
  queryJobStatus: vi.fn()
}))

import { getJobs, getJobDetail, queryJobStatus } from '@/api/osdeploy/job'

const createWrapper = () => {
  return mount(Jobs, {
    global: {
      stubs: {
        'router-link': true,
        router: { push: vi.fn() }
      }
    }
  })
}

describe('Jobs.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('UI 渲染', () => {
    it('渲染标题', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('h2').text()).toBe('任务管理')
    })

    it('渲染刷新按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.btn-refresh').text()).toBe('刷新')
    })

    it('渲染状态筛选下拉框', () => {
      const wrapper = createWrapper()
      expect(wrapper.findAll('.filter-select').length).toBe(2)
    })

    it('渲染搜索输入框', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.search-input').exists()).toBe(true)
    })
  })

  describe('数据加载', () => {
    it('初始加载时显示 loading', async () => {
      getJobs.mockImplementation(() => new Promise(() => {}))
      const wrapper = createWrapper()
      // 验证 loading 状态为 true
      expect(wrapper.vm.loading).toBe(true)
    })

    it('加载失败时显示错误信息', async () => {
      getJobs.mockRejectedValue(new Error('加载失败'))
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.error).toBe('加载失败')
      expect(wrapper.find('.error').exists()).toBe(true)
    })

    it('无数据时显示暂无数据', async () => {
      getJobs.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.empty-text').exists()).toBe(true)
    })
  })

  describe('表格渲染', () => {
    it('正确显示任务数据', async () => {
      const mockJobs = [{
        id: 1,
        job_id: 'job-001',
        job_type: 'osdeploy',
        target: '192.168.1.100',
        status: 'running',
        progress: 50,
        created_at: '2026-01-01T00:00:00Z'
      }]

      getJobs.mockResolvedValue({ results: mockJobs, count: 1 })
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await wrapper.vm.loadJobs()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.jobs.length).toBe(1)
      expect(wrapper.vm.jobs[0].job_id).toBe('job-001')
    })

    it('任务类型正确映射', async () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatJobType('osdeploy')).toBe('OS部署')
      expect(wrapper.vm.formatJobType('hardware')).toBe('硬件采集')
    })
  })

  describe('状态显示', () => {
    it('formatStatus 返回正确的中文状态', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatStatus('pending')).toBe('等待中')
      expect(wrapper.vm.formatStatus('running')).toBe('运行中')
      expect(wrapper.vm.formatStatus('success')).toBe('成功')
      expect(wrapper.vm.formatStatus('failed')).toBe('失败')
    })

    it('getStatusClass 返回正确的样式类', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.getStatusClass('pending')).toBe('status-pending')
      expect(wrapper.vm.getStatusClass('running')).toBe('status-running')
      expect(wrapper.vm.getStatusClass('success')).toBe('status-success')
      expect(wrapper.vm.getStatusClass('failed')).toBe('status-failed')
    })
  })

  describe('详情弹窗', () => {
    it('点击详情按钮打开弹窗', async () => {
      const mockJob = {
        id: 1,
        job_id: 'job-001',
        job_type: 'osdeploy',
        target: 'target',
        status: 'success',
        progress: 100,
        created_at: '2026-01-01T00:00:00Z'
      }

      getJobDetail.mockResolvedValue(mockJob)
      const wrapper = createWrapper()

      await wrapper.vm.openDetailDialog(mockJob)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.detailDialogVisible).toBe(true)
      expect(getJobDetail).toHaveBeenCalledWith(1)
    })

    it('关闭弹窗清空数据', async () => {
      const wrapper = createWrapper()
      wrapper.vm.detailDialogVisible = true
      wrapper.vm.selectedJob = { id: 1, job_id: 'job-001' }

      await wrapper.vm.closeDetailDialog()

      expect(wrapper.vm.detailDialogVisible).toBe(false)
      expect(wrapper.vm.selectedJob).toBe(null)
    })
  })

  describe('操作按钮', () => {
    it('详情按钮可点击', async () => {
      const mockJobs = [{
        id: 1,
        job_id: 'job-001',
        job_type: 'osdeploy',
        target: 'target',
        status: 'success',
        progress: 100,
        created_at: '2026-01-01T00:00:00Z'
      }]

      getJobs.mockResolvedValue({ results: mockJobs, count: 1 })
      getJobDetail.mockResolvedValue(mockJobs[0])
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.btn-detail').exists()).toBe(true)
    })
  })

  describe('工具方法', () => {
    it('formatDate 正确格式化日期', () => {
      const wrapper = createWrapper()
      const result = wrapper.vm.formatDate('2026-01-15T10:30:00Z')
      expect(result).toContain('2026')
    })

    it('formatDate 处理空值', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm.formatDate('')).toBe('-')
      expect(wrapper.vm.formatDate(null)).toBe('-')
    })
  })

  describe('分页', () => {
    it('正确计算总页数', () => {
      const wrapper = createWrapper()
      wrapper.vm.totalCount = 45
      wrapper.vm.pageSize = 20
      expect(wrapper.vm.totalPages).toBe(3)
    })

    it('处理最后一页不满的情况', () => {
      const wrapper = createWrapper()
      wrapper.vm.totalCount = 21
      wrapper.vm.pageSize = 20
      expect(wrapper.vm.totalPages).toBe(2)
    })

    it('总页数为0时返回1', () => {
      const wrapper = createWrapper()
      wrapper.vm.totalCount = 0
      wrapper.vm.pageSize = 20
      expect(wrapper.vm.totalPages).toBe(1)
    })
  })

  describe('筛选和搜索', () => {
    it('handleFilter 重置页码', async () => {
      getJobs.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      wrapper.vm.page = 5

      await wrapper.vm.handleFilter()

      expect(wrapper.vm.page).toBe(1)
    })

    it('handleSearch 重置页码', async () => {
      getJobs.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()
      wrapper.vm.page = 5

      await wrapper.vm.handleSearch()

      expect(wrapper.vm.page).toBe(1)
    })

    it('handlePageChange 更改页码', async () => {
      getJobs.mockResolvedValue({ results: [], count: 0 })
      const wrapper = createWrapper()

      await wrapper.vm.handlePageChange(3)

      expect(wrapper.vm.page).toBe(3)
    })
  })
})