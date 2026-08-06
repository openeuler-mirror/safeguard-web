import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AutoInstall from '@/views/osdeploy/AutoInstall.vue'

// Mock API
vi.mock('@/api/host', () => ({
  getHosts: vi.fn()
}))

vi.mock('@/api/osdeploy/pxe', () => ({
  getPXEServers: vi.fn()
}))

vi.mock('@/api/osdeploy/kickstart', () => ({
  getKickstarts: vi.fn()
}))

vi.mock('@/api/osdeploy/repo', () => ({
  getRepos: vi.fn()
}))

vi.mock('@/api/osdeploy/job', () => ({
  getJobs: vi.fn()
}))

import { getHosts } from '@/api/host'
import { getPXEServers } from '@/api/osdeploy/pxe'
import { getKickstarts } from '@/api/osdeploy/kickstart'
import { getRepos } from '@/api/osdeploy/repo'
import { getJobs } from '@/api/osdeploy/job'

const createWrapper = () => {
  return mount(AutoInstall, {
    global: {
      stubs: {
        'router-link': true,
        router: { push: vi.fn() }
      }
    }
  })
}

describe('AutoInstall.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getHosts.mockResolvedValue({ results: [] })
    getPXEServers.mockResolvedValue({ results: [] })
    getKickstarts.mockResolvedValue({ results: [] })
    getRepos.mockResolvedValue({ results: [] })
    getJobs.mockResolvedValue({ results: [], count: 0 })
  })

  describe('UI 渲染', () => {

    it('渲染装机配置表单卡片', () => {
      const wrapper = createWrapper()
      expect(wrapper.findAll('.form-card').length).toBe(1)
    })

    it('渲染目标主机下拉框', () => {
      const wrapper = createWrapper()
      expect(wrapper.findAll('select').length).toBe(4)
    })

    it('渲染开始装机按钮', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.btn-primary').text()).toBe('开始装机')
    })
  })

  describe('数据加载', () => {
    it('挂载时加载主机列表', async () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(getHosts).toHaveBeenCalled()
    })

    it('挂载时加载PXE服务器列表', async () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(getPXEServers).toHaveBeenCalled()
    })

    it('挂载时加载Kickstart模板列表', async () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(getKickstarts).toHaveBeenCalled()
    })

    it('挂载时加载仓库列表', async () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(getRepos).toHaveBeenCalled()
    })

    it('挂载时加载近期任务', async () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(getJobs).toHaveBeenCalled()
    })
  })

  describe('下拉框数据', () => {
    it('正确显示主机选项', async () => {
      const mockHosts = [
        { id: 1, hostname: 'host1', ip_address: '192.168.1.10' },
        { id: 2, hostname: 'host2', ip_address: '192.168.1.11' }
      ]

      getHosts.mockResolvedValue({ results: mockHosts })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const options = wrapper.findAll('select:first-of-type option')
      expect(options.length).toBeGreaterThanOrEqual(2)
    })
  })

  describe('表单验证', () => {
    it('目标主机必填验证', async () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      wrapper.vm.form.host_id = ''
      wrapper.vm.form.pxe_server_id = '1'
      wrapper.vm.form.kickstart_id = '1'
      wrapper.vm.form.repo_id = '1'

      await wrapper.vm.handleSubmit()

      expect(wrapper.vm.errors.host_id).toBe('请选择目标主机')
    })

    it('PXE服务器必填验证', async () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      wrapper.vm.form.host_id = '1'
      wrapper.vm.form.pxe_server_id = ''
      wrapper.vm.form.kickstart_id = '1'
      wrapper.vm.form.repo_id = '1'

      await wrapper.vm.handleSubmit()

      expect(wrapper.vm.errors.pxe_server_id).toBe('请选择PXE服务器')
    })

    it('Kickstart模板必填验证', async () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      wrapper.vm.form.host_id = '1'
      wrapper.vm.form.pxe_server_id = '1'
      wrapper.vm.form.kickstart_id = ''
      wrapper.vm.form.repo_id = '1'

      await wrapper.vm.handleSubmit()

      expect(wrapper.vm.errors.kickstart_id).toBe('请选择Kickstart模板')
    })

    it('仓库必填验证', async () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      wrapper.vm.form.host_id = '1'
      wrapper.vm.form.pxe_server_id = '1'
      wrapper.vm.form.kickstart_id = '1'
      wrapper.vm.form.repo_id = ''

      await wrapper.vm.handleSubmit()

      expect(wrapper.vm.errors.repo_id).toBe('请选择仓库')
    })
  })

  describe('近期任务显示', () => {
    it('无任务时显示暂无任务记录', async () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.empty-text').text()).toBe('暂无任务记录')
    })

    it('有任务时显示任务列表', async () => {
      const mockJobs = [
        {
          id: 1,
          job_type: 'osdeploy',
          target: '192.168.1.100',
          status: 'success',
          created_at: '2026-01-01T00:00:00Z'
        }
      ]

      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: mockJobs })

      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const jobItems = wrapper.findAll('.job-item')
      expect(jobItems.length).toBe(1)
    })
  })

  describe('工具方法', () => {
    it('formatDate 正确格式化日期', () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      const result = wrapper.vm.formatDate('2026-01-15T10:30:00Z')
      expect(result).toContain('2026')
    })

    it('formatDate 处理空值', () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      expect(wrapper.vm.formatDate('')).toBe('-')
      expect(wrapper.vm.formatDate(null)).toBe('-')
    })

    it('formatStatus 返回正确的中文状态', () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      expect(wrapper.vm.formatStatus('pending')).toBe('等待中')
      expect(wrapper.vm.formatStatus('running')).toBe('运行中')
      expect(wrapper.vm.formatStatus('success')).toBe('成功')
      expect(wrapper.vm.formatStatus('failed')).toBe('失败')
    })

    it('formatJobType 返回正确的中文类型', () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      expect(wrapper.vm.formatJobType('osdeploy')).toBe('OS部署')
      expect(wrapper.vm.formatJobType('hardware')).toBe('硬件采集')
    })

    it('getStatusClass 返回正确的样式类', () => {
      getHosts.mockResolvedValue({ results: [] })
      getPXEServers.mockResolvedValue({ results: [] })
      getKickstarts.mockResolvedValue({ results: [] })
      getRepos.mockResolvedValue({ results: [] })
      getJobs.mockResolvedValue({ results: [] })

      const wrapper = createWrapper()
      expect(wrapper.vm.getStatusClass('pending')).toBe('status-pending')
      expect(wrapper.vm.getStatusClass('running')).toBe('status-running')
      expect(wrapper.vm.getStatusClass('success')).toBe('status-success')
      expect(wrapper.vm.getStatusClass('failed')).toBe('status-failed')
    })
  })
})