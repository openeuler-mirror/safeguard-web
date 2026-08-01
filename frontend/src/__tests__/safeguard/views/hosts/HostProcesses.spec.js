import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HostProcesses from '@/views/hosts/HostProcesses.vue'
import { getHost } from '@/api/host'
import { getProcessesInfo, killProcess } from '@/api/safeguard/host-info'
import ProcessList from '@/components/safeguard/ProcessList.vue'

vi.mock('@/api/host')
vi.mock('@/api/safeguard/host-info')

const mockPush = vi.fn()
const mockAlert = vi.fn()
window.alert = mockAlert

describe('HostProcesses 页面测试', () => {
  const mockHostId = 1
  const mockHost = { id: 1, hostname: 'test-host' }
  const mockProcesses = [
    { pid: 1, name: 'systemd', cpu_percent: 0.5, mem_percent: 1.2 },
    { pid: 1234, name: 'nginx', cpu_percent: 2.5, mem_percent: 3.1 },
    { pid: 5678, name: 'node', cpu_percent: 10.5, mem_percent: 8.2 }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockReset()
    mockAlert.mockReset()

    getHost.mockResolvedValue(mockHost)
    getProcessesInfo.mockResolvedValue({ processes: mockProcesses })
    killProcess.mockResolvedValue({ success: true })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(HostProcesses, {
      global: {
        mocks: {
          $route: {
            params: { id: mockHostId }
          },
          $router: {
            push: mockPush
          }
        },
        stubs: {
          ProcessList
        }
      }
    })
  }

  describe('页面加载时显示 loading 状态', () => {
    it('初始应显示loading状态', async () => {
      wrapper = createWrapper()
      expect(wrapper.vm.loading).toBe(true)
    })

    it('数据加载完成后应停止loading', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('从路由参数获取 hostId', () => {
    it('应正确从路由参数获取hostId', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.hostId).toBe(mockHostId)
    })
  })

  describe('加载进程列表数据', () => {
    it('应调用getHost和getProcessesInfo API', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(getHost).toHaveBeenCalledWith(mockHostId)
      expect(getProcessesInfo).toHaveBeenCalledWith(mockHostId)
    })

    it('应正确设置processes数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      expect(wrapper.vm.processes).toEqual(mockProcesses)
    })
  })

})
